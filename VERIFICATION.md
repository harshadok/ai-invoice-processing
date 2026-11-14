# Verification — 14 November 2026

## Automated checks

- Python backend suite: **6 passed** in the local development environment.
- `python -m pip check`: no broken requirements for the installed project environment.
- Deterministic tests isolate provider failures using doubles; the real-provider checks below are separate evidence.
- GitHub Actions runs the backend suite on Python 3.11 without requiring model weights or credentials.

## Real-provider checks

- Apple Vision OCR read the generated synthetic invoice image, including invoice number and total.
- Real Ollama Qwen2.5 1.5B extracted the image's vendor, date, currency, line item, subtotal, tax and total; deterministic validation reported no issues.
- Explicit review and JSON export were exercised on a synthetic invoice. Missing fields from an earlier 0.5B run were correctly blocked until human correction.
- No general extraction-accuracy percentage is claimed.

## Scope

This is a runnable single-user local portfolio implementation. Smoke checks on synthetic/public data are not a production-readiness claim, a general quality benchmark, or proof that an AI output is always correct. See README for supported formats, runtime dependencies and operational boundaries.
