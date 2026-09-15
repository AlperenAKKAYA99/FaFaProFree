# Contributing to FaFaProFree 🤝

Thank you for your interest in contributing to **FaFaProFree**! We welcome bug reports, feature suggestions, documentation enhancements, and multilingual translations.

---

## 📜 Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all members of the community with respect and empathy.

---

## 🛠️ Development Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/user05-ioemlak/FaFaProFree.git
   cd FaFaProFree
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Unit Tests:**
   ```bash
   python -m unittest discover -s tests
   ```

---

## 🌐 Adding or Updating Languages (i18n)

FaFaProFree supports 4 primary languages:
- `en`: English (`lang/en.json`)
- `tr`: Türkçe (`lang/tr.json`)
- `ru`: Русский (`lang/ru.json`)
- `de`: Deutsch (`lang/de.json`)

When adding new translation keys or modifying existing ones:
1. Update `lang/en.json` first as the baseline truth.
2. Mirror the new keys in `lang/tr.json`, `lang/ru.json`, and `lang/de.json`.
3. Verify test integrity: `python -m unittest tests/test_i18n.py`.

---

## 🔒 Security & Credentials

- **Zero-Credential Policy:** NEVER commit tokens (`ghp_*`, `fa_*`), API keys, passwords, or personal credentials.
- The build logger automatically masks tokens matching security patterns. Ensure your code does not bypass this protection.
- For vulnerability reports, please refer to [SECURITY.md](SECURITY.md).

---

## 📥 Pull Request Guidelines

1. **Branch Naming:** Use clear branch names like `feat/add-new-profile`, `fix/cdn-status-parsing`, `docs/update-readme`.
2. **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat: add retry backoff`, `fix: handle cp1254 encoding on windows`).
3. **Automated Verification:** Run `python fa_pro_v3.py --verify` and `python -m unittest discover -s tests` before submitting your PR.
