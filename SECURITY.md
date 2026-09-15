# Security Policy 🛡️

## Supported Versions

Only the latest active release branch of **FaFaProFree** receives security updates:

| Version | Supported          |
| ------- | ------------------ |
| 3.2.x   | :white_check_mark: |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :x:                |
| < 3.0   | :x:                |

---

## Reporting a Vulnerability

We take the security of this project seriously, especially regarding credential handling and integrity verification.

If you discover a security vulnerability (such as token leakage, credential exposure, or hash tampering bypass):

1. **Do NOT open a public issue.**
2. Report the vulnerability privately via GitHub Security Advisories:
   - Navigate to [Security Advisories](https://github.com/user05-ioemlak/FaFaProFree/security/advisories) and click **"New draft advisory"**.
3. Include:
   - Description of the vulnerability.
   - Steps to reproduce or proof-of-concept.
   - Potential impact.

We will acknowledge receipt within 48 hours and work with you on a patch before public disclosure.

---

## Security Practices in FaFaProFree

- **Streaming Cryptographic Hashing:** Uses `hashlib.sha256()` with 1 MB streaming chunks to guarantee file authenticity.
- **Automated Secret Redaction:** All logs in `logs/` automatically mask GitHub tokens, Font Awesome tokens, Bearer authorization headers, and password strings.
- **Fail-Safe Atomic Staging:** Writes are isolated under `build/.staging/` and promoted only after complete verification.
- **Automated Verification:** `scripts/verify_build.py` scans build directories for accidental credential leaks and regex patterns before marking builds as verified.
