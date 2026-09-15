#!/usr/bin/env python3
"""
FaFaProFree - Smart Downloader & Integrity Decision Engine
=========================================================
Handles intelligent asset downloading, atomic .part file writing,
HTTP Range resumption, exponential backoff retries, and streaming hashing.
"""

import os
import io
import sys
import time
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Set, Callable
import warnings
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

import requests

from scripts.hasher import compute_sha256, verify_file_checksum
from scripts.cache_manager import CacheManager


CHUNK_SIZE = 64 * 1024  # 64 KB download chunks


class DownloadItem:
    """Represents a scheduled asset in the download decision pipeline."""
    def __init__(self, url: str, target_path: Path, rel_path: str, expected_sha256: Optional[str] = None):
        self.url = url
        self.target_path = Path(target_path)
        self.rel_path = rel_path
        self.expected_sha256 = expected_sha256
        self.status: str = "pending"  # "reused", "downloaded", "skipped", "failed", "corrupted"
        self.size_bytes: int = 0
        self.sha256: Optional[str] = None
        self.error_msg: Optional[str] = None


class SmartDownloadEngine:
    """Orchestrates asset discovery, cache inspection, and network downloads."""

    def __init__(self, cache_mgr: CacheManager, headers: Dict[str, str],
                 workers: int = 4, force: bool = False):
        self.cache_mgr = cache_mgr
        self.headers = headers
        self.workers = max(1, workers)
        self.force = force
        self.total_downloaded_bytes = 0
        self.total_saved_bytes = 0

    def evaluate_item(self, item: DownloadItem, version: str,
                      existing_manifest: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes Download Decision Engine:
        1. Target file exists?
           - If hash matches expected: SKIP
           - If hash mismatches: CORRUPTED -> REDOWNLOAD
        2. Local cache exists?
           - Copy from cache -> REUSE
        3. Cross-build asset exists?
           - Copy from other build -> REUSE
        4. Else:
           - DOWNLOAD
        """
        if self.force:
            return "download"

        target = item.target_path

        # 1. Target already exists in current build/staging folder
        if target.exists() and target.is_file() and target.stat().st_size > 0:
            target_size = target.stat().st_size
            expected_hash = item.expected_sha256

            # If expected hash not passed, check previous manifest
            if not expected_hash and existing_manifest:
                file_info = existing_manifest.get("files", {}).get(item.rel_path)
                if file_info:
                    expected_hash = file_info.get("sha256")

            if expected_hash:
                actual_hash = compute_sha256(target)
                if actual_hash.lower() == expected_hash.lower():
                    item.status = "skipped"
                    item.size_bytes = target_size
                    item.sha256 = actual_hash
                    self.total_saved_bytes += target_size
                    return "skip"
                else:
                    # Checksum mismatch: file was modified/corrupted
                    item.status = "corrupted"
                    return "redownload"
            else:
                # Basic non-zero size check
                item.status = "skipped"
                item.size_bytes = target_size
                item.sha256 = compute_sha256(target)
                self.total_saved_bytes += target_size
                return "skip"

        # 2. Check local .cache/
        cached_file = self.cache_mgr.get_cached_asset(version, item.rel_path)
        if cached_file:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cached_file, target)
                item.status = "reused"
                item.size_bytes = target.stat().st_size
                item.sha256 = compute_sha256(target)
                self.total_saved_bytes += item.size_bytes
                return "reused_cache"
            except Exception:
                pass

        # 3. Check cross-build reuse from another build of the same version
        cross_asset = self.cache_mgr.find_cross_build_asset(version, item.rel_path, exclude_dir=target.parent.parent)
        if cross_asset:
            src_path, src_build = cross_asset
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, target)
                item.status = "reused"
                item.size_bytes = target.stat().st_size
                item.sha256 = compute_sha256(target)
                self.total_saved_bytes += item.size_bytes
                # Also store in cache for future builds
                self.cache_mgr.store_cached_asset(version, item.rel_path, target)
                return f"reused_{src_build}"
            except Exception:
                pass

        return "download"

    def download_file_atomic(self, item: DownloadItem, version: str) -> bool:
        """
        Downloads asset with:
        - Atomic .part file
        - HTTP Range resumption
        - Exponential backoff (2s, 4s, 8s)
        - Streaming SHA-256 calculation
        - Safe rename to final destination
        """
        target = item.target_path
        part_path = target.with_suffix(target.suffix + ".part")
        target.parent.mkdir(parents=True, exist_ok=True)

        max_attempts = 3
        backoff_delays = [2, 4, 8]

        for attempt in range(1, max_attempts + 1):
            req_headers = dict(self.headers)
            resume_pos = 0

            # Check for existing partial download for Range resumption
            if part_path.exists() and part_path.stat().st_size > 0:
                resume_pos = part_path.stat().st_size
                req_headers["Range"] = f"bytes={resume_pos}-"

            try:
                response = requests.get(item.url, headers=req_headers, stream=True, timeout=30)

                # Auth / Forbidden errors: Do NOT retry needlessly
                if response.status_code in (401, 403):
                    item.status = "failed"
                    item.error_msg = f"HTTP {response.status_code} Access Denied"
                    part_path.unlink(missing_ok=True)
                    return False

                if response.status_code == 404:
                    item.status = "failed"
                    item.error_msg = "HTTP 404 Not Found"
                    part_path.unlink(missing_ok=True)
                    return False

                # Handle Range response
                file_mode = "ab" if response.status_code == 206 else "wb"
                if response.status_code != 206:
                    resume_pos = 0

                response.raise_for_status()

                hasher = hashlib.sha256()
                with open(part_path, file_mode) as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            self.total_downloaded_bytes += len(chunk)

                # Completed download: verify size and checksum
                if part_path.stat().st_size == 0:
                    part_path.unlink(missing_ok=True)
                    raise IOError("Downloaded 0 bytes")

                actual_hash = compute_sha256(part_path)
                if item.expected_sha256 and actual_hash.lower() != item.expected_sha256.lower():
                    part_path.unlink(missing_ok=True)
                    raise ValueError(f"Checksum mismatch: expected {item.expected_sha256[:8]}, got {actual_hash[:8]}")

                # Atomic rename from .part to final destination
                if target.exists():
                    target.unlink()
                part_path.rename(target)

                item.status = "downloaded"
                item.size_bytes = target.stat().st_size
                item.sha256 = actual_hash

                # Store in persistent local cache
                self.cache_mgr.store_cached_asset(version, item.rel_path, target)
                return True

            except (requests.RequestException, IOError, ValueError) as e:
                item.error_msg = str(e)
                if attempt < max_attempts:
                    delay = backoff_delays[attempt - 1]
                    time.sleep(delay)
                else:
                    item.status = "failed"
                    part_path.unlink(missing_ok=True)
                    return False

        return False
