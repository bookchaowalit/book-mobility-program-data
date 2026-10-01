# Upgrade plan — book-mobility-program-data

Score: **7.5/10** (6 -> 7.5 in pass 1; unchanged in passes 2-4). Offline contract, adapters and CLI have offline tests and lint wired into CI (runs not yet confirmed green, see P0); live capture, source permission and consumers remain unverified by design. Before pass 1: discoverEU stayed `open` past its deadline; otherwise solid contract/source tests, but no CI, lint drift and no policy-consistency checks.

## Backlog

- P0: Confirm GitHub Actions `CI` is green on `claude/untitled-session-bhlj06`. The branch is pushed, but every run so far ended within ~5 s with no job logs (runner never started, not a test failure); check the account's Actions/billing settings, then re-run.
- P1: DiscoverEU record hard-codes the autumn-2026 window; the next call needs a new adapter
  branch (and source ID) rather than editing dates in place.
- P1: Extract dates/coverage for the four generic sources instead of fixed `unknown` status.
- P1: Live-source monitoring (drift alerts) stays in the shared runtime; keep adapters pure.
- P2: Fill the PRODUCT.md acceptance-gate table only with evidence that exists (CI run link,
  replay report); do not mark gates passed without it.
- P2: Consider extracting the byte-identical `cli.py` shared by the sibling `book-*-data`
  products into one versioned package once a consumer exists (today each repo vendors it).

## Done in this pass (pass 1)

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

## Done in this pass (pass 2)

- Bug: DiscoverEU was emitted as `open` for captures before the application window opens
  (1 Oct 2026 12:00 CEST, as documented in the README); a fresh pre-opening capture passed
  `--open-only`. It is now `open` only in [opening, deadline) and `closed` otherwise;
  boundary tests added, README documents it.
- Remaining P1s (next DiscoverEU call, dates for generic sources) need reviewed live page
  content; not attempted offline. `source.json` stays content-identical to
  `source-discovereu-autumn-2026.json` (asserted by `tests/test_policy.py`).

## Done in this pass (pass 3)

- Score unchanged; shared-CLI hardening only.
- Shared `cli.py` (same edit in all 13 sibling copies): `validate` now rejects NaN, ±Infinity and overflowing literals such as `1e400` (Python's json turns them into non-finite floats that JSON Schema `number` accepted); `timestamp` normalises fractional seconds so Python 3.10 accepts the same RFC3339 values as 3.11+ (it rejected e.g. `.1Z`) and only ASCII digits match; a trailing-dot `example.org.` host can no longer be claimed `live`.
- `tests/test_shared_cli.py` (byte-identical in all 13 repos) pins this repo's `cli.py` sha256 (three variants: base, +`contract --version`, +benefit availability) so a one-repo edit fails CI, and covers the fixes above across UTC/+07:00/-04:00 offsets. To change `cli.py`: edit every copy of the variant, then update `CLI_SHA256` in all 13 copies of the test.
- Not done (needs a reviewed live capture, so left blocked): stronger drift markers and any page-phrase extraction; no page phrases were invented.

## Done in this pass (pass 4: edge cases)

- Shared `cli.py` (all 13 copies, pins updated in `tests/test_shared_cli.py`):
  - `validate` accepted `" "` or a lone U+200B/BOM/soft hyphen as `id`,
    `title`, `provider` or `eligibility_text` (schema `minLength: 1` counts
    invisible characters); these are now rejected as blank.
  - Record ids that differ only by invisible characters or surrounding
    whitespace (`"x"` vs `"​x "`) are now reported as duplicates.
  - `demo --query` compared raw `casefold()` strings, so Thai SARA AM (`ำ`)
    did not match NIKHAHIT + SARA AA (either mark order), Thai digits did not
    match ASCII (`๒๕๖๙` vs `2569`), and full-width Latin (`ＵＫ`) or a stray
    zero-width space never matched; both sides are now NFKC-folded.
  - Verified: new `TextNormalisationTest` (all cases fail on the old code);
    full suite on Python 3.10 and 3.11; ruff 0.15.8 + 0.16.9.
