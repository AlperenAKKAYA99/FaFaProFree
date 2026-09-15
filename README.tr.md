# FaFaProFree 🧪

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Türkçe](https://img.shields.io/badge/Language-T%C3%BCrk%C3%A7e-red.svg)](README.tr.md)
[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-green.svg)](README.ru.md)
[![Deutsch](https://img.shields.io/badge/Language-Deutsch-yellow.svg)](README.de.md)

<br/>

![FaFaProFree Türkçe Banner](assets/images/thumbnail_tr.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CI Build](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)](.github/workflows/build.yml)
[![Scope: Educational Research](https://img.shields.io/badge/Scope-Educational%20Research-red.svg)](#-yasal-lisanslama-ve-telif-hakkı-uyarısı)
[![Repository](https://img.shields.io/badge/GitHub-user05--ioemlak%2FFaFaProFree-orange.svg)](https://github.com/user05-ioemlak/FaFaProFree)

**Ağ İletişimi, CDN Mimarisi, Akıllı Varlık Senkronizasyonu ve Çok Dilli Build Laboratuvarı**

</div>

---

## ⚖️ Yasal Lisanslama ve Telif Hakkı Uyarısı

> [!CAUTION]
> ### ⚠️ ÇOK ÖNEMLİ HUKUKİ UYARI: TELİF HAKKI VE TİCARİ KULLANIM RİSKİ
> 
> 1. **Eğitim ve Akademik Araştırma Kapsamı:**  
>    Bu proje **tamamen eğitim, teknik araştırma ve CDN mimarisi inceleme** amacıyla geliştirilmiştir. Projenin amacı; modern web standartlarında HTTP Range tabanlı parça indirme, bellek dostu (streaming) SHA-256 kriptografik bütünlük denetimi, CI/CD hatlarında atomik staging derleme ve canlı GitHub sürüm tarama mekanizmalarını teknik olarak incelemektir.
> 
> 2. **Telif Hakkı İhlali Riski (Copyright Infringement):**  
>    **Font Awesome Pro**, [Fonticons, Inc.](https://fontawesome.com) şirketine ait ücretli, ticari ve fikri mülkiyet kanunlarıyla korunan tescilli bir yazılımdır. Font Awesome Pro varlıklarını (CSS, SVG, WOFF2, JS) resmi bir lisans satın almadan ticari web sitelerinde, kurumsal projelerde veya kamuya açık ortamlarda kullanmak **DOĞRUDAN TELİF HAKKI İHLALİDİR** ve tarafları ciddi cezai ve hukuki yaptırımlarla karşı karşıya bırakabilir.
> 
> 3. **Yetkisiz Dağıtım veya Lisans Atlama Değildir:**  
>    Bu proje, Font Awesome Pro varlıklarını yetkisiz veya ücretsiz dağıtan bir platform **değildir**. Proje kodları herhangi bir lisans anahtarını kırmaz, ödeme duvarını aşmaz veya tersine mühendislik yoluyla yetkisiz erişim sağlamaz.
> 
> 4. **Kullanıcı Sorumluluğu ve Resmi Lisans Zorunluluğu:**  
>    Bu otomasyon aracını kullanarak herhangi bir varlığı inceleyen veya derleyen her kullanıcı, kendi eylemlerinden ve yerel yasalarından **bizzat ve münhasıran sorumludur**. Canlı veya ticari projelerinizde Font Awesome Pro varlıklarını kullanabilmek için mutlaka resmi Font Awesome sitesinden yetkili bir lisans temin etmeniz zorunludur:
>    - 🛒 **Resmi Font Awesome Lisansı Satın Alın:** [fontawesome.com/plans](https://fontawesome.com/plans)
>    - 📜 **Resmi Lisans Koşulları:** [fontawesome.com/license](https://fontawesome.com/license)

---

## 📌 İçindekiler
- [Yasal Lisanslama ve Telif Hakkı Uyarısı](#-yasal-lisanslama-ve-telif-hakkı-uyarısı)
- [Projenin Eğitim ve Araştırma Amacı](#-projenin-eğitim-ve-araştırma-amacı)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Hızlı Kurulum](#-hızlı-kurulum)
- [Kullanım Rehberi](#-kullanım-rehberi)
  - [1. İnteraktif Mod (Sihirbaz)](#1-i̇nteraktif-mod-sihirbaz)
  - [2. Çok Dilli Kullanım (--lang)](#2-çok-dilli-kullanım---lang)
  - [3. Canlı GitHub Sürüm Keşfi (--list-versions)](#3-canlı-github-sürüm-keşfi---list-versions)
  - [4. Komut Satırı (CLI) Modu](#4-komut-satırı-cli-modu)
  - [5. Simülasyon Modu (--dry-run)](#5-simülasyon-modu---dry-run)
  - [6. Bütünlük Doğrulama Modu (--verify)](#6-bütünlük-doğrulama-modu---verify)
  - [7. Eksik ve Bozuk Dosya Onarımı (--repair)](#7-eksik-ve-bozuk-dosya-onarımı---repair)
- [Akıllı Karar Motoru ve Bütünlük Denetimi](#-akıllı-karar-motoru-ve-bütünlük-denetimi)
- [Build Profilleri (Free, Pro, Pro-Plus, Custom)](#-build-profilleri)
- [İzole Build Dizin Mimarisi](#-i̇zole-build-dizin-mimarisi)
- [Güvenli Temizlik Sistemi (--clean)](#-güvenli-temizlik-sistemi---clean)
- [GitHub Actions CI/CD Entegrasyonu](#-github-actions-cicd-entegrasyonu)
- [Lisanslama Modeli](#-lisanslama-modeli)

---

## 🔬 Projenin Eğitim ve Araştırma Amacı

Bu açık kaynaklı çalışma, yazılım mühendisliği ve ağ mimarisi alanında şu teknik konuları öğrenmek ve test etmek için inşa edilmiştir:

1. **Çok Dilli (i18n) Terminal Mimarisi:** CLI ve terminal uygulamalarında JSON tabanlı (`lang/*.json`), hiyerarşik geri çekilmeli (fallback) ve nokta notasyonlu uluslararasılaştırma.
2. **Dinamik Sürüm Tarama (Live Release Discovery):** GitHub REST API, HTML sayfalama (`releases?page=N`) ve Atom akışını birleştiren 4 katmanlı dayanıklı sürüm tarama motoru.
3. **HTTP Range Tabanlı Kesintisiz İndirme:** Ağ kesintilerinde soketin baştan açılması yerine `Range: bytes={pos}-` başlığıyla bayt bazlı indirmeye devam etme (resumption) mekanizması.
4. **Akışlı (Streaming) Kriptografik Doğrulama:** Dosyaların RAM'e tamamen yüklenmeden 1 MB'lık parçalar (`chunks`) halinde okunarak `hashlib.sha256()` ile işlenmesi.
5. **Fail-Safe Atomik Staging:** Olası bir hata veya kullanıcı kesintisinde (`CTRL+C`) yarım kalmış bozuk klasörler bırakmamak adına işlemlerin `.staging/` altında izole edilip doğrulandıktan sonra atomik olarak terfi ettirilmesi.
6. **Çapraz Build Varlık Paylaşımı:** Daha önce doğrulanmış yerel build'lerin envanterini tarayarak ortak dosyaların yeniden indirilmesini engelleyip bant genişliğini %90-100 oranında koruma.

---

## 💻 Sistem Gereksinimleri

- **Python:** 3.10 veya üzeri (Python 3.11 / 3.12 önerilir)
- **İşletim Sistemi:** Windows, macOS veya Linux (tamamen çapraz platform)
- **Ağ:** Standart HTTPS bağlantısı

---

## 🚀 Hızlı Kurulum

```bash
# Depoyu klonlayın
git clone https://github.com/user05-ioemlak/FaFaProFree.git
cd FaFaProFree

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

---

## 📖 Kullanım Rehberi

### 1. İnteraktif Mod (Sihirbaz)

Herhangi bir bayrak girmeden çalıştırıldığında kullanıcıyı adım adım yönlendiren güvenli sihirbaz ekranı açılır:

```bash
python fa_pro_v3.py
```

Sihirbaz sırasıyla şu kararları alır:
1. **Dil:** `[1] English`, `[2] Türkçe`, `[3] Русский`, `[4] Deutsch`
2. **Profil:** `[1] Free`, `[2] Pro`, `[3] Pro-Plus`, `[4] Custom`
3. **Sürüm:** Canlı taranan en güncel sürümler (örn: v7.3.1, v7.3.0, v6.7.2 LTS) veya tüm listeyi inceleme
4. **Kategori:** `[1] Standart (CSS+JS+Fonts)`, `[2] Genişletilmiş (+Sprites)`, `[3] Özel Seçim`

---

### 2. Çok Dilli Kullanım (`--lang`)

FaFaProFree terminal çıktıları 4 dilde anlık olarak değiştirilebilir:

```bash
# Türkçe arayüz
python fa_pro_v3.py --lang tr --list-versions

# İngilizce arayüz
python fa_pro_v3.py --lang en --list-versions

# Rusça arayüz
python fa_pro_v3.py --lang ru --list-versions

# Almanca arayüz
python fa_pro_v3.py --lang de --list-versions
```

---

### 3. Canlı GitHub Sürüm Keşfi (`--list-versions`)

Font Awesome'ın resmi GitHub deposundaki sürümleri (`https://github.com/FortAwesome/Font-Awesome/releases?page=*`) anlık olarak tarar, önbelleğe alır ve CDN kaynak uygunluğunu doğrular:

```bash
# Canlı taranan tüm sürümleri majör versiyon gruplarına (v7, v6, v5) göre listele
python fa_pro_v3.py --list-versions

# Önbelleği temizleyip GitHub'dan taze sürüm listesini çek ve CDN durumunu denetle
python fa_pro_v3.py --refresh-versions --list-versions --validate-cdn

# Taranacak sayfa derinliğini belirle (varsayılan: 3 sayfa)
python fa_pro_v3.py --list-versions --pages 5
```

---

### 4. Komut Satırı (CLI) Modu

CI/CD hatları ve betik otomasyonları için:

```bash
# Pro profilini derle (CSS + Webfonts)
python fa_pro_v3.py --version 7.3.1 --profile Pro --css --fonts --non-interactive

# Pro-Plus profilini derle
python fa_pro_v3.py --version 7.3.1 --profile Pro-Plus --non-interactive

# Tamamen ücretsiz resmi Free paketini derle
python fa_pro_v3.py --version 7.3.1 --profile Free --non-interactive

# Çıktıyı otomatik zip arşivi olarak paketle
python fa_pro_v3.py --version 7.3.1 --profile Pro --archive --non-interactive
```

---

### 5. Simülasyon Modu (`--dry-run`)

Hiçbir dosya indirmeden veya diske yazmadan karar motorunun planını görüntüler:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --dry-run
```

Çıktı örneği:
```text
  ✓ css/all.css                            → Yeniden Kullan (cache/build)
  ✓ js/all.js                              → Yeniden Kullan (cache/build)
  ↓ webfonts/fa-solid-900.woff2            → İndir
  Plan: 0 atla, 62 yeniden kullan, 1 indir
```

---

### 6. Bütünlük Doğrulama Modu (`--verify`)

İndirme yapmadan sadece mevcut derlemenin SHA-256 hash'lerini ve dosya bütünlüğünü test eder:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --verify
```

---

### 7. Eksik ve Bozuk Dosya Onarımı (`--repair`)

Hedef klasörü tarar; silinmiş, bozulmuş veya hash'i tutmayan dosyaları tespit ederek yalnızca arızalı olanları tekrar indirir:

```bash
python fa_pro_v3.py --version 7.3.1 --profile Pro --repair
```

---

## ⚡ Akıllı Karar Motoru ve Bütünlük Denetimi

```text
                 ┌─────────────────┐
                 │ Dosya Mevcut mu? │
                 └────────┬────────┘
                          │
                ┌─────────▼─────────┐
                │       EVET        │
                └─────────┬─────────┘
                          │
                  SHA-256 Doğrulama
                          │
             ┌────────────┴────────────┐
             │                         │
          EŞLEŞTİ                   FARKLI
             │                         │
             ▼                         ▼
      İNDİRMEYİ ATLA             YENİDEN İNDİR
     (Bant Tasarrufu)           (Bozuk / Değişmiş)
```

1. **Checksum Karşılaştırması:** Bir dosya hedef klasörde mevcut olsa dahi, akışlı SHA-256 hash'i doğrulanmadan asla güvenilir kabul edilmez.
2. **Çapraz Build Paylaşımı:** Örneğin `v7.3.1-Pro` derlemesindeki 63 ortak dosya, `v7.3.1-Pro-Plus` oluşturulurken internetten tekrar indirilmez; yerel olarak kopyalanır ve doğrulanır (%92+ bant tasarrufu).
3. **Atomik `.part` Koruması:** İndirmeler önce `.part` uzantısıyla yazılır. Ağ kesilirse yarım dosya çıktıya karışmaz. Range resumption ile kaldığı bayttan devam eder.

---

## 🎛️ Build Profilleri

Profil tanımları [config/build_profiles.json](config/build_profiles.json) dosyasında yapılandırılmıştır:

| Profil Adı | Stil Aile Sayısı | Kapsam |
| :--- | :---: | :--- |
| **Free** | 3 | Resmi ücretsiz stiller: `Solid`, `Regular`, `Brands`. |
| **Pro** | 17 | Classic (`Solid`, `Regular`, `Light`, `Thin`), Duotone, Sharp ve Brands. |
| **Pro-Plus** | 37 | Pro stilleri + 20 ek aile (`Chisel`, `Etch`, `Jelly`, `Mosaic`, `Pixel`, `Slab`, `Utility`, `Whiteboard` vb.). |
| **Custom** | Özel | Geliştirici tarafından seçilen bağımsız aileler. |

---

## 📁 İzole Build Dizin Mimarisi

Her build izole bir klasörde üretilir:

```text
build/
└── v7.3.1-Pro-Plus/
    ├── css/
    ├── js/
    ├── webfonts/
    ├── LICENSE.txt          # Lisans ve telif bildirimleri
    ├── BUILD_INFO.json      # Sürüm, profil, zaman damgası
    ├── BUILD_REPORT.json    # Doğrulama istatistikleri
    └── manifest.json        # Dosya listesi, boyutlar ve SHA-256 hash'leri
```

---

## 🧹 Güvenli Temizlik Sistemi (`--clean`)

```bash
# build/ çıktılarını ve geçici staging klasörlerini temizler
python fa_pro_v3.py --clean

# .cache/ klasörünü de sıfırlamak için
python fa_pro_v3.py --clean --clean-cache
```

---

## ⚙️ GitHub Actions CI/CD Entegrasyonu

Proje deposunda 2 adet otomatik GitHub Actions iş akışı bulunmaktadır:
1. **`.github/workflows/build.yml`:** Her kod itildiğinde (push/PR) test çalıştırır, sanal ortamda derleme ve bütünlük doğrulamasını test eder.
2. **`.github/workflows/release.yml`:** Yeni bir Git etiketi (`v*`) verildiğinde otomatik zip arşivi oluşturup GitHub Releases sayfasına yükler.

---

## 📄 Lisanslama Modeli

- **Derleme ve Otomasyon Araçları (Kod Tabanı):** [MIT Lisansı](LICENSE) altında sunulmaktadır.
- **Font Awesome Varlıkları:** [Fonticons, Inc.](https://fontawesome.com) mülkiyetindedir ve ticari projelerde resmi ticari lisans gerektirir.
