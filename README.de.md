# FaFaProFree 🧪

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Türkçe](https://img.shields.io/badge/Language-T%C3%BCrk%C3%A7e-red.svg)](README.tr.md)
[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-green.svg)](README.ru.md)
[![Deutsch](https://img.shields.io/badge/Language-Deutsch-yellow.svg)](README.de.md)

<br/>

![FaFaProFree Deutscher Banner](assets/images/thumbnail_de.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI Build](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)](.github/workflows/build.yml)
[![Scope: Educational Research](https://img.shields.io/badge/Scope-Educational%20Research-red.svg)](#-rechtliche-hinweise-und-urheberrechtswarnung)
[![Repository](https://img.shields.io/badge/GitHub-user05--ioemlak%2FFaFaProFree-orange.svg)](https://github.com/user05-ioemlak/FaFaProFree)

**Netzwerkprotokolle, CDN-Architektur, intelligente Asset-Synchronisation & mehrsprachiges Build-Labor**

</div>

---

## ⚖️ Rechtliche Hinweise und Urheberrechtswarnung

> [!CAUTION]
> ### ⚠️ WICHTIGER RECHTLICHER HINWEIS: URHEBERRECHT UND KOMMERZIELLE EINSCHRÄNKUNGEN
> 
> 1. **Bildungs- und Forschungsumfang:**  
>    Dieses Projekt wurde **ausschließlich zu Bildungs-, Forschungs- und Netzwerkanalysezwecken** entwickelt. Ziel ist die Untersuchung moderner Webprotokolle, HTTP-Range-basierter Download-Wiederaufnahme, speichereffizienter kryptografischer SHA-256-Integritätsprüfung, atomarer Staging-Build-Prozesse und robuster Versionserkennung über GitHub.
> 
> 2. **Gefahr von Urheberrechtsverletzungen (Copyright Infringement):**  
>    **Font Awesome Pro** ist ein geschütztes, kommerzielles Softwareprodukt im Eigentum von [Fonticons, Inc.](https://fontawesome.com). Die unlizenzierte Nutzung von Font Awesome Pro-Dateien (CSS, SVG, WOFF2, JS) auf kommerziellen Websites, in Unternehmenssoftware oder in öffentlich zugänglichen Projekten ohne Erwerb einer offiziellen Lizenz stellt eine **DIREKTE URHEBERRECHTSVERLETZUNG** dar und kann erhebliche zivil- und strafrechtliche Konsequenzen nach sich ziehen.
> 
> 3. **Kein Umgehungs- oder unbefugtes Verbreitungswerkzeug:**  
>    Dieses Tool bricht keine Lizenzschlüssel, umgeht keine Bezahlschranken und bietet keine unautorisierte kommerzielle Distribution an.
> 
> 4. **Nutzerverantwortung und offizielle Lizenzpflicht:**  
>    Jeder Nutzer trägt die **alleinige und persönliche Verantwortung** für seine Handlungen und die Einhaltung geltender Urheberrechtsgesetze. Um Font Awesome Pro in Produktions- oder kommerziellen Umgebungen einzusetzen, muss eine offizielle Lizenz erworben werden:
>    - 🛒 **Offizielle Font Awesome Lizenz erwerben:** [fontawesome.com/plans](https://fontawesome.com/plans)
>    - 📜 **Offizielle Lizenzbedingungen:** [fontawesome.com/license](https://fontawesome.com/license)

---

## 📌 Inhaltsverzeichnis
- [Rechtliche Hinweise und Urheberrechtswarnung](#-rechtliche-hinweise-und-urheberrechtswarnung)
- [Ziele der Bildungsforschung](#-ziele-der-bildungsforschung)
- [Systemanforderungen](#-systemanforderungen)
- [Schnellinstallation](#-schnellinstallation)
- [Benutzerhandbuch](#-benutzerhandbuch)
  - [1. Interaktiver Assistent (Wizard)](#1-interaktiver-assistent-wizard)
  - [2. Mehrsprachige Nutzung (--lang)](#2-mehrsprachige-nutzung---lang)
  - [3. Live-Versionserkennung über GitHub (--list-versions)](#3-live-versionserkennung-über-github---list-versions)
  - [4. Befehlszeilenschnittstelle (CLI)](#4-befehlszeilenschnittstelle-cli)
  - [5. Simulationsmodus (--dry-run)](#5-simulationsmodus---dry-run)
  - [6. Integritätsprüfung (--verify)](#6-integritätsprüfung---verify)
  - [7. Reparatur fehlender/beschädigter Dateien (--repair)](#7-reparatur-fehlenderbeschädigter-dateien---repair)
- [Intelligente Entscheidungs-Engine & Datenintegrität](#-intelligente-entscheidungs-engine--datenintegrität)
- [Build-Profile (Free, Pro, Pro-Plus, Custom)](#-build-profile)
- [Isolierte Build-Verzeichnisarchitektur](#-isolierte-build-verzeichnisarchitektur)
- [Sichere Arbeitsbereichsbereinigung (--clean)](#-sichere-arbeitsbereichsbereinigung---clean)
- [GitHub Actions CI/CD-Integration](#-github-actions-cicd-integration)
- [Lizenzmodell](#-lizenzmodell)

---

## 🔬 Ziele der Bildungsforschung

Dieses Open-Source-Projekt untersucht folgende Methoden der modernen Softwaretechnik:

1. **Terminal-Internationalisierung (i18n):** Modulare JSON-Wörterbücher (`lang/*.json`) mit hierarchischer Ausweichlogik (Fallback) und Punkt-Notation-Interpolation.
2. **Robuster mehrschichtiger Web-Crawler:** Dynamische Versionserkennung über die GitHub-REST-API, HTML-Paginierung (`releases?page=N`) und Atom-Feeds (`releases.atom`) ohne Beschränkung durch API-Ratenbegrenzungen.
3. **HTTP-Range-Wiederaufnahme:** Zuverlässige Fortsetzung unterbrochener Übertragungen per `Range: bytes={pos}-`.
4. **Streaming-Prüfsummenvalidierung:** Speicheroptimierte Berechnung mit `hashlib.sha256()` in 1-MB-Datenblöcken ohne RAM-Überlastung.
5. **Fehlertolerantes atomares Staging:** Build-Generierung im isolierten Verzeichnis `build/.staging/`, um beschädigte Ausgaben bei unerwartetem Abbruch (`CTRL+C`) auszuschließen.
6. **Build-übergreifende Wiederverwendung:** Automatischer Abgleich bestehender Builds zur Vermeidung redundanter Downloads und Einsparung von 90–100 % der Bandbreite.

---

## 💻 Systemanforderungen

- **Python:** 3.10 oder neuer (Python 3.11 / 3.12 empfohlen)
- **Betriebssystem:** Windows, macOS oder Linux (plattformübergreifend)
- **Netzwerk:** Standard-HTTPS-Verbindung

---

## 🚀 Schnellinstallation

```bash
# Repository klonen
git clone https://github.com/user05-ioemlak/FaFaProFree.git
cd FaFaProFree

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

## 📖 Benutzerhandbuch

### 1. Interaktiver Assistent (Wizard)

Starten Sie das Skript ohne Parameter für den interaktiven Modus:

```bash
python fa_pro_v3.py
```

Der Assistent führt durch folgende Schritte:
1. **Sprache:** `[1] English`, `[2] Türkçe`, `[3] Русский`, `[4] Deutsch`
2. **Profil:** `[1] Free`, `[2] Pro`, `[3] Pro-Plus`, `[4] Custom`
3. **Version:** Live gefundene Releases (z. B. v7.3.1, v7.3.0, v6.7.2 LTS) oder alle Versionen durchsuchen
4. **Kategorien:** `[1] Standardpaket (CSS+JS+Fonts)`, `[2] Erweitertes Paket (+Sprites)`, `[3] Benutzerdefiniert`

---

### 2. Mehrsprachige Nutzung (`--lang`)

Die Sprache der Konsolenausgabe kann dynamisch angepasst werden:

```bash
# Deutsch
python fa_pro_v3.py --lang de --list-versions

# Englisch
python fa_pro_v3.py --lang en --list-versions

# Türkisch
python fa_pro_v3.py --lang tr --list-versions

# Russisch
python fa_pro_v3.py --lang ru --list-versions
```

---

### 3. Live-Versionserkennung über GitHub (`--list-versions`)

Automatisches Durchsuchen von `https://github.com/FortAwesome/Font-Awesome/releases?page=*` mit Zwischenspeicherung und CDN-Validierung:

```bash
# Alle erkannten Releases gruppiert nach Hauptversionen (v7, v6, v5) auflisten
python fa_pro_v3.py --list-versions

# Cache aktualisieren und CDN-Verfügbarkeit der Assets vorab prüfen
python fa_pro_v3.py --refresh-versions --list-versions --validate-cdn

# Paginierungstiefe anpassen (Standard: 3 Seiten)
python fa_pro_v3.py --list-versions --pages 5
```

---

### 4. Befehlszeilenschnittstelle (CLI)

Für Skriptautomatisierungen und CI/CD-Pipelines:

```bash
# Pro-Profil (CSS + Webfonts) nicht-interaktiv erstellen
python fa_pro_v3.py --version 7.3.1 --profile Pro --css --fonts --non-interactive

# Vollständiges Pro-Plus-Profil erstellen
python fa_pro_v3.py --version 7.3.1 --profile Pro-Plus --non-interactive

# Kostenloses offizielles Free-Paket erstellen
python fa_pro_v3.py --version 7.3.1 --profile Free --non-interactive

# Ausgabe als Release-Zip-Archiv verpacken
python fa_pro_v3.py --version 7.3.1 --profile Pro --archive --non-interactive
```

---

### 5. Simulationsmodus (`--dry-run`)

Prüfen Sie den Ausführungsplan ohne Schreib- oder Downloadvorgänge:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --dry-run
```

Beispielausgabe:
```text
  ✓ css/all.css                            → Wiederverwenden (Cache/Build)
  ✓ js/all.js                              → Wiederverwenden (Cache/Build)
  ↓ webfonts/fa-solid-900.woff2            → Herunterladen
  Plan: 0 übersprungen, 62 wiederverwendet, 1 heruntergeladen
```

---

### 6. Integritätsprüfung (`--verify`)

Kryptografische SHA-256-Prüfsummen und Verzeichnisstrukturen ohne Download validieren:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --verify
```

---

### 7. Reparatur fehlender/beschädigter Dateien (`--repair`)

Zielverzeichnis analysieren und selektiv nur beschädigte oder fehlende Dateien nachladen:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --repair
```

---

## ⚡ Intelligente Entscheidungs-Engine & Datenintegrität

```text
                 ┌──────────────────┐
                 │ Existiert Datei  │
                 │ auf Festplatte?  │
                 └────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │        JA         │
                └─────────┬─────────┘
                          │
                  SHA-256 Validierung
                          │
             ┌────────────┴────────────┐
             │                         │
        STIMMT ÜBEREIN            ABWEICHUNG
             │                         │
             ▼                         ▼
      DOWNLOAD ÜBERSPRINGEN     ERNEUTER DOWNLOAD
     (Bandbreite gespart)      (Datei beschädigt)
```

1. **Kryptografische Checksummen:** Dateien werden nicht allein anhand von Namen oder Größe validiert, sondern per SHA-256-Streaming-Abgleich verifiziert.
2. **Build-übergreifende Wiederverwendung:** 63 identische Dateien aus `v7.3.1-Pro` werden bei der Erstellung von `v7.3.1-Pro-Plus` wiederverwendet (über 92 % Bandbreitenersparnis).
3. **Atomare `.part`-Dateien:** Downloads erfolgen in temporäre `.part`-Dateien und werden erst nach vollständiger Hash-Bestätigung umbenannt.

---

## 🎛️ Build-Profile

Die Profile sind in [config/build_profiles.json](config/build_profiles.json) definiert:

| Profilname | Anzahl Schriftfamilien | Umfang |
| :--- | :---: | :--- |
| **Free** | 3 | Offizielle freie Stile: `Solid`, `Regular`, `Brands`. |
| **Pro** | 17 | Classic (`Solid`, `Regular`, `Light`, `Thin`), Duotone, Sharp und Brands. |
| **Pro-Plus** | 37 | Pro-Stile + 20 Spezialfamilien (`Chisel`, `Etch`, `Jelly`, `Mosaic`, `Pixel` usw.). |
| **Custom** | Variabel | Individuelle Zusammenstellung durch den Entwickler. |

---

## 📁 Isolierte Build-Verzeichnisarchitektur

Jedes Build-Ergebnis wird isoliert strukturiert:

```text
build/
└── v7.3.1-Pro-Plus/
    ├── css/
    ├── js/
    ├── webfonts/
    ├── LICENSE.txt          # Lizenz- und Urheberrechtshinweise Dritter
    ├── BUILD_INFO.json      # Metadaten zu Version, Profil und Zeitstempel
    ├── BUILD_REPORT.json    # Detaillierter Integritätsprüfbericht
    └── manifest.json        # Dateipfade, Byte-Größen und SHA-256-Hashes
```

---

## 🧹 Sichere Arbeitsbereichsbereinigung (`--clean`)

```bash
# Bereinigt build/ und temporäre Staging-Ordner
python fa_pro_v3.py --clean

# Bereinigt zusätzlich den lokalen .cache/
python fa_pro_v3.py --clean --clean-cache
```

---

## ⚙️ GitHub Actions CI/CD-Integration

Das Repository umfasst zwei automatisierte Workflows:
1. **`.github/workflows/build.yml`:** Automatisierte Validierungs- und Integritätstests bei Pushes und Pull Requests.
2. **`.github/workflows/release.yml`:** Erstellt und veröffentlicht Release-Zip-Pakete bei Erstellung eines Git-Tags (`v*`).

---

## 📄 Lizenzmodell

- **Automatisierungs-Tools und Quellcode:** Lizenziert unter der [MIT-Lizenz](LICENSE).
- **Font Awesome Assets:** Geistiges Eigentum von [Fonticons, Inc.](https://fontawesome.com) und unterliegen deren kommerziellen Lizenzbedingungen.
