# Upgrade plan — book-mobility-program-data

Score: 6/10 -> 7.5/10 — DiscoverEU stayed `open` past its deadline; otherwise solid contract/source tests, but no CI, lint drift and no policy-consistency checks.

## Backlog

- P0: Confirm the new GitHub Actions CI is green on the first push and keep it required.
- P1: DiscoverEU record hard-codes the autumn-2026 window; the next call needs a new adapter
  branch (and source ID) rather than editing dates in place.
- P1: Extract dates/coverage for the four generic sources instead of fixed `unknown` status.
- P1: Live-source monitoring (drift alerts) stays in the shared runtime; keep adapters pure.
- P2: Fill the PRODUCT.md acceptance-gate table only with evidence that exists (CI run link,
  replay report); do not mark gates passed without it.
- P2: Consider extracting the byte-identical `cli.py` shared by the sibling `book-*-data`
  products into one versioned package once a consumer exists (today each repo vendors it).

## Done in this pass

- Fixed: the DiscoverEU record was always emitted as `open`; captures at or after the
  15 Oct 2026 12:00 CEST deadline now emit `closed` (regression test in `tests/test_source.py`).
- Added `.github/workflows/ci.yml`: Python 3.10/3.12 matrix, `pip install -e ".[dev]"`,
  `ruff check .`, `pytest`, and a `contract`/`validate`/`demo` CLI smoke. Verified by
  replaying those steps in a clean Python 3.10 venv.
- Added `[project.optional-dependencies] dev`, pytest config (`pythonpath = src`) and an
  explicit ruff rule set (E4/E9/F/I/B/UP); fixed the resulting import-order/encode lint.
- Added `tests/test_policy.py`: `sources.json` ↔ `source*.json` ↔ schema category
  consistency, duplicate policy copies identical, https/no-query URLs, 6h minimum
  interval, `--source-id` traversal rejection, capture fail-closed without
  `SOLO_EMPIRE_ROOT`, CLI `validate` exit codes without echoing input, bad demo clock.
- README: documented the developer/CI commands and offline test boundary.
