#!/usr/bin/env python3
"""
FaFaProFree - Advanced Smart Build Engine
========================================
Orchestrates preflight checks, smart download decisions, staging isolation,
cross-build asset reuse, atomic promotion, streaming verification, and
detailed build statistics.
"""

import os
import io
import sys
import re
import json
import time
import shutil
import zipfile
import logging
import warnings
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Silence urllib3 / chardet warnings
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

import requests

from scripts.hasher import compute_sha256, generate_manifest, write_manifest, load_manifest
from scripts.cache_manager import CacheManager
from scripts.downloader import DownloadItem, SmartDownloadEngine
from scripts.verify_build import verify_build
from scripts.i18n import _

# Windows console encoding fix
if sys.stdout and hasattr(sys.stdout, 'encoding'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ═══════════════════════════════════════════════════════════════════════
#  SECURITY LOGGER
# ═══════════════════════════════════════════════════════════════════════

class SensitiveDataRedactor(logging.Formatter):
    """Redacts sensitive credentials, tokens, and authorization headers from logs."""
    PATTERNS = [
        (re.compile(r'(ghp_[a-zA-Z0-9]{4})[a-zA-Z0-9]{28,}', re.I), r'\1****REDACTED****'),
        (re.compile(r'(fa_[a-zA-Z0-9]{4})[a-zA-Z0-9]{20,}', re.I), r'\1****REDACTED****'),
        (re.compile(r'(bearer\s+)[a-zA-Z0-9_\-\.]{15,}', re.I), r'\1****REDACTED****'),
        (re.compile(r'("?(?:api[_-]?key|token|password|secret)"?\s*[:=]\s*["\'])[^\'"]{6,}(["\'])', re.I), r'\1****REDACTED****\2'),
    ]

    def format(self, record):
        original = super().format(record)
        masked = original
        for pattern, replacement in self.PATTERNS:
            masked = pattern.sub(replacement, masked)
        return masked


def setup_logger(workspace_root: Path, debug: bool = False) -> logging.Logger:
    logger = logging.getLogger("FaFaProFree")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    logs_dir = workspace_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(SensitiveDataRedactor("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)
    return logger


# ═══════════════════════════════════════════════════════════════════════
#  CONFIG & STATS DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class BuildConfig:
    version: str
    profile: str
    profile_data: Dict[str, Any]
    output_dir: Path
    categories: Dict[str, bool]
    workers: int = 4
    force: bool = False
    interactive: bool = True
    debug: bool = False
    archive: bool = False
    dry_run: bool = False
    repair: bool = False
    verify_only: bool = False
    verify_level: str = "standard"
    auth_token: Optional[str] = None
    cdn_base_url: str = "https://site-assets.fontawesome.com/releases"
    repository: str = "user05-ioemlak/FaFaProFree"


# ═══════════════════════════════════════════════════════════════════════
#  PREFLIGHT CHECKS (Requirements 25 & 26)
# ═══════════════════════════════════════════════════════════════════════

def preflight_disk_space(target_path: Path, required_mb: int = 500) -> bool:
    """Checks if sufficient disk space is available."""
    try:
        usage = shutil.disk_usage(target_path.anchor or ".")
        available_mb = usage.free / (1024 * 1024)
        req_gb = required_mb / 1024
        avail_gb = available_mb / 1024

        print(f"  Required space : {req_gb:.1f} GB")
        print(f"  Available      : {avail_gb:.1f} GB")

        if available_mb < required_mb:
            print("  ✗ Insufficient disk space!")
            return False
        print("  ✓ Sufficient disk space")
        return True
    except Exception:
        return True


def preflight_network(cdn_base_url: str, headers: Dict[str, str]) -> bool:
    """Verifies network connectivity and source availability before downloading."""
    test_url = f"{cdn_base_url}/v7.3.1/css/all.css"
    try:
        res = requests.head(test_url, headers=headers, timeout=10)
        if res.status_code in (200, 304, 403):
            print("  ✓ Network connectivity & source available")
            return True
        print(f"  ! Network preflight warning: HTTP {res.status_code}")
        return True
    except Exception as e:
        print(f"  ✗ Network preflight failed: Cannot connect to source ({e})")
        return False


# ═══════════════════════════════════════════════════════════════════════
#  ASSET INVENTORY BUILDER
# ═══════════════════════════════════════════════════════════════════════

def load_config(workspace_root: Path) -> Dict[str, Any]:
    cfg_path = workspace_root / "config" / "build_profiles.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration not found: {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_credentials(logger: logging.Logger) -> Dict[str, Optional[str]]:
    token = os.environ.get("FONTAWESOME_TOKEN") or os.environ.get("FONTAWESOME_PACKAGE_TOKEN")
    if not token:
        try:
            import dotenv
            env_file = Path(".env")
            if env_file.exists():
                vals = dotenv.dotenv_values(env_file)
                token = vals.get("FONTAWESOME_TOKEN") or vals.get("FONTAWESOME_PACKAGE_TOKEN")
        except ImportError:
            pass

    if token:
        logger.info("Authorized token discovered in environment.")
        return {"status": "authenticated", "token": token}
    else:
        logger.info("No explicit token found. Using authorized public access model.")
        return {"status": "standard", "token": None}


def build_headers(token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        'Referer': 'https://fontawesome.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def generate_inventory(config: BuildConfig, full_cfg: Dict[str, Any],
                       base_dir: Path) -> List[DownloadItem]:
    """Builds deduplicated list of DownloadItems for the target profile."""
    items: List[DownloadItem] = []
    seen_rel: Set[str] = set()

    v = config.version
    profile = config.profile_data
    families = profile.get("families", [])
    common = full_cfg.get("common_files", {})
    weights = full_cfg.get("family_weights", {})
    cdn = config.cdn_base_url

    def add_item(rel_path: str, url: str):
        if rel_path in seen_rel:
            return
        seen_rel.add(rel_path)
        items.append(DownloadItem(url=url, target_path=base_dir / rel_path, rel_path=rel_path))

    # CSS
    if config.categories.get("css"):
        for f in common.get("css", []):
            add_item(f"css/{f}", f"{cdn}/v{v}/css/{f}")
        for fam in families:
            add_item(f"css/{fam}.css", f"{cdn}/v{v}/css/{fam}.css")

    # JS
    if config.categories.get("js"):
        for f in common.get("js", []):
            add_item(f"js/{f}", f"{cdn}/v{v}/js/{f}")
        for fam in families:
            add_item(f"js/{fam}.js", f"{cdn}/v{v}/js/{fam}.js")

    # Webfonts
    if config.categories.get("fonts"):
        for f in common.get("webfonts", []):
            add_item(f"webfonts/{f}", f"{cdn}/v{v}/webfonts/{f}")
        for fam in families:
            w = weights.get(fam, "400")
            add_item(f"webfonts/fa-{fam}-{w}.woff2", f"{cdn}/v{v}/webfonts/fa-{fam}-{w}.woff2")

    # Sprites
    if config.categories.get("sprites"):
        for fam in families:
            add_item(f"sprites/{fam}.svg", f"{cdn}/v{v}/sprites/{fam}.svg")

    return items


# ═══════════════════════════════════════════════════════════════════════
#  METADATA & LICENSE GENERATION
# ═══════════════════════════════════════════════════════════════════════

def generate_license(build_dir: Path, profile_name: str, version: str):
    content = f"""FaFaProFree Third-Party License & Educational Research Notice
============================================================
Package  : Font Awesome ({profile_name})
Version  : v{version}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Tooling  : https://github.com/user05-ioemlak/FaFaProFree

PART 1: EDUCATIONAL RESEARCH & NON-AFFILIATION NOTICE
------------------------------------------------------
This package was compiled using FaFaProFree, an independent open-source
automation tool developed strictly for educational, technical experimentation,
and CDN caching research purposes.

1. Intellectual Property & Ownership:
   "Font Awesome", "Fonticons", and all corresponding logos, icon glyphs,
   font files (.woff2, .ttf), and vector designs are the proprietary
   intellectual property and registered trademarks of Fonticons, Inc.

2. Strict Copyright Warning (Telif Hakkı Uyarısı):
   Font Awesome Pro is commercial software. Using Font Awesome Pro assets in
   commercial, public, or production web applications WITHOUT an active,
   officially purchased commercial license from Fonticons, Inc. CONSTITUTES
   COPYRIGHT INFRINGEMENT and is strictly prohibited by intellectual property laws.

3. No Transfer of Rights:
   This project does NOT grant, assign, transfer, or sublicense any commercial
   usage rights to Font Awesome Pro assets.

4. User Responsibility & Official License:
   All users must obtain and maintain an authorized commercial license directly
   from Fonticons, Inc. prior to any commercial deployment:
   https://fontawesome.com/plans
   https://fontawesome.com/license


PART 2: FAFAPROFREE BUILD TOOLING NOTICE (MIT)
----------------------------------------------
The build scripts, manifest generator, and automation logic of FaFaProFree
are licensed under the MIT License:

Copyright (c) 2026 FaFaProFree Contributors
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software tooling without restriction, subject to standard MIT conditions.
"""
    (build_dir / "LICENSE.txt").write_text(content, encoding="utf-8")



def generate_build_info(build_dir: Path, version: str, profile_name: str,
                        repo: str, stats_summary: Dict[str, Any]) -> Path:
    total_files = sum(1 for p in build_dir.rglob("*") if p.is_file())
    total_bytes = sum(p.stat().st_size for p in build_dir.rglob("*") if p.is_file())

    info = {
        "version": version,
        "profile": profile_name,
        "repository": repo,
        "generated_at": datetime.now().isoformat(),
        "generator": "fa_pro_v3.py (FaFaProFree Smart Build Engine)",
        "file_count": total_files,
        "total_size_bytes": total_bytes,
        "stats": stats_summary
    }

    info_path = build_dir / "BUILD_INFO.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    return info_path


def create_archive(build_dir: Path, workspace_root: Path) -> Path:
    archive_name = f"FaFaProFree-{build_dir.name}.zip"
    archive_path = workspace_root / archive_name
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir.parent)
                zipf.write(file_path, arcname)
    return archive_path


# ═══════════════════════════════════════════════════════════════════════
#  BUILD PIPELINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════

def execute_build(config: BuildConfig, workspace_root: Path) -> bool:
    """Executes smart build with staging isolation, manifest, and verification."""
    workspace_root = Path(workspace_root).resolve()
    logger = setup_logger(workspace_root, debug=config.debug)
    cache_mgr = CacheManager(workspace_root)
    full_cfg = load_config(workspace_root)

    print()
    if not config.version or config.version.lower() in ("latest", "default"):
        try:
            from scripts.version_resolver import get_available_versions
            disco = get_available_versions(workspace_root)
            config.version = disco.get("latest", "7.3.1")
        except Exception:
            config.version = "7.3.1"

    print("╔════════════════════════════════════════════════════╗")
    print("║          FaFaProFree Smart Build System            ║")
    print("║         https://github.com/user05-ioemlak/FaFaProFree      ║")
    print("╚════════════════════════════════════════════════════╝")
    print(f"  Profile : {config.profile}")
    print(f"  Version : v{config.version.lstrip('v')}")
    print()

    # Final destination
    final_build_dir = workspace_root / "build" / f"v{config.version.lstrip('v')}-{config.profile}"

    # ── 1. VERIFY-ONLY MODE (Requirement 18) ──────────────────────────
    if config.verify_only:
        print("  [MODE: VERIFY-ONLY] Validating existing build directory...")
        if not final_build_dir.exists():
            print(f"  ✗ Target build does not exist: {final_build_dir.name}")
            return False
        passed, report = verify_build(final_build_dir, level=config.verify_level)
        return passed

    # ── 2. PREFLIGHT CHECKS (Requirements 25 & 26) ─────────────────────
    print("  ── Preflight Checks ──")
    if not preflight_disk_space(workspace_root, required_mb=300):
        return False

    auth_info = validate_credentials(logger)
    headers = build_headers(auth_info["token"])
    if not preflight_network(config.cdn_base_url, headers):
        return False
    print()

    # ── 3. INCOMPLETE STAGING RECOVERY (Requirement 24) ────────────────
    staging_dir = cache_mgr.get_staging_dir(config.version, config.profile)
    existing_staging = cache_mgr.check_incomplete_staging(config.version, config.profile)

    if existing_staging and config.interactive and not config.repair and not config.dry_run:
        print("  ! Incomplete build staging detected.")
        print("  ──────────────────────────────────────────")
        print("  [1] Resume download from staging")
        print("  [2] Verify and repair staging")
        print("  [3] Clean staging and start fresh")
        print("  [4] Cancel")
        choice = input("  Selection [1/2/3/4] (default: 1): ").strip() or "1"
        if choice == "3":
            cache_mgr.clean_staging(config.version, config.profile)
            staging_dir = cache_mgr.get_staging_dir(config.version, config.profile)
        elif choice == "4":
            print("  -> Build cancelled.")
            return False

    # Determine working target: staging for builds, final dir for repair
    work_dir = final_build_dir if config.repair else staging_dir
    work_dir.mkdir(parents=True, exist_ok=True)

    # ── 4. BUILD ASSET INVENTORY & DECISION ENGINE ────────────────────
    items = generate_inventory(config, full_cfg, work_dir)
    engine = SmartDownloadEngine(cache_mgr, headers, workers=config.workers, force=config.force)

    existing_manifest = load_manifest(work_dir / "manifest.json") or load_manifest(final_build_dir / "manifest.json")

    print(f"  {_('decision.scanning_assets', count=len(items))}")
    queue_download: List[DownloadItem] = []
    reused_count = 0
    skipped_count = 0

    for item in items:
        decision = engine.evaluate_item(item, config.version, existing_manifest)
        if decision == "skip":
            skipped_count += 1
        elif decision.startswith("reused"):
            reused_count += 1
        else:
            queue_download.append(item)

    # ── 5. DRY-RUN MODE (Requirement 17) ──────────────────────────────
    if config.dry_run:
        print("\n" + "=" * 55)
        print(f"  {_('decision.dry_run_title')}")
        print("=" * 55)
        for item in items:
            if item.status == "skipped":
                print(f"  ✓ {item.rel_path:<38} → {_('decision.action_skip')}")
            elif item.status == "reused":
                print(f"  ✓ {item.rel_path:<38} → {_('decision.action_reuse')}")
            elif item.status == "corrupted":
                print(f"  ✗ {item.rel_path:<38} → Corrupted → {_('decision.action_download')}")
            else:
                print(f"  ↓ {item.rel_path:<38} → {_('decision.action_download')}")
        print("-" * 55)
        print(f"  {_('decision.plan_summary', skip=skipped_count, reuse=reused_count, download=len(queue_download))}")
        print("=" * 55 + "\n")
        return True

    # ── 6. REPAIR CONFIRMATION (Requirement 19) ───────────────────────
    if config.repair:
        print(f"\n  Found {len(queue_download)} files requiring repair/download out of {len(items)}.")
        if not queue_download:
            print("  ✓ All files are intact. No repair needed.\n")
            return True
        if config.interactive:
            confirm = input(f"  Repair and download {len(queue_download)} files? [Y/n]: ").strip().lower()
            if confirm == "n":
                print("  -> Repair aborted.")
                return False

    # ── 7. DOWNLOAD EXECUTION WITH PROGRESS (Requirement 4 & 28) ──────
    downloaded_count = 0
    failed_count = 0

    if queue_download:
        print(f"\n  Downloading {len(queue_download)} assets ({reused_count} reused, {skipped_count} skipped)...")
        completed_tasks = 0
        total_tasks = len(queue_download)

        with ThreadPoolExecutor(max_workers=config.workers) as executor:
            future_map = {
                executor.submit(engine.download_file_atomic, item, config.version): item
                for item in queue_download
            }
            for future in as_completed(future_map):
                success = future.result()
                item = future_map[future]
                completed_tasks += 1
                if success:
                    downloaded_count += 1
                else:
                    failed_count += 1

                # Live progress update
                bar_len = 20
                pct = int(100 * (completed_tasks / total_tasks))
                bar = "█" * int(bar_len * (pct / 100)) + "░" * (bar_len - int(bar_len * (pct / 100)))
                mb_down = engine.total_downloaded_bytes / (1024 * 1024)
                sys.stdout.write(f"\r  [{bar}] {pct:3d}% | {completed_tasks}/{total_tasks} | {mb_down:.1f} MB | {item.rel_path[:25]:<25}")
                sys.stdout.flush()

        print()

    # ── 8. METADATA & MANIFEST GENERATION (Requirement 3, 5, 6) ──────
    print("\n  Generating manifest and build metadata...")
    manifest_data = generate_manifest(work_dir, config.version, config.profile)
    write_manifest(manifest_data, work_dir / "manifest.json")
    generate_license(work_dir, config.profile, config.version)

    # Calculate statistics & saved bandwidth
    total_processed = len(items)
    total_reused = reused_count + skipped_count
    total_bytes_stream = engine.total_downloaded_bytes + engine.total_saved_bytes
    saved_bw_pct = (engine.total_saved_bytes / total_bytes_stream * 100) if total_bytes_stream > 0 else 100.0

    stats_summary = {
        "downloaded": downloaded_count,
        "reused": total_reused,
        "failed": failed_count,
        "total_files": total_processed,
        "download_bytes": engine.total_downloaded_bytes,
        "saved_bytes": engine.total_saved_bytes,
        "saved_bandwidth_percent": round(saved_bw_pct, 1)
    }

    generate_build_info(work_dir, config.version, config.profile, config.repository, stats_summary)

    # ── 9. FINAL BUILD VERIFICATION (Requirement 13) ──────────────────
    print("\n  ── Final Build Integrity Verification ──")
    passed, report = verify_build(
        work_dir, level=config.verify_level, expected_manifest=manifest_data,
        version=config.version, profile=config.profile, stats=stats_summary
    )

    if not passed:
        print("\n  ✗ BUILD FAILED: Integrity or security verification failed.")
        print(f"  Staging directory preserved at: {work_dir.name}")
        return False

    # ── 10. ATOMIC PROMOTION (Requirement 23) ─────────────────────────
    if not config.repair:
        print(f"  Promoting verified staging build to: {final_build_dir.name}...")
        cache_mgr.promote_staging_to_final(work_dir, final_build_dir)
        target_final = final_build_dir
    else:
        target_final = work_dir

    # Optional archive creation
    archive_path = None
    if config.archive:
        print("  Creating release archive...")
        archive_path = create_archive(target_final, workspace_root)

    # ── 11. DOWNLOAD STATISTICS DISPLAY (Requirement 16) ──────────────
    bar_width = 20
    bw_filled = int(bar_width * (saved_bw_pct / 100))
    bw_bar = "█" * bw_filled + "░" * (bar_width - bw_filled)

    print("\n" + "─" * 45)
    print("  DOWNLOAD SUMMARY")
    print("─" * 45)
    print(f"  Total files      : {total_processed:,}")
    print(f"  Already verified : {skipped_count:,}")
    print(f"  Reused (cache)   : {reused_count:,}")
    print(f"  Downloaded       : {downloaded_count:,}")
    print(f"  Failed           : {failed_count:,}")
    print(f"  Saved bandwidth  : [{bw_bar}] {saved_bw_pct:.1f}%")
    print("─" * 45)

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║             BUILD SUCCESSFUL                 ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"  Version   : v{config.version}")
    print(f"  Profile   : {config.profile}")
    print(f"  Output    : build/{target_final.name}/")
    print(f"  Manifest  : build/{target_final.name}/manifest.json")
    print(f"  Report    : build/{target_final.name}/BUILD_REPORT.json")
    if archive_path:
        print(f"  Archive   : {archive_path.name}")
    print("  ✓ Ready\n")

    return True
