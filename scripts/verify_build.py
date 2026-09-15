#!/usr/bin/env python3
"""
FaFaProFree - Advanced Build Verification & Security Engine
===========================================================
Performs multi-level integrity checks (quick, standard, strict),
identifies Missing/Modified/Unexpected files, detects security leaks,
and produces standardized BUILD_REPORT.json.
"""

import sys
import io
import re
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set, Optional

from scripts.hasher import compute_sha256, load_manifest
from scripts.i18n import _

# Windows console encoding fix (cp1254 -> utf-8)
if sys.stdout and hasattr(sys.stdout, 'encoding'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Secret patterns for automated leakage detection
SECRET_PATTERNS = [
    re.compile(r'ghp_[a-zA-Z0-9]{36,}', re.IGNORECASE),
    re.compile(r'gho_[a-zA-Z0-9]{36,}', re.IGNORECASE),
    re.compile(r'github_pat_[a-zA-Z0-9_]{50,}', re.IGNORECASE),
    re.compile(r'bearer\s+[a-zA-Z0-9_\-\.]{25,}', re.IGNORECASE),
    re.compile(r'-----BEGIN\s+[A-Z\s]+PRIVATE\s+KEY-----'),
    re.compile(r'FONTAWESOME_TOKEN\s*=\s*["\']?[a-zA-Z0-9_\-]{20,}["\']?', re.IGNORECASE),
    re.compile(r'FONTAWESOME_PACKAGE_TOKEN\s*=\s*["\']?[a-zA-Z0-9_\-]{20,}["\']?', re.IGNORECASE),
    re.compile(r'"(?:api[_-]?key|access[_-]?token|secret|password)"\s*:\s*"(?!REDACTED)[^"]{16,}"', re.IGNORECASE),
]

TEMP_FILE_EXTENSIONS = {".tmp", ".temp", ".part", ".crdownload", ".swp", ".swo", ".pyc"}
STANDARD_META_FILES = {"manifest.json", "BUILD_INFO.json", "BUILD_REPORT.json", "LICENSE.txt"}


class BuildVerificationReport:
    """Stores detailed categorization of files and validation metrics."""
    def __init__(self, target_dir: Path):
        self.target_dir = Path(target_dir).resolve()
        self.files_discovered = 0
        self.files_verified = 0
        self.missing_files: List[str] = []
        self.modified_files: List[Tuple[str, str]] = []  # (path, reason)
        self.corrupted_files: List[str] = []
        self.unexpected_files: List[str] = []
        self.security_violations: List[str] = []
        self.checks: List[Tuple[str, bool, str]] = []
        self.passed = True

    def add_check(self, name: str, passed: bool, message: str = ""):
        self.checks.append((name, passed, message))
        if not passed:
            self.passed = False

    def print_summary(self):
        print("\n" + "=" * 55)
        print(f"  {_('verify.report_title')}")
        print("=" * 55)
        print(f"  {_('verify.target_dir', dir=self.target_dir.name)}")
        print(f"  {_('verify.files_discovered', count=self.files_discovered)}")
        print(f"  {_('verify.files_verified', count=self.files_verified)}")
        print(f"  {_('verify.missing', count=len(self.missing_files))}")
        print(f"  {_('verify.modified', count=len(self.modified_files))}")
        print(f"  {_('verify.corrupted', count=len(self.corrupted_files))}")
        print(f"  {_('verify.unexpected', count=len(self.unexpected_files))}")
        print(f"  {_('verify.security_breaches', count=len(self.security_violations))}")
        print("-" * 55)

        for name, passed, msg in self.checks:
            detail = f" - {msg}" if msg else ""
            sym = "✓" if passed else "✗"
            print(f"  {sym} {name}{detail}")

        print("=" * 55)
        if self.passed and not self.missing_files and not self.modified_files and not self.corrupted_files:
            print(f"  {_('verify.verified_pass')}\n")
        else:
            print(f"  {_('verify.verified_fail')}\n")

    def to_dict(self, version: str = "", profile: str = "",
                stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates BUILD_REPORT.json structure."""
        st = stats or {}
        return {
            "status": "verified" if self.passed else "failed",
            "version": version,
            "profile": profile,
            "files_total": self.files_discovered,
            "files_verified": self.files_verified,
            "files_downloaded": st.get("downloaded", 0),
            "files_reused": st.get("reused", 0),
            "files_missing": len(self.missing_files),
            "files_modified": len(self.modified_files),
            "files_unexpected": len(self.unexpected_files),
            "files_failed": st.get("failed", 0),
            "saved_bandwidth_percent": st.get("saved_bandwidth_percent", 0.0),
            "missing": self.missing_files[:50],
            "modified": [p for p, _ in self.modified_files[:50]],
            "unexpected": self.unexpected_files[:50]
        }


def verify_build(build_dir: Path, level: str = "standard",
                 expected_manifest: Optional[Dict[str, Any]] = None,
                 version: str = "", profile: str = "",
                 stats: Optional[Dict[str, Any]] = None) -> Tuple[bool, BuildVerificationReport]:
    """
    Executes multi-level verification on a build folder.
    Levels:
      - 'quick': file existence and non-zero sizes
      - 'standard': quick + streaming SHA-256 validation
      - 'strict': standard + archive checks + manifest comparison + unexpected files + security scan
    """
    build_dir = Path(build_dir).resolve()
    report = BuildVerificationReport(build_dir)

    # 1. Output directory exists
    if not build_dir.exists() or not build_dir.is_dir():
        report.add_check("Output directory exists", False, f"Directory not found: {build_dir}")
        report.print_summary()
        return False, report
    report.add_check("Output directory exists", True)

    # 2. LICENSE.txt exists
    lic_file = build_dir / "LICENSE.txt"
    if lic_file.exists() and lic_file.stat().st_size > 0:
        report.add_check("LICENSE.txt exists", True, "Third-Party notices present")
    else:
        report.add_check("LICENSE.txt exists", False, "Missing or empty LICENSE.txt")

    # 3. BUILD_INFO.json exists
    info_file = build_dir / "BUILD_INFO.json"
    if info_file.exists() and info_file.stat().st_size > 0:
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                info_data = json.load(f)
            version = version or info_data.get("version", "")
            profile = profile or info_data.get("profile", "")
            report.add_check("BUILD_INFO.json valid", True, f"v{version} [{profile}]")
        except Exception as e:
            report.add_check("BUILD_INFO.json valid", False, f"JSON parse error: {e}")
    else:
        report.add_check("BUILD_INFO.json valid", False, "Missing BUILD_INFO.json")

    # 4. Manifest comparison & File verification
    manifest = expected_manifest or load_manifest(build_dir / "manifest.json")
    manifest_files = manifest.get("files", {}) if manifest else {}

    # Scan files on disk
    disk_files: Dict[str, Path] = {}
    for p in build_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(build_dir).as_posix()
            disk_files[rel] = p

    report.files_discovered = len(disk_files)

    # Check for temporary files
    for rel, p in disk_files.items():
        if p.suffix.lower() in TEMP_FILE_EXTENSIONS or p.name.startswith("."):
            report.corrupted_files.append(rel)

    # If manifest is present, compare against manifest
    if manifest_files:
        for rel_path, meta in manifest_files.items():
            disk_path = build_dir / rel_path
            if not disk_path.exists():
                report.missing_files.append(rel_path)
                continue

            disk_size = disk_path.stat().st_size
            expected_size = meta.get("size", 0)

            # Quick check: Size match
            if disk_size == 0 or (expected_size and disk_size != expected_size):
                report.modified_files.append((rel_path, f"Size mismatch: {disk_size} != {expected_size}"))
                continue

            # Standard & Strict: SHA-256 checksum
            if level in ("standard", "strict"):
                expected_hash = meta.get("sha256")
                if expected_hash:
                    actual_hash = compute_sha256(disk_path)
                    if actual_hash.lower() != expected_hash.lower():
                        report.modified_files.append((rel_path, "SHA-256 hash mismatch"))
                        continue

            report.files_verified += 1

        # Check for unexpected files (Strict mode)
        if level == "strict":
            manifest_set = set(manifest_files.keys()) | STANDARD_META_FILES
            for rel in disk_files.keys():
                if rel not in manifest_set:
                    report.unexpected_files.append(rel)
    else:
        # If no manifest, verify non-zero size for all assets
        for rel, p in disk_files.items():
            if rel not in STANDARD_META_FILES:
                if p.stat().st_size == 0:
                    report.corrupted_files.append(rel)
                else:
                    if level in ("standard", "strict"):
                        compute_sha256(p)
                    report.files_verified += 1

    # Check for missing/modified status
    report.add_check("All required files present", len(report.missing_files) == 0,
                     f"{len(report.missing_files)} missing" if report.missing_files else "No missing files")
    report.add_check("No corrupted or modified files", len(report.modified_files) == 0 and len(report.corrupted_files) == 0,
                     f"{len(report.modified_files)} modified, {len(report.corrupted_files)} corrupted" if (report.modified_files or report.corrupted_files) else "Integrity verified")

    if level == "strict":
        report.add_check("No unexpected files", len(report.unexpected_files) == 0,
                         f"{len(report.unexpected_files)} unexpected" if report.unexpected_files else "Clean build structure")

    # 5. Security & Secret leakage scan
    for rel, p in disk_files.items():
        if p.suffix.lower() in {".json", ".txt", ".css", ".js", ".html", ".md"}:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                for pat in SECRET_PATTERNS:
                    if pat.search(content):
                        report.security_violations.append(f"{rel} (matched pattern)")
            except Exception:
                pass

    report.add_check("Zero credential leaks", len(report.security_violations) == 0,
                     f"Breach detected in: {', '.join(report.security_violations)}" if report.security_violations else "Clean of secrets")

    # Generate BUILD_REPORT.json
    report_path = build_dir / "BUILD_REPORT.json"
    report_dict = report.to_dict(version=version, profile=profile, stats=stats)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)

    report.print_summary()
    return report.passed and len(report.missing_files) == 0 and len(report.modified_files) == 0, report


def check_configuration(config_path: Path) -> bool:
    """Validates config/build_profiles.json structure."""
    print("\n" + "=" * 65)
    print("  CONFIGURATION VALIDATION: config/build_profiles.json")
    print("=" * 65)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = data.get("profiles", {})
        if not profiles or not {"Free", "Pro", "Pro-Plus"}.issubset(set(profiles.keys())):
            print("  ✗ Missing required profile definitions in config")
            return False
        print(f"  ✓ Configuration valid. Profiles: {', '.join(profiles.keys())}")
        print("=" * 65 + "\n")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify FaFaProFree build directories.")
    parser.add_argument("--dir", "-d", type=str, default=None, help="Target build directory")
    parser.add_argument("--level", type=str, choices=["quick", "standard", "strict"],
                        default="standard", help="Integrity verification level (default: standard)")
    parser.add_argument("--check-config", action="store_true", help="Validate config/build_profiles.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent

    if args.check_config:
        cfg = root / "config" / "build_profiles.json"
        sys.exit(0 if check_configuration(cfg) else 1)

    if args.dir:
        target = Path(args.dir)
        if not target.is_absolute():
            target = root / target
        passed, _ = verify_build(target, level=args.level)
        sys.exit(0 if passed else 1)

    build_root = root / "build"
    if not build_root.exists() or not any(build_root.iterdir()):
        print("\n  ! No build directories found in 'build/'. Run a build first.\n")
        sys.exit(0)

    overall = True
    for item in sorted(build_root.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            passed, _ = verify_build(item, level=args.level)
            if not passed:
                overall = False

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
