# AI Invoice Processing System

Extract invoice text and fields, validate financial arithmetic, correct fields, explicitly review the result, and export JSON or CSV.

**Implemented local portfolio application**, with source, persistent storage, runnable API, synthetic examples, automated tests, and a demo script. The interactive API at `/docs` is the included client. This repository does not claim a production deployment, a native mobile client, or previously measured customer usage.

## Features

- UTF-8 TXT/Markdown, text PDFs, and PNG/JPEG images.
- Real image OCR: Apple Vision on macOS, Tesseract on Linux.
- Local-model extraction constrained by an invoice JSON schema.
- Decimal arithmetic with explicit half-up rounding, required-field checks, line checks, subtotal/tax/total validation.
- Duplicate-content detection, optimistic version checks, persisted corrections and review status.
- Export is blocked until review succeeds; CSV textual fields are protected against spreadsheet formula interpretation.
- Failed/incomplete model extraction remains visible and can be corrected manually.

## Install and run

Use Python 3.9–3.12 (developed/tested here with 3.9.6; Python 3.11 is recommended for a new environment).

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

For AI operations, install [Ollama](https://ollama.com/download), start its local server, and pull a model:

```sh
ollama serve
# In a second terminal:
ollama pull qwen2.5:1.5b
export AI_MODEL=qwen2.5:1.5b
./scripts/start.sh
```

Open [interactive API docs](http://127.0.0.1:8102/docs). The default service port is 8102; override with `PORT`. Keep one API worker bound to localhost. This single-user application has no authentication and stores development data in ignored `data/`; do not expose it as a multi-user public service.

Configuration is read from environment variables. `.env.example` documents them but is not automatically executed or loaded. `OLLAMA_BASE_URL` defaults to `http://127.0.0.1:11434`; `AI_MODEL` selects the installed local model. Providers run on the backend computer; the initial model downloads need internet. No paid API credentials are required.

`requirements.txt` contains portable version ranges; `requirements-lock.txt`, when present, records the exact versions installed in this macOS development environment.

## Walkthrough

1. Multipart upload a file to `POST /invoices`.
2. Inspect the returned `source_text`, `data`, `issues`, `status`, `id`, and `version`.
3. Correct the complete structured record with `PATCH /invoices/{id}` and `{"version":1,"data":...}`. A full example is in `examples/corrected.json`.
4. Resolve all validation issues. Call `POST /invoices/{id}/review` with the current version.
5. Download `/invoices/{id}/export?format=json` or `?format=csv`.
6. Editing a reviewed record returns it to `needs_review`; stale versions return 409.
7. List and reopen persisted invoices with `GET /invoices` and `GET /invoices/{id}`.

With the API running, execute the synthetic walkthrough in another terminal:

```sh
source .venv/bin/activate
python scripts/demo.py
```

Use `--url http://127.0.0.1:PORT` to target a different local port. `/docs` exposes the full request and response schemas for manual testing.

## Tests

```sh
python -m pytest -q
```

The current automated suite has **6 passing tests** covering workflow behaviour and important failures. Tests inject provider doubles to remain deterministic; `VERIFICATION.md` separately records real-provider checks. Automated CI runs the deterministic suite without model credentials. The synthetic demo is not a production accuracy benchmark.

## OCR prerequisites and sample

On macOS, install Xcode Command Line Tools (`xcode-select --install`) if Swift is unavailable. The shipped `native/ocr.swift` uses Vision; the app compiles it once into ignored `.tools/ocr`. On Linux install the `tesseract` executable and English language data. No system package installation is performed automatically.

`examples/invoice.png` and `examples/invoice.txt` contain the same entirely synthetic invoice. The expected reviewed data is `examples/corrected.json`. A missing model produces a persisted `extraction_failed` record which supports the same manual correction/review flow.

Modules: `app/main.py` contains parsing, OCR, schema, deterministic validation, versioned review, and export. `app/runtime.py` contains persistence and the local-model adapter.

## Operational boundaries

- 10 MB uploads; PDFs up to 30 pages; images up to 16 megapixels; extracted text up to 24,000 characters. Scanned PDFs must be supplied as separate page images for OCR.
- Supported currency codes: INR, USD, EUR, GBP. Calculations use two-decimal monetary rounding. Discounts, multi-currency invoices, complex tax rules and accounting-system integrations are outside this local implementation.
- OCR and LLM extraction can be incomplete or wrong. Null/missing fields and arithmetic mismatches block review. Human review is required even when checks pass.
- Extracted text and structured records are saved locally; original uploads are not retained. SHA-256 content IDs detect exact duplicate uploads, not all semantically duplicate invoices.
- No payment execution or claim of invoice legitimacy is made.

## Technical references

- [FastAPI](https://fastapi.tiangolo.com/)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Apple Vision](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [Tesseract command line](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html)
