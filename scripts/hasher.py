#!/usr/bin/env python3
"""
FaFaProFree - Streaming Hasher and Manifest System
==================================================
Handles streaming chunk-based SHA-256 checksums, manifest generation,
and cryptographic file verification with zero large-memory allocation.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


CHUNK_SIZE = 1024 * 1024  # 1 MB chunk for streaming hashing


def compute_sha256(file_path: Path) -> str:
    """
    Computes the SHA-256 hex digest of a file using streaming 1 MB chunks.
    Safe for multi-gigabyte files.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_file_checksum(file_path: Path, expected_sha256: str) -> bool:
    """
    Verifies if file matches expected SHA-256.
    Returns False if file doesn't exist or hash mismatches.
    """
    if not file_path.exists() or not file_path.is_file():
        return False
    actual_hash = compute_sha256(file_path)
    return actual_hash.lower() == expected_sha256.lower()


def generate_manifest(build_dir: Path, version: str, profile: str) -> Dict[str, Any]:
    """
    Scans build_dir and generates manifest dictionary with relative paths,
    exact file sizes, and streaming SHA-256 hashes.
    Excludes metadata/manifest files themselves.
    """
    build_dir = Path(build_dir).resolve()
    excluded_names = {"manifest.json", "BUILD_INFO.json", "BUILD_REPORT.json", "LICENSE.txt"}

    files_manifest: Dict[str, Dict[str, Any]] = {}

    for file_path in sorted(build_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name in excluded_names or file_path.name.endswith(".part") or file_path.name.endswith(".download"):
            continue

        rel_path = file_path.relative_to(build_dir).as_posix()
        files_manifest[rel_path] = {
            "size": file_path.stat().st_size,
            "sha256": compute_sha256(file_path)
        }

    return {
        "version": version,
        "profile": profile,
        "generator": "fa_pro_v3.py (FaFaProFree Hasher)",
        "file_count": len(files_manifest),
        "files": files_manifest
    }


def write_manifest(manifest_data: Dict[str, Any], output_path: Path) -> Path:
    """Writes manifest JSON cleanly without secrets."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    return output_path


def load_manifest(manifest_path: Path) -> Optional[Dict[str, Any]]:
    """Loads manifest JSON safely if it exists."""
    manifest_path = Path(manifest_path).resolve()
    if not manifest_path.exists():
        return None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
