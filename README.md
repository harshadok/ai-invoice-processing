# AI Invoice Processing System

**Status: Planning / documentation only.** This repository currently contains a project specification and implementation roadmap. No working application, provider integration, deployment, or measured results are included yet.

A personal learning project by [Harshad Odakkal](https://github.com/harshadok), building on professional Flutter and mobile engineering experience while transitioning toward AI/mobile engineering.

## Problem and goal

Convert invoice images or PDFs into structured records that users can validate before exporting.

## Skills to practise

- Optical Character Recognition (OCR)
- Structured outputs
- Data validation
- Document extraction
- Human review workflows

## Planned end-to-end workflow

1. Upload a synthetic invoice image or PDF.
2. Extract text using an OCR adapter while preserving relevant source references.
3. Map extracted text into a defined invoice schema.
4. Validate required fields, types, dates, currency, and line-item arithmetic.
5. Flag missing or inconsistent values for human review without inventing data.
6. Save the reviewed result and export structured JSON or CSV.

## Proposed architecture

Flutter upload and review client; Python API service; OCR adapter; schema-constrained LLM extraction adapter; validation layer; relational storage.

The stack is a design proposal. Specific providers, libraries, model versions, and database products will be selected and documented during implementation.

## Planned API surface

- `POST /invoices` — upload an invoice
- `GET /invoices/{id}` — retrieve extraction and validation findings
- `PATCH /invoices/{id}` — submit reviewed field corrections
- `GET /invoices/{id}/export` — export a reviewed record

These endpoints are proposed contracts; they are not implemented.

## Core data model

Invoice(vendor, invoice_number, invoice_date, currency, line_items, subtotal, tax, total); ValidationIssue(field, rule, message); Review(status, corrections).

## Flutter/mobile experience

Camera or file upload, side-by-side source and extracted fields, validation warnings, correction form, and export action.

## Evaluation and acceptance plan

- [ ] Measure per-field extraction accuracy against synthetic labelled invoices.
- [ ] Validate totals using decimal arithmetic and explicit rounding rules.
- [ ] Test missing fields, multiple currencies, duplicate invoices, and malformed dates.
- [ ] Confirm invalid or incomplete records cannot silently pass as reviewed.
- [ ] Compare OCR errors with extraction errors to identify the failing stage.

No accuracy, latency, cost, or reliability results have been measured. Results will be added only after reproducible runs.

## Implementation roadmap

- [ ] **Milestone 1:** Define the invoice schema and build synthetic invoice fixtures.
- [ ] **Milestone 2:** Add OCR text extraction and inspect raw output.
- [ ] **Milestone 3:** Add structured extraction with missing-value handling.
- [ ] **Milestone 4:** Implement deterministic validation and a human correction flow.
- [ ] **Milestone 5:** Build the Flutter review interface and publish field-level evaluation results.

## Planned demonstration

Process a synthetic invoice with an intentionally incorrect total, show the validation issue, correct it, and export the reviewed JSON.

## Data and operational boundaries

Use synthetic financial documents for demonstrations. Do not execute payment actions; extraction and review do not establish that an invoice is legitimate.

## Getting started today

1. Read the proposed workflow and choose the first milestone.
2. Decide on providers and local development tools; record those decisions before implementation.
3. Add application code and a reproducible setup guide as the first milestone is built.
4. Use synthetic or public test data and keep credentials outside version control.

**There is no runnable quick start yet.** Installation and run commands will be added when code exists.

## Suggested future layout

```text
apps/mobile/        # Planned Flutter client
services/api/       # Planned application API
evals/              # Planned fixtures and evaluation runs
docs/               # Architecture decisions and demonstration notes
```

These directories describe the intended structure and have not been implemented.

## Portfolio context

This is an independent planned portfolio project, not client work or a production deployment. Its current scope is documentation; update the status and roadmap as working milestones are completed.
