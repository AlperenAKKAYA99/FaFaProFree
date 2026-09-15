#!/usr/bin/env python3
"""
FaFaProFree - Dynamic Release Discovery & Version Resolver
==========================================================
Repository : https://github.com/user05-ioemlak/FaFaProFree
License    : MIT (Tooling)

Real-time crawler and resolver for Font Awesome releases.
Discovers available releases from GitHub using a resilient 4-layer fallback model:
  1. GitHub REST API (Structured JSON)
  2. HTML Pagination Scraper (releases?page=N - zero API rate limit impact)
  3. GitHub Atom Feed (releases.atom - high-speed top releases)
  4. Local Configuration Fallback (config/build_profiles.json)

Includes 24-hour smart caching (.cache/versions_cache.json), pre-flight CDN
validation, and semver sorting/grouping.
"""

import os
import io
import sys
import re
import json
import time
import warnings

# Silence warnings before importing requests
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
import xml.etree.ElementTree as ET

# Ensure project root is in sys.path for direct execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


import requests

# Windows console encoding fix
if sys.stdout and hasattr(sys.stdout, 'encoding'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DEFAULT_TTL_SECONDS = 86400  # 24 hours
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fontawesome.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


# ═══════════════════════════════════════════════════════════════════════
#  SEMANTIC VERSION HELPERS
# ═══════════════════════════════════════════════════════════════════════

def clean_version_str(ver_str: str) -> str:
    """Strips leading 'v', 'Release ', whitespace, and non-version noise."""
    v = ver_str.strip()
    if v.lower().startswith("release"):
        v = v[7:].strip()
    return v.lstrip("v").strip()


def parse_semver(ver_str: str) -> Tuple[int, int, int, str]:
    """
    Parses clean semver strings for robust numerical sorting.
    Examples:
      '7.3.1' -> (7, 3, 1, '')
      '6.5.2-beta.1' -> (6, 5, 2, 'beta.1')
    """
    cleaned = clean_version_str(ver_str)
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([a-zA-Z0-9.\-_]+))?$", cleaned)
    if not match:
        return (0, 0, 0, cleaned)
    major = int(match.group(1) or 0)
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    prerelease = match.group(4) or ""
    return (major, minor, patch, prerelease)


def sort_versions_descending(versions: List[str]) -> List[str]:
    """Sorts version strings in descending semantic order (newest first)."""
    def sort_key(v: str):
        major, minor, patch, pre = parse_semver(v)
        # Empty prerelease should sort higher than prereleases (e.g., 7.0.0 > 7.0.0-beta)
        pre_weight = 1 if not pre else 0
        return (major, minor, patch, pre_weight, pre)

    # Deduplicate while preserving order, then sort
    unique = []
    seen = set()
    for ver in versions:
        c = clean_version_str(ver)
        if c and c not in seen and re.match(r"^\d+\.\d+", c):
            seen.add(c)
            unique.append(c)

    return sorted(unique, key=sort_key, reverse=True)


def group_versions_by_major(versions: List[str]) -> Dict[str, List[str]]:
    """Groups versions into major version buckets (e.g. 'v7', 'v6', 'v5')."""
    groups: Dict[str, List[str]] = {}
    for ver in versions:
        major, _, _, _ = parse_semver(ver)
        key = f"v{major}" if major > 0 else "other"
        groups.setdefault(key, []).append(ver)
    return groups


# ═══════════════════════════════════════════════════════════════════════
#  CRAWLER & SCRAPER ENGINES
# ═══════════════════════════════════════════════════════════════════════

def fetch_versions_from_api(max_pages: int = 2, token: Optional[str] = None) -> List[str]:
    """
    Fetches releases via GitHub REST API.
    Returns empty list if rate limited (403/429) or network fails.
    """
    versions = []
    headers = dict(DEFAULT_HEADERS)
    headers["Accept"] = "application/vnd.github.v3+json"
    if token:
        headers["Authorization"] = f"token {token}"

    session = requests.Session()
    try:
        for page in range(1, max_pages + 1):
            url = f"https://api.github.com/repos/FortAwesome/Font-Awesome/releases?per_page=50&page={page}"
            resp = session.get(url, headers=headers, timeout=6)
            if resp.status_code == 403 or resp.status_code == 429:
                # Rate limit hit; graceful fallback
                break
            if resp.status_code != 200:
                break
            items = resp.json()
            if not items or not isinstance(items, list):
                break
            for item in items:
                tag = item.get("tag_name") or item.get("name") or ""
                c = clean_version_str(tag)
                if c:
                    versions.append(c)
    except Exception:
        pass
    return sort_versions_descending(versions)


