#!/usr/bin/env python3
"""
FaFaProFree - Modern Build Automation System v3.0
=================================================
Repository : https://github.com/user05-ioemlak/FaFaProFree
Author     : FaFaProFree Contributors
License    : MIT (Tooling) + Third-Party Notices (Fonticons, Inc.)

Smart download engine, streaming SHA-256 verification, cross-build asset reuse,
atomic staging promotion, and automatic repair system.
"""

import os
import io
import sys
import json
import argparse
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List

# Silence warnings
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

# Windows console encoding fix (cp1254 -> utf-8)
if sys.stdout and hasattr(sys.stdout, 'encoding'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import core build modules from scripts/
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.build import BuildConfig, execute_build, load_config
from scripts.clean import safe_clean
from scripts.verify_build import verify_build
from scripts.version_resolver import (
    get_available_versions,
    validate_cdn_availability,
    clean_version_str,
    group_versions_by_major
)
from scripts.i18n import (
    _,
    t,
    set_language,
    get_language,
    get_supported_languages,
    detect_system_language
)


# ═══════════════════════════════════════════════════════════════════════
#  INTERACTIVE WIZARD
# ═══════════════════════════════════════════════════════════════════════

def interactive_select_language() -> str:
    """Prompts the user to select an interface language."""
    langs = get_supported_languages()
    keys = list(langs.keys())
    current = get_language()
    default_idx = keys.index(current) + 1 if current in keys else 1

    print()
    print("  +----------------------------------------------------+")
    print(f"  |         {_('wizard.select_language_title'):<42} |")
    print("  +----------------------------------------------------+")
    for idx, k in enumerate(keys, 1):
        star = " *" if k == current else ""
        print(f"  |  [{idx}] {langs[k]:<20} ({k.upper()}){star:<15} |")
    print("  +----------------------------------------------------+")
    print()

    choice = input(f"  {_('wizard.select_language_prompt', max=len(keys), current=default_idx)}").strip() or str(default_idx)
    try:
        val = int(choice)
        if 1 <= val <= len(keys):
            chosen = keys[val - 1]
            set_language(chosen)
            return chosen
    except ValueError:
        pass
    return current


def interactive_select_profile(profiles: Dict[str, Any]) -> str:
    """Prompts the user to select an available build profile."""
    print()
    print("  +----------------------------------------------------+")
    print(f"  |            {_('wizard.select_profile_title'):<40} |")
    print("  +----------------------------------------------------+")
    keys = list(profiles.keys())
    for idx, key in enumerate(keys, 1):
        prof = profiles[key]
        label = prof.get("display_name", key)
        desc = prof.get("description", "")
        print(f"  |  [{idx}] {label:<22} ({desc[:25]}...)")
    print("  +----------------------------------------------------+")
    print()

    while True:
        prompt_text = _("wizard.select_profile_prompt", max=len(keys))
        choice = input(f"  {prompt_text}").strip() or "2"
        try:
            val = int(choice)
            if 1 <= val <= len(keys):
                selected = keys[val - 1]
                print(f"  {_('wizard.profile_selected', name=profiles[selected].get('display_name', selected))}")
                return selected
        except ValueError:
            pass
        print(f"  {_('wizard.invalid_range', max=len(keys))}")


def interactive_select_version(workspace_root: Path, config: Dict[str, Any], refresh: bool = False, pages: int = 3) -> str:
    """Prompts the user to select or enter a version using dynamic release discovery."""
    print(f"  {_('wizard.discovering_releases')}", end="\r", flush=True)
    discovery = get_available_versions(workspace_root, refresh=refresh, max_pages=pages)
    latest_v = discovery.get("latest", "7.3.1")
    versions = discovery.get("versions", [])
    source = discovery.get("source", "cache")

    # Pick top versions to show in quick menu
    quick_versions: List[str] = []
    if latest_v and latest_v not in quick_versions:
        quick_versions.append(latest_v)
    for v in versions:
        if v not in quick_versions and len(quick_versions) < 4:
            quick_versions.append(v)

    # Find the latest v6 if not yet in quick list
    v6_list = discovery.get("groups", {}).get("v6", [])
    if v6_list and v6_list[0] not in quick_versions and len(quick_versions) < 5:
        quick_versions.append(v6_list[0])

    print(" " * 50, end="\r", flush=True)
    print()
    print("  +----------------------------------------------------+")
    print(f"  |            {_('wizard.select_version_title'):<40} |")
    print("  +----------------------------------------------------+")
    for idx, v in enumerate(quick_versions, 1):
        badge = ""
        if v == latest_v:
            badge = _("wizard.latest_badge")
        elif v.startswith("6."):
            badge = _("wizard.lts_badge")
        elif v.startswith("5."):
            badge = _("wizard.legacy_badge")
        print(f"  |  [{idx}] v{v:<12} {badge}")

    browse_idx = len(quick_versions) + 1
    custom_idx = len(quick_versions) + 2
    print(f"  |  [{browse_idx}] {_('wizard.browse_all_releases', count=len(versions))}")
    print(f"  |  [{custom_idx}] {_('wizard.custom_version_input')}")
    print("  +----------------------------------------------------+")
    print(f"  {_('wizard.source_summary', source=source, count=len(versions))}")
    print()

    while True:
        choice = input(f"  {_('wizard.select_version_prompt', max=custom_idx)}").strip() or "1"
        try:
            val = int(choice)
            if 1 <= val <= len(quick_versions):
                return quick_versions[val - 1]
            elif val == browse_idx:
                print()
                print("  ══════════════════════════════════════════════════════")
                print(f"             {_('wizard.all_releases_title'):<42}")
                print("  ══════════════════════════════════════════════════════")
                groups = discovery.get("groups", {})
                num_map = {}
                counter = 1
                for grp, grp_versions in groups.items():
                    print(f"\n  ── {grp.upper()} Releases ──")
                    for v in grp_versions:
                        star = f" {_('wizard.latest_badge')}" if v == latest_v else ""
                        print(f"    [{counter:2d}] v{v:<10}{star}")
                        num_map[counter] = v
                        counter += 1
                print("  ══════════════════════════════════════════════════════")
                print()
                sub_choice = input(f"  {_('wizard.select_release_num', max=counter-1)}").strip()
                if sub_choice.lower() == 'b':
                    continue
                try:
                    s_val = int(sub_choice)
                    if s_val in num_map:
                        return num_map[s_val]
                except ValueError:
                    pass
                print(f"  {_('wizard.invalid_option', max=counter-1)}")
            elif val == custom_idx:
                custom_ver = input(f"  {_('wizard.custom_version_prompt')}").strip().lstrip("v")
                if custom_ver:
                    return custom_ver
        except ValueError:
            pass
        print(f"  {_('wizard.invalid_option', max=custom_idx)}")


def interactive_select_categories() -> Dict[str, bool]:
    """Prompts for target asset categories."""
    print()
    print("  +----------------------------------------------------+")
    print(f"  |            {_('wizard.select_categories_title'):<40} |")
    print("  +----------------------------------------------------+")
    print(f"  |  [1] {_('wizard.cat_standard'):<46} |")
    print(f"  |  [2] {_('wizard.cat_extended'):<46} |")
    print(f"  |  [3] {_('wizard.cat_complete'):<46} |")
    print(f"  |  [4] {_('wizard.cat_custom'):<46} |")
    print("  +----------------------------------------------------+")
    print()

    while True:
        choice = input(f"  {_('wizard.select_cat_prompt')}").strip() or "1"
        if choice == "1":
            return {"css": True, "js": True, "fonts": True, "sprites": False}
        elif choice == "2":
            return {"css": True, "js": True, "fonts": True, "sprites": True}
        elif choice == "3":
            return {"css": True, "js": True, "fonts": True, "sprites": True}
        elif choice == "4":
            cats = {}
            cats["css"] = input(f"  {_('wizard.ask_css')}").strip().lower() != "n"
            cats["js"] = input(f"  {_('wizard.ask_js')}").strip().lower() != "n"
            cats["fonts"] = input(f"  {_('wizard.ask_fonts')}").strip().lower() != "n"
            cats["sprites"] = input(f"  {_('wizard.ask_sprites')}").strip().lower() == "y"
            return cats
        print("  ! Please enter 1, 2, 3, or 4.")


# ═══════════════════════════════════════════════════════════════════════
#  CLI ARGUMENT PARSING
# ═══════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="FaFaProFree - Modern Build Automation System v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fa_pro_v3.py                               # Interactive build wizard
  python fa_pro_v3.py --version 7.3.1 --profile Pro # Smart build (skips verified assets)
  python fa_pro_v3.py --version 7.3.1 --profile Pro --verify   # Verify-only without downloading
  python fa_pro_v3.py --version 7.3.1 --profile Pro --repair   # Fix missing/corrupted files
  python fa_pro_v3.py --version 7.3.1 --profile Pro --dry-run  # Show execution plan
  python fa_pro_v3.py --version 7.3.1 --profile Pro --force    # Force complete redownload
  python fa_pro_v3.py --clean                       # Clean generated build files & cache
        """
    )

    # Core build parameters
    parser.add_argument("--version", "-v", type=str, default=None,
                        help="Font Awesome release version (e.g. 7.3.1)")
    parser.add_argument("--profile", "-p", type=str, default=None,
                        help="Build profile: Free, Pro, Pro-Plus, Custom")
    parser.add_argument("--plan", type=str, default=None,
                        help="Backward-compatibility alias for --profile (e.g. pro, pro-plus)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Custom base build directory (default: build/)")
    parser.add_argument("--workers", "-w", type=int, default=4,
                        help="Parallel worker threads (default: 4)")
    parser.add_argument("--force", action="store_true",
                        help="Force redownload, bypassing cache and cross-build reuse")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Disable interactive wizard prompts")
    parser.add_argument("--archive", action="store_true",
                        help="Create release zip archive upon build completion")
    parser.add_argument("--debug", action="store_true",
                        help="Enable verbose debug logging in logs/")

    parser.add_argument("--lang", "-l", type=str, choices=["en", "tr", "ru", "de"], default=None,
                        help="Interface language: en (English), tr (Türkçe), ru (Русский), de (Deutsch)")

    # Smart features
    smart_group = parser.add_argument_group("Smart Modes")
    smart_group.add_argument("--dry-run", action="store_true",
                             help="Simulate execution without downloading or writing files")
    smart_group.add_argument("--repair", action="store_true",
                             help="Scan existing build and repair missing/corrupted files")
    smart_group.add_argument("--verify", action="store_true",
                             help="Verify integrity of existing build without downloading")
    smart_group.add_argument("--verify-level", type=str, choices=["quick", "standard", "strict"],
                             default="standard", help="Integrity check level (default: standard)")

    # Asset categories
    cat_group = parser.add_argument_group("Category Options")
    cat_group.add_argument("--all", "-a", action="store_true", help="Include all asset categories")
    cat_group.add_argument("--css", action="store_true", help="Download CSS stylesheets")
    cat_group.add_argument("--js", action="store_true", help="Download JavaScript files")
    cat_group.add_argument("--fonts", action="store_true", help="Download webfonts (.woff2)")
    cat_group.add_argument("--sprites", action="store_true", help="Download SVG sprites")

    # Live Version Discovery
    version_group = parser.add_argument_group("Release Discovery")
    version_group.add_argument("--refresh-versions", action="store_true",
                               help="Force refresh cached release list from GitHub")
    version_group.add_argument("--pages", type=int, default=3,
                               help="Number of GitHub release pages to scan (default: 3)")
    version_group.add_argument("--validate-cdn", action="store_true",
                               help="Pre-flight check CDN availability for discovered releases")

    # Utilities
    util_group = parser.add_argument_group("Utility Commands")
    util_group.add_argument("--clean", action="store_true",
                            help="Safely remove build/ artifacts and temporary files")
    util_group.add_argument("--clean-cache", action="store_true",
                            help="Also delete .cache/ when cleaning")
    util_group.add_argument("--list-profiles", action="store_true",
                            help="List all defined build profiles and exit")
    util_group.add_argument("--list-versions", action="store_true",
                            help="List discovered Font Awesome releases from GitHub and exit")

    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════════════
#  MAIN CONTROLLER
# ═══════════════════════════════════════════════════════════════════════

def main():
    args = parse_args()
    workspace_root = ROOT_DIR

    # Initialize language from CLI, Environment, or System
    selected_lang = args.lang or detect_system_language()
    set_language(selected_lang)

    # 1. Clean Utility Mode
    if args.clean:
        safe_clean(workspace_root, clean_cache=args.clean_cache)
        sys.exit(0)

    # Load project configuration
    full_cfg = load_config(workspace_root)
    profiles = full_cfg.get("profiles", {})

    # 2. List Profiles Mode
    if args.list_profiles:
        print("\n  Available FaFaProFree Build Profiles:")
        print("  " + "─" * 55)
        for key, p in profiles.items():
            print(f"  • {key:<12} : {p.get('display_name', key)} ({len(p.get('families', []))} families)")
            print(f"    Description  : {p.get('description', '')}")
        print("  " + "─" * 55 + "\n")
        sys.exit(0)

    # 3. List Versions Mode
    if args.list_versions:
        print(f"\n  {_('discovery.discovering')}")
        data = get_available_versions(
            workspace_root=workspace_root,
            refresh=args.refresh_versions,
            max_pages=args.pages,
            validate_cdn=args.validate_cdn
        )
        print("\n  ╔════════════════════════════════════════════════════════════╗")
        print(f"  ║        {_('discovery.banner'):<51} ║")
        print("  ╚════════════════════════════════════════════════════════════╝")
        print(f"  {_('discovery.source', source=data.get('source'))}")
        print(f"  {_('discovery.discovered', count=data.get('total_discovered', len(data.get('versions', []))))}")
        print(f"  {_('discovery.latest_release', latest=data.get('latest'))}")
        print(f"  {_('discovery.last_updated', time=data.get('updated_at'))}")
        print()

        groups = data.get("groups", {})
        for major, v_list in groups.items():
            print(f"  {_('discovery.major_releases', major=major.upper(), count=len(v_list))}")
            for v in v_list[:8]:
                cdn_flag = ""
                if args.validate_cdn and v in data.get("cdn_status", {}):
                    cdn_ok = data["cdn_status"][v]
                    cdn_flag = _("discovery.cdn_online") if cdn_ok else _("discovery.cdn_unavailable")
                star = f" {_('wizard.latest_badge')}" if v == data.get("latest") else ""
                print(f"    • v{v:<12}{star}{cdn_flag}")
            if len(v_list) > 8:
                print(f"      {_('discovery.more_in_group', count=len(v_list) - 8, major=major.upper())}")
            print()
        sys.exit(0)

    # 4. Global Verify Mode (if --verify passed without version/profile)
    if args.verify and not args.version and not args.profile and not args.plan:
        build_root = workspace_root / "build"
        if not build_root.exists() or not any(build_root.iterdir()):
            print(f"\n  {_('errors.no_builds_found')}\n")
            sys.exit(0)
        overall = True
        for item in sorted(build_root.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                passed, report = verify_build(item, level=args.verify_level)
                if not passed:
                    overall = False
        sys.exit(0 if overall else 1)

    # 5. Determine Profile
    profile_key = args.profile or args.plan
    if profile_key:
        matched_key = None
        for k in profiles.keys():
            if k.lower() == profile_key.lower() or k.lower().replace("-", "") == profile_key.lower().replace("-", ""):
                matched_key = k
                break
        if not matched_key:
            print(f"  {_('errors.unknown_profile', name=profile_key, profiles=', '.join(profiles.keys()))}")
            sys.exit(1)
        profile_key = matched_key
    elif args.non_interactive or args.dry_run or args.verify or args.repair:
        profile_key = "Pro"
    else:
        profile_key = interactive_select_profile(profiles)

    # 6. Determine Version
    version = args.version
    if version:
        version = version.lstrip("v")
    elif args.non_interactive or args.dry_run or args.verify or args.repair:
        disco = get_available_versions(
            workspace_root=workspace_root,
            refresh=args.refresh_versions,
            max_pages=args.pages
        )
        version = disco.get("latest", full_cfg.get("default_version", "7.3.1"))
    else:
        version = interactive_select_version(
            workspace_root,
            full_cfg,
            refresh=args.refresh_versions,
            pages=args.pages
        )

    # 7. Determine Categories
    if args.all:
        categories = {"css": True, "js": True, "fonts": True, "sprites": True}
    elif any([args.css, args.js, args.fonts, args.sprites]):
        categories = {
            "css": args.css,
            "js": args.js,
            "fonts": args.fonts,
            "sprites": args.sprites,
        }
    elif args.non_interactive or args.dry_run or args.verify or args.repair:
        categories = {"css": True, "js": True, "fonts": True, "sprites": False}
    else:
        categories = interactive_select_categories()

    # Build target directory preview
    safe_v = version.lstrip("v")
    target_preview = f"build/v{safe_v}-{profile_key}/"

    # Build configuration object
    build_config = BuildConfig(
        version=version,
        profile=profile_key,
        profile_data=profiles[profile_key],
        output_dir=Path(target_preview),
        categories=categories,
        workers=args.workers,
        force=args.force,
        interactive=not args.non_interactive,
        debug=args.debug,
        archive=args.archive,
        dry_run=args.dry_run,
        repair=args.repair,
        verify_only=args.verify,
        verify_level=args.verify_level,
        cdn_base_url=full_cfg.get("cdn_base_url", "https://site-assets.fontawesome.com/releases"),
        repository=full_cfg.get("repository", "user05-ioemlak/FaFaProFree")
    )

    # Execute Build Engine
    success = execute_build(build_config, workspace_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
