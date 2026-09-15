# Changelog

All notable changes to the FaFaProFree project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2026-09-15

### Added
- **Internationalization (i18n) Engine (`scripts/i18n.py`)**:
  - Full localization support for 4 languages: `en` (English), `tr` (Türkçe), `ru` (Русский), `de` (Deutsch).
  - Modular dictionary storage under `lang/` (`en.json`, `tr.json`, `ru.json`, `de.json`).
  - Hierarchical language resolution: CLI flag (`--lang`) -> Environment variable (`FAFA_LANG` / `LANG`) -> Config -> Default `en`.
  - Graceful key fallback mechanism protecting against incomplete translations.
  - Dot-notation translation lookup and dynamic template interpolation (`_("key", **kwargs)`).
- **CLI & Wizard Localization**:
  - Added `--lang, -l [en|tr|ru|de]` parameter across all commands.
  - Interactive language selector (`interactive_select_language`) for guided wizard mode.
  - Localized console messages across preflight checks, release discovery banners, dry-run simulation plans, and verification reports.
- **Multilingual Cross-Linked Documentation Suite**:
  - Added cross-language navigation badges to all README files.
  - Localized hero banners matching each language (`Font Awesome Pro Free Thumbnail*.png`).
  - `README.md`: Primary documentation in English.
  - `README.tr.md`: Comprehensive documentation in Turkish.
  - `README.ru.md`: Comprehensive documentation in Russian.
  - `README.de.md`: Comprehensive documentation in German.

## [3.1.0] - 2026-09-15

### Added
- **Dynamic Release Discovery Engine (`scripts/version_resolver.py`)**:
  - Real-time crawling of official releases from `https://github.com/FortAwesome/Font-Awesome/releases?page=*`.
  - 4-layer resilient fallback pipeline: GitHub REST API -> HTML Pagination Scraper -> Atom Feed (`releases.atom`) -> Local config fallback.
  - Automatic SemVer parsing, descending sorting, and major version grouping (v7.x, v6.x, v5.x).
  - Pre-flight Font Awesome CDN asset validation (`validate_cdn_availability`) using lightweight HTTP `HEAD` checks.
  - 24-hour smart version caching (`.cache/versions_cache.json`) with `--refresh-versions` override.
- **Interactive Wizard Upgrades**:
  - Dynamic version selection showing latest discovered releases, LTS versions, and interactive release browser.
- **New CLI Flags**:
  - `--refresh-versions`: Force refresh release cache directly from GitHub.
  - `--pages N`: Configurable pagination depth for crawling releases (default: 3).
  - `--validate-cdn`: Pre-flight check CDN availability for discovered releases.

## [3.0.0] - 2026-09-15

### Added
- **Repository Migration**: Migrated to `https://github.com/user05-ioemlak/FaFaProFree`.
- **Modular Architecture**:
  - `scripts/build.py`: Core build orchestration engine.
  - `scripts/clean.py`: Safe build and artifact cleaning utility.
  - `scripts/verify_build.py`: Automated build verification and security scanner.
- **Build Isolation**: Output generated strictly in `build/v<version>-<profile>/`.
- **Profile Configuration**: `config/build_profiles.json` defining Free, Pro, Pro-Plus, and Custom profiles.
- **Enhanced Progress System**: Rich ASCII header, dynamic progress bar, active spinner, elapsed time, and download speed indicators.
- **Automated Verification**: Automatic verification on completion checking directory structure, required assets, `LICENSE.txt`, `BUILD_INFO.json`, credential leakage, and temporary files.
- **Dual-License Model**: Distinct separation between tool code (MIT) and Font Awesome proprietary third-party notices.
- **CI/CD Automation**: Added GitHub Actions workflows for continuous build testing (`build.yml`) and automated release packaging (`release.yml`).
- **CLI Commands**: Added `--clean`, `--verify`, `--list-profiles`, `--list-versions`, `--non-interactive`, `--archive`, and `--debug`.

### Changed
- Refactored `fa_pro_v3.py` into a robust CLI and interactive wizard supporting custom versions and profiles.
- Standardized logging into `logs/` with automatic redaction of sensitive tokens and authorization headers.
- Completely rewritten `README.md` in Turkish to reflect legal compliance, licensed-access models, and comprehensive usage guides.

### Removed
- Legacy shell (`.sh`) and PowerShell (`.ps1`) scripts in favor of modern cross-platform Python 3.10+ engine.
- Hardcoded URLs and references to legacy repositories.