def scrape_versions_from_html(max_pages: int = 3) -> List[str]:
    """
    Scrapes https://github.com/FortAwesome/Font-Awesome/releases?page=N.
    Bypasses GitHub API rate limits. Scrapes release tags via regex.
    """
    versions = []
    session = requests.Session()

    for page in range(1, max_pages + 1):
        url = f"https://github.com/FortAwesome/Font-Awesome/releases?page={page}"
        try:
            resp = session.get(url, headers=DEFAULT_HEADERS, timeout=7)
            if resp.status_code != 200:
                break
            html = resp.text
            # Match release tags in href attributes
            matches = re.findall(r'/FortAwesome/Font-Awesome/releases/tag/([^"\'\s/>]+)', html)
            for m in matches:
                c = clean_version_str(m)
                if c:
                    versions.append(c)
        except Exception:
            break

    return sort_versions_descending(versions)


def fetch_versions_from_atom() -> List[str]:
    """
    Fetches releases via GitHub Atom Feed.
    Fast, lightweight, and not subject to REST API quotas.
    """
    versions = []
    url = "https://github.com/FortAwesome/Font-Awesome/releases.atom"
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=6)
        if resp.status_code == 200:
            tree = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in tree.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                if title_elem is not None and title_elem.text:
                    c = clean_version_str(title_elem.text)
                    if c:
                        versions.append(c)
                id_elem = entry.find("atom:id", ns)
                if id_elem is not None and id_elem.text:
                    parts = id_elem.text.split("/")
                    if parts:
                        c_id = clean_version_str(parts[-1])
                        if c_id:
                            versions.append(c_id)
    except Exception:
        pass
    return sort_versions_descending(versions)


def validate_cdn_availability(version: str, timeout: float = 3.5) -> bool:
    """
    Performs pre-flight validation to check if Font Awesome CDN has published
    the release assets. Checks /releases/v{version}/css/all.css.
    Returns True if CDN responds with HTTP 200.
    """
    clean_v = clean_version_str(version)
    url = f"https://site-assets.fontawesome.com/releases/v{clean_v}/css/all.css"
    headers = {
        "User-Agent": DEFAULT_HEADERS["User-Agent"],
        "Referer": "https://fontawesome.com/"
    }
    try:
        resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        return resp.status_code == 200
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════
#  CACHE MANAGEMENT (.cache/versions_cache.json)
# ═══════════════════════════════════════════════════════════════════════

def get_cache_file_path(workspace_root: Path) -> Path:
    return workspace_root / ".cache" / "versions_cache.json"


