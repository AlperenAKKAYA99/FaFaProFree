# FaFaProFree 🧪

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Türkçe](https://img.shields.io/badge/Language-T%C3%BCrk%C3%A7e-red.svg)](README.tr.md)
[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-green.svg)](README.ru.md)
[![Deutsch](https://img.shields.io/badge/Language-Deutsch-yellow.svg)](README.de.md)

<br/>

![FaFaProFree English Banner](assets/images/thumbnail.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI Build](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)](.github/workflows/build.yml)
[![Scope: Educational Research](https://img.shields.io/badge/Scope-Educational%20Research-red.svg)](#-legal-licensing-and-copyright-warning)
[![Repository](https://img.shields.io/badge/GitHub-user05--ioemlak%2FFaFaProFree-orange.svg)](https://github.com/user05-ioemlak/FaFaProFree)

**Network Protocols, CDN Architecture, Intelligent Asset Synchronization & Multilingual Build Laboratory**

</div>

---

## ⚖️ Legal Licensing and Copyright Warning

> [!CAUTION]
> ### ⚠️ CRITICAL LEGAL NOTICE: COPYRIGHT AND COMMERCIAL USE RESTRICTIONS
> 
> 1. **Educational & Academic Research Scope:**  
>    This project is developed **strictly for educational, research, and network architecture analysis** purposes. Its objective is to explore modern web protocol standards, HTTP Range-based chunk resumption, streaming SHA-256 cryptographic integrity verification, atomic staging in CI/CD pipelines, and resilient real-time GitHub release crawling.
> 
> 2. **Risk of Copyright Infringement:**  
>    **Font Awesome Pro** is a proprietary commercial product owned and protected by copyright and intellectual property laws of [Fonticons, Inc.](https://fontawesome.com). Using Font Awesome Pro assets (CSS, SVG, WOFF2, JS) without purchasing an official commercial license on public websites, enterprise applications, or commercial products constitutes **DIRECT COPYRIGHT INFRINGEMENT** and may subject violators to substantial civil and criminal liabilities.
> 
> 3. **Not an Unauthorized Distribution or DRM Bypass Tool:**  
>    This software does **not** crack license keys, circumvent payment walls, or reverse-engineer DRM mechanisms. It does not provide or host unauthorized commercial distributions.
> 
> 4. **User Responsibility and Official Licensing Requirement:**  
>    Any individual or entity utilizing this automation tooling is **personally and exclusively responsible** for their own actions and compliance with applicable intellectual property legislation. To use Font Awesome Pro assets in production or commercial environments, you must acquire a valid license directly from Font Awesome:
>    - 🛒 **Purchase Official Font Awesome License:** [fontawesome.com/plans](https://fontawesome.com/plans)
>    - 📜 **Official Terms & Conditions:** [fontawesome.com/license](https://fontawesome.com/license)

---

## 📌 Table of Contents
- [Legal Licensing and Copyright Warning](#-legal-licensing-and-copyright-warning)
- [Educational & Research Objectives](#-educational--research-objectives)
- [System Requirements](#-system-requirements)
- [Quick Installation](#-quick-installation)
- [Usage Guide](#-usage-guide)
  - [1. Interactive Wizard](#1-interactive-wizard)
  - [2. Multilingual Support (--lang)](#2-multilingual-support---lang)
  - [3. Live GitHub Release Discovery (--list-versions)](#3-live-github-release-discovery---list-versions)
  - [4. Command-Line Interface (CLI)](#4-command-line-interface-cli)
  - [5. Dry-Run Simulation (--dry-run)](#5-dry-run-simulation---dry-run)
  - [6. Integrity Verification (--verify)](#6-integrity-verification---verify)
  - [7. Repair Damaged/Missing Assets (--repair)](#7-repair-damagedmissing-assets---repair)
- [Smart Decision Engine & Cryptographic Integrity](#-smart-decision-engine--cryptographic-integrity)
- [Build Profiles (Free, Pro, Pro-Plus, Custom)](#-build-profiles)
- [Isolated Build Directory Architecture](#-isolated-build-directory-architecture)
- [Safe Workspace Cleaning (--clean)](#-safe-workspace-cleaning---clean)
- [GitHub Actions CI/CD Integration](#-github-actions-cicd-integration)
- [Licensing Model](#-licensing-model)

---

## 🔬 Educational & Research Objectives

This open-source research initiative is designed to investigate the following software engineering paradigms:

1. **Terminal Internationalization (i18n):** Modular JSON dictionary architecture (`lang/*.json`) with hierarchical fallbacks and dot-notation interpolation.
2. **Resilient Multi-Layer Web Crawling:** Dynamic release resolution combining GitHub REST API, HTML pagination scraping (`releases?page=N`), and Atom feeds (`releases.atom`) without API rate limit penalties.
3. **HTTP Range-Based Resumption:** Resilient byte-level download continuation (`Range: bytes={pos}-`) upon network disruptions.
4. **Streaming Cryptographic Verification:** Memory-friendly, 1 MB chunk-based streaming calculation using `hashlib.sha256()`.
5. **Fail-Safe Atomic Staging:** Isolated build staging under `build/.staging/` to guarantee zero incomplete build artifacts upon abrupt termination (`CTRL+C`).
6. **Cross-Build Asset Deduplication:** Automatic scanning and verification of pre-existing local builds to eliminate redundant downloads and conserve 90–100% of network bandwidth.

---

## 💻 System Requirements

- **Python:** 3.10 or newer (Python 3.11 / 3.12 recommended)
- **Operating System:** Windows, macOS, or Linux (Fully Cross-Platform)
- **Network:** Standard HTTPS connectivity

---

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/user05-ioemlak/FaFaProFree.git
cd FaFaProFree

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 Usage Guide

### 1. Interactive Wizard

Run without arguments to launch the guided interactive wizard:

```bash
python fa_pro_v3.py
```

The wizard guides you through:
1. **Language:** `[1] English`, `[2] Türkçe`, `[3] Русский`, `[4] Deutsch`
2. **Profile:** `[1] Free`, `[2] Pro`, `[3] Pro-Plus`, `[4] Custom`
3. **Version:** Live discovered releases (e.g. v7.3.1, v7.3.0, v6.7.2 LTS) or browse all 30+ versions
4. **Category:** `[1] Standard (CSS+JS+Fonts)`, `[2] Extended (+Sprites)`, `[3] Custom Selection`

---

### 2. Multilingual Support (`--lang`)

Switch terminal interface language dynamically across 4 supported locales:

```bash
# English interface (default)
python fa_pro_v3.py --lang en --list-versions

# Turkish interface
python fa_pro_v3.py --lang tr --list-versions

# Russian interface
python fa_pro_v3.py --lang ru --list-versions

# German interface
python fa_pro_v3.py --lang de --list-versions
```

---

### 3. Live GitHub Release Discovery (`--list-versions`)

Dynamically crawl releases from `https://github.com/FortAwesome/Font-Awesome/releases?page=*` in real-time with smart caching and CDN validation:

```bash
# List all discovered releases grouped by major version (v7, v6, v5)
python fa_pro_v3.py --list-versions

# Force refresh release cache from GitHub and pre-flight validate CDN assets
python fa_pro_v3.py --refresh-versions --list-versions --validate-cdn

# Scan deeper pagination (default: 3 pages)
python fa_pro_v3.py --list-versions --pages 5
```

---

### 4. Command-Line Interface (CLI)

For scripted workflows and CI/CD pipelines:

```bash
# Build Pro profile (CSS + Webfonts) non-interactively
python fa_pro_v3.py --version 7.3.1 --profile Pro --css --fonts --non-interactive

# Build complete Pro-Plus profile
python fa_pro_v3.py --version 7.3.1 --profile Pro-Plus --non-interactive

# Build official Free open-source package
python fa_pro_v3.py --version 7.3.1 --profile Free --non-interactive

# Package output into a release zip archive
python fa_pro_v3.py --version 7.3.1 --profile Pro --archive --non-interactive
```

---

### 5. Dry-Run Simulation (`--dry-run`)

Inspect the decision engine plan without writing or downloading files:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --dry-run
```

Sample output:
```text
  ✓ css/all.css                            → Reuse (cache/build)
  ✓ js/all.js                              → Reuse (cache/build)
  ↓ webfonts/fa-solid-900.woff2            → Download
  Plan: 0 skip, 62 reuse, 1 download
```

---

### 6. Integrity Verification (`--verify`)

Validate cryptographic SHA-256 checksums and file structures without downloading:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --verify
```

---

### 7. Repair Damaged/Missing Assets (`--repair`)

Scan the target build directory and selectively re-download only corrupted or missing files:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --repair
```

---

## ⚡ Smart Decision Engine & Cryptographic Integrity

```text
                 ┌──────────────────┐
                 │ File exists on   │
                 │ disk?            │
                 └────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │       YES         │
                └─────────┬─────────┘
                          │
                 SHA-256 Validation
                          │
             ┌────────────┴────────────┐
             │                         │
          MATCHES                  MISMATCH
             │                         │
             ▼                         ▼
       SKIP DOWNLOAD             REDOWNLOAD
     (Bandwidth Saved)       (Corrupted/Modified)
```

1. **Cryptographic Checksum Verification:** Files are never assumed valid based on name alone; streaming SHA-256 digests are verified against the manifest.
2. **Cross-Build Asset Reuse:** 63 common files in `v7.3.1-Pro` are automatically reused when compiling `v7.3.1-Pro-Plus` (saving over 92% bandwidth).
3. **Atomic `.part` Isolation:** Downloads are saved as `.part` files during transfer and renamed only after full hash confirmation.

---

## 🎛️ Build Profiles

Profiles are configured in [config/build_profiles.json](config/build_profiles.json):

| Profile Name | Family Count | Scope |
| :--- | :---: | :--- |
| **Free** | 3 | Official free styles: `Solid`, `Regular`, `Brands`. |
| **Pro** | 17 | Classic (`Solid`, `Regular`, `Light`, `Thin`), Duotone, Sharp, and Brands. |
| **Pro-Plus** | 37 | Pro styles + 20 specialty families (`Chisel`, `Etch`, `Jelly`, `Mosaic`, `Pixel`, `Slab`, `Utility`, etc.). |
| **Custom** | Custom | Custom selection of icon families. |

---

## 📁 Isolated Build Directory Architecture

Each build output is isolated cleanly:

```text
build/
└── v7.3.1-Pro-Plus/
    ├── css/
    ├── js/
    ├── webfonts/
    ├── LICENSE.txt          # Third-party notices and licenses
    ├── BUILD_INFO.json      # Version, profile, timestamp metadata
    ├── BUILD_REPORT.json    # Verification statistics and audit
    └── manifest.json        # File paths, byte sizes, and SHA-256 hashes
```

---

## 🧹 Safe Workspace Cleaning (`--clean`)

```bash
# Safely clean build/ and staging directories
python fa_pro_v3.py --clean

# Also clear the local .cache/
python fa_pro_v3.py --clean --clean-cache
```

---

## ⚙️ GitHub Actions CI/CD Integration

The repository includes two automated workflows:
1. **`.github/workflows/build.yml`:** Runs automated build validation and integrity verification on pushes and PRs.
2. **`.github/workflows/release.yml`:** Builds and uploads release zip packages when a Git tag (`v*`) is created.

---

## 📄 Licensing Model

- **Automation Tooling (Codebase):** Licensed under the [MIT License](LICENSE).
- **Font Awesome Assets:** Intellectual property of [Fonticons, Inc.](https://fontawesome.com) and subject to commercial licensing terms.
