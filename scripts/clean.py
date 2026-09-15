#!/usr/bin/env python3
"""
FaFaProFree - Safe Clean Utility
================================
Safely cleans build artifacts, logs, and temporary caches without
ever touching project source files, configuration, or workflows.
"""

import sys
import io
import shutil
import argparse
from pathlib import Path

# Ensure project root is in sys.path for direct execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# Windows console encoding fix (cp1254 -> utf-8)
if sys.stdout and hasattr(sys.stdout, 'encoding'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Paths that must NEVER be deleted
PROTECTED_PATHS = {
    "fa_pro_v3.py",
    "main.py",
    "pyproject.toml",
    "README.md",
    "README.tr.md",
    "README.ru.md",
    "README.de.md",
    "LICENSE",
    "LICENSE.txt",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "requirements.txt",
    ".gitignore",
    "config",
    "scripts",
    "assets",
    "lang",
    "tests",
    ".github",
    ".git",
}


def safe_clean(workspace_root: Path, clean_logs: bool = False, clean_cache: bool = False, dry_run: bool = False) -> int:
    """
    Cleans build/ and generated artifacts safely.
    
    Args:
        workspace_root: Project root directory
        clean_logs: If True, also clears logs/ (preserves .gitkeep)
        clean_cache: If True, also clears .cache/
        dry_run: If True, only prints what would be deleted
        
    Returns:
        Number of items cleaned
    """
    workspace_root = workspace_root.resolve()
    cleaned_count = 0
    
    print("=" * 60)
    print("  FaFaProFree - Safe Clean Utility")
    print("=" * 60)
    if dry_run:
        print("  [DRY-RUN MODE] No files will be permanently deleted.")
        print("-" * 60)
        
    # 1. Clean build directory contents
    build_dir = workspace_root / "build"
    if build_dir.exists() and build_dir.is_dir():
        for item in build_dir.iterdir():
            if item.name in PROTECTED_PATHS:
                print(f"  [SKIPPED PROTECTED] {item.name}")
                continue
            print(f"  -> Cleaning build target: {item.name}")
            cleaned_count += 1
            if not dry_run:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
                    
    # 2. Clean generated zip archives in root
    for archive in workspace_root.glob("FaFaProFree-*.zip"):
        print(f"  -> Cleaning archive: {archive.name}")
        cleaned_count += 1
        if not dry_run:
            archive.unlink(missing_ok=True)
            
    # 3. Clean temporary test directories
    for temp_dir in workspace_root.glob("test_*"):
        if temp_dir.is_dir():
            print(f"  -> Cleaning temp directory: {temp_dir.name}")
            cleaned_count += 1
            if not dry_run:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
    for temp_dir in workspace_root.glob("temp_*"):
        if temp_dir.is_dir():
            print(f"  -> Cleaning temp directory: {temp_dir.name}")
            cleaned_count += 1
            if not dry_run:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
    # 4. Clean python caches
    for pycache in workspace_root.rglob("__pycache__"):
        if pycache.is_dir():
            print(f"  -> Cleaning cache: {pycache.relative_to(workspace_root)}")
            cleaned_count += 1
            if not dry_run:
                shutil.rmtree(pycache, ignore_errors=True)
                
    # 5. Clean staging and backups
    staging_dir = workspace_root / "build" / ".staging"
    if staging_dir.exists():
        print(f"  -> Cleaning staging: {staging_dir.name}")
        cleaned_count += 1
        if not dry_run:
            shutil.rmtree(staging_dir, ignore_errors=True)

    backup_dir = workspace_root / ".backup"
    if backup_dir.exists():
        print(f"  -> Cleaning backups: {backup_dir.name}")
        cleaned_count += 1
        if not dry_run:
            shutil.rmtree(backup_dir, ignore_errors=True)

    # 6. Clean local cache if requested
    if clean_cache:
        cache_dir = workspace_root / ".cache"
        if cache_dir.exists():
            print(f"  -> Cleaning cache: {cache_dir.name}")
            cleaned_count += 1
            if not dry_run:
                shutil.rmtree(cache_dir, ignore_errors=True)

    # 7. Clean logs if requested
    if clean_logs:
        logs_dir = workspace_root / "logs"
        if logs_dir.exists() and logs_dir.is_dir():
            for log_file in logs_dir.glob("*.log*"):
                print(f"  -> Cleaning log: {log_file.name}")
                cleaned_count += 1
                if not dry_run:
                    log_file.unlink(missing_ok=True)
            if not dry_run:
                (logs_dir / ".gitkeep").touch(exist_ok=True)


    print("-" * 60)
    print(f"  Clean completed. Total items cleaned: {cleaned_count}")
    print("=" * 60)
    return cleaned_count


def main():
    parser = argparse.ArgumentParser(description="Safely clean FaFaProFree build targets and artifacts.")
    parser.add_argument("--logs", action="store_true", help="Also delete files in logs/ directory")
    parser.add_argument("--cache", action="store_true", help="Also delete .cache/ directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without deleting")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    safe_clean(root, clean_logs=args.logs, clean_cache=args.cache, dry_run=args.dry_run)



if __name__ == "__main__":
    main()