def load_version_cache(cache_path: Path, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> Optional[Dict[str, Any]]:
    """Loads cached version data if present and within TTL."""
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_timestamp = data.get("timestamp", 0)
        if time.time() - cached_timestamp < ttl_seconds:
            return data
    except Exception:
        pass
    return None


def save_version_cache(cache_path: Path, data: Dict[str, Any]) -> None:
    """Saves resolved versions to cache file atomically."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = cache_path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(cache_path)
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════
#  HIGH-LEVEL RESOLVER ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════

def get_available_versions(
    workspace_root: Optional[Path] = None,
    refresh: bool = False,
    max_pages: int = 3,
    validate_cdn: bool = False
) -> Dict[str, Any]:
    """
    Resolves available Font Awesome releases through the 4-layer fallback pipeline.
    
    Returns dict:
      {
        "latest": "7.3.1",
        "versions": ["7.3.1", "7.3.0", ...],
        "groups": {"v7": [...], "v6": [...], "v5": [...]},
        "source": "cache" | "html_scrape" | "api" | "atom_feed" | "offline_config",
        "updated_at": "2026-09-15T...",
        "cdn_status": {"7.3.1": True, ...} (if validate_cdn=True)
      }
    """
    if workspace_root is None:
        workspace_root = Path(__file__).resolve().parent.parent

    cache_file = get_cache_file_path(workspace_root)

    # 1. Check local cache (unless refresh requested)
    if not refresh:
        cached = load_version_cache(cache_file)
        if cached and cached.get("versions"):
            cached["source"] = "cache"
            return cached

    versions: List[str] = []
    source = "offline_config"

    # 2. Try Layer 1: GitHub HTML Pagination Scraper (Most reliable, no API key limit)
    try:
        scraped = scrape_versions_from_html(max_pages=max_pages)
        if scraped:
            versions = scraped
            source = "html_scrape"
    except Exception:
        pass

    # 3. Try Layer 2: GitHub Atom Feed (if scraper returned nothing)
    if not versions:
        try:
            atom_vers = fetch_versions_from_atom()
            if atom_vers:
                versions = atom_vers
                source = "atom_feed"
        except Exception:
            pass

    # 4. Try Layer 3: GitHub REST API
    if not versions:
        try:
            token = os.environ.get("GITHUB_TOKEN")
            api_vers = fetch_versions_from_api(max_pages=max_pages, token=token)
            if api_vers:
                versions = api_vers
                source = "api"
        except Exception:
            pass

    # 5. Fallback Layer 4: Local config/build_profiles.json
    if not versions:
        cfg_file = workspace_root / "config" / "build_profiles.json"
        if cfg_file.exists():
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    versions = cfg.get("supported_versions", ["7.3.1", "7.3.0", "6.7.2"])
                    source = "offline_config"
            except Exception:
                pass

    if not versions:
        versions = ["7.3.1", "7.3.0", "7.2.0", "6.7.2", "5.15.4"]
        source = "hardcoded_fallback"

    sorted_versions = sort_versions_descending(versions)
    latest_ver = sorted_versions[0] if sorted_versions else "7.3.1"
    grouped = group_versions_by_major(sorted_versions)

    # Optional CDN validation for top 5 versions
    cdn_status = {}
    if validate_cdn:
        for v in sorted_versions[:5]:
            cdn_status[v] = validate_cdn_availability(v)

    result_data = {
        "latest": latest_ver,
        "versions": sorted_versions,
        "groups": grouped,
        "source": source,
        "total_discovered": len(sorted_versions),
        "timestamp": time.time(),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "cdn_status": cdn_status
    }

    # Save to cache
    save_version_cache(cache_file, result_data)

    return result_data


def format_github_summary(data: Dict[str, Any]) -> str:
    """Formats discovery results into a clean Markdown table for GitHub Actions."""
    lines = [
        "### 🔍 Font Awesome Release Discovery Summary",
        "",
        f"- **Discovery Source:** `{data.get('source')}`",
        f"- **Total Discovered Releases:** `{data.get('total_discovered', len(data.get('versions', [])))}`",
        f"- **Latest Discovered Release:** **v{data.get('latest')}**",
        f"- **Last Updated:** `{data.get('updated_at')}`",
        "",
        "| Major Series | Top Releases in Series | Total |",
        "| :--- | :--- | :---: |"
    ]
    groups = data.get("groups", {})
    for major, v_list in groups.items():
        top_vers = ", ".join([f"`v{v}`" for v in v_list[:5]])
        lines.append(f"| **{major.upper()}** | {top_vers} | {len(v_list)} releases |")
    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  CLI TEST & DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="FaFaProFree Release Discovery Engine")
    parser.add_argument("--refresh", action="store_true", help="Force refresh cache from GitHub")
    parser.add_argument("--pages", type=int, default=3, help="Pages of releases to scrape (default: 3)")
    parser.add_argument("--validate", action="store_true", help="Validate CDN availability of top versions")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--get-latest", action="store_true", help="Output only the latest version string")
    parser.add_argument("--github-summary", action="store_true", help="Output summary in Markdown and write to GITHUB_STEP_SUMMARY if present")
    args = parser.parse_args()

    data = get_available_versions(refresh=args.refresh, max_pages=args.pages, validate_cdn=args.validate)

    if args.get_latest:
        print(data.get("latest", "7.3.1"))
        return

    if args.github_summary:
        summary = format_github_summary(data)
        print(summary)
        summary_env = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_env:
            try:
                with open(summary_env, "a", encoding="utf-8") as f:
                    f.write(summary + "\n")
            except Exception:
                pass
        return

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     FaFaProFree - Live Release Discovery Engine            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  Source          : {data.get('source')}")
    print(f"  Discovered      : {data.get('total_discovered', len(data.get('versions', [])))} releases")
    print(f"  Latest Release  : v{data.get('latest')}")
    print(f"  Last Updated    : {data.get('updated_at')}")
    print()

    groups = data.get("groups", {})
    for major, v_list in groups.items():
        print(f"  ── {major.upper()} Releases ({len(v_list)}) ──")
        for v in v_list[:6]:
            cdn_flag = ""
            if args.validate and v in data.get("cdn_status", {}):
                cdn_ok = data["cdn_status"][v]
                cdn_flag = " [CDN: ✓ Online]" if cdn_ok else " [CDN: ✗ Unavailable]"
            latest_badge = " (Latest)" if v == data.get("latest") else ""
            print(f"    • v{v:<12}{latest_badge}{cdn_flag}")
        if len(v_list) > 6:
            print(f"      ... and {len(v_list) - 6} more")
        print()


if __name__ == "__main__":
    main()

