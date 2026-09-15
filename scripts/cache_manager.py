#!/usr/bin/env python3
"""
FaFaProFree - Cache Manager & Cross-Build Asset Reuse Engine
============================================================
Handles local caching, cross-build deduplication, staging directory
isolation, and atomic build promotion.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Ensure project root is in sys.path for direct execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.hasher import compute_sha256, load_manifest


class CacheManager:
    """Manages .cache/, cross-build reuse, and atomic staging workflows."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root).resolve()
        self.cache_dir = self.workspace_root / ".cache" / "assets"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.staging_root = self.workspace_root / "build" / ".staging"
        self.backup_root = self.workspace_root / ".backup"

    # ── Local Cache ───────────────────────────────────────────────────

    def get_cached_asset(self, version: str, rel_path: str) -> Optional[Path]:
        """
        Retrieves a verified cached file if it exists and has non-zero size.
        Path: .cache/assets/v<version>/<rel_path>
        """
        cached_file = self.cache_dir / f"v{version}" / rel_path
        if cached_file.exists() and cached_file.is_file() and cached_file.stat().st_size > 0:
            return cached_file
        return None

    def store_cached_asset(self, version: str, rel_path: str, source_path: Path):
        """Stores a newly verified asset in the cache."""
        target = self.cache_dir / f"v{version}" / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source_path, target)
        except Exception:
            pass

    # ── Cross-Build Reuse (Requirement 10) ────────────────────────────

    def find_cross_build_asset(self, version: str, rel_path: str,
                               exclude_dir: Optional[Path] = None) -> Optional[Tuple[Path, str]]:
        """
        Scans other existing builds in build/ for identical verified assets.
        Returns (source_path, source_build_name) if found and verified.
        """
        builds_root = self.workspace_root / "build"
        if not builds_root.exists():
            return None

        # Look across all build directories
        for build_folder in builds_root.iterdir():
            if not build_folder.is_dir() or build_folder.name.startswith("."):
                continue
            if exclude_dir and build_folder.resolve() == exclude_dir.resolve():
                continue

            # Check if directory name matches the target version
            if f"v{version}-" in build_folder.name or build_folder.name.startswith(f"v{version}"):
                candidate = build_folder / rel_path
                if candidate.exists() and candidate.is_file() and candidate.stat().st_size > 0:
                    return candidate, build_folder.name

        return None

    # ── Staging Management (Requirement 23 & 24) ──────────────────────

    def get_staging_dir(self, version: str, profile: str) -> Path:
        """Returns isolated staging path: build/.staging/v<version>-<profile>/"""
        dir_name = f"v{version.lstrip('v')}-{profile}"
        staging_path = self.staging_root / dir_name
        staging_path.mkdir(parents=True, exist_ok=True)
        return staging_path

    def check_incomplete_staging(self, version: str, profile: str) -> Optional[Path]:
        """Checks if a previously incomplete staging build exists."""
        dir_name = f"v{version.lstrip('v')}-{profile}"
        staging_path = self.staging_root / dir_name
        if staging_path.exists() and any(staging_path.iterdir()):
            return staging_path
        return None

    def clean_staging(self, version: str, profile: str):
        """Removes staging directory after atomic promotion or cancellation."""
        dir_name = f"v{version.lstrip('v')}-{profile}"
        staging_path = self.staging_root / dir_name
        if staging_path.exists():
            shutil.rmtree(staging_path, ignore_errors=True)

    def promote_staging_to_final(self, staging_dir: Path, final_dir: Path) -> bool:
        """
        Atomically/safely moves staging directory to the final build directory.
        If final_dir exists, backs it up first.
        """
        staging_dir = Path(staging_dir).resolve()
        final_dir = Path(final_dir).resolve()

        final_dir.parent.mkdir(parents=True, exist_ok=True)

        # If final_dir exists, move it to backup temporarily
        backup_dir = None
        if final_dir.exists():
            self.backup_root.mkdir(parents=True, exist_ok=True)
            backup_dir = self.backup_root / f"{final_dir.name}_prev"
            if backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)
            try:
                shutil.move(str(final_dir), str(backup_dir))
            except Exception:
                shutil.rmtree(str(final_dir), ignore_errors=True)

        try:
            shutil.move(str(staging_dir), str(final_dir))
            # Clean up backup if promotion succeeded
            if backup_dir and backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)
            return True
        except Exception as e:
            # Rollback if move failed
            if backup_dir and backup_dir.exists() and not final_dir.exists():
                shutil.move(str(backup_dir), str(final_dir))
            raise RuntimeError(f"Failed to promote staging to final build directory: {e}")

    # ── Safe Deletion / Backup (Requirement 22) ───────────────────────

    def safe_backup_file(self, file_path: Path) -> Path:
        """Moves a corrupted or replaced file to .backup/ instead of hard-deleting."""
        file_path = Path(file_path).resolve()
        self.backup_root.mkdir(parents=True, exist_ok=True)
        backup_target = self.backup_root / f"{file_path.name}.bak"
        shutil.move(str(file_path), str(backup_target))
        return backup_target
