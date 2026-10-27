# Testing guide

## What exists

| Layer | What it tests | How to run | Status in this release |
|---|---|---|---|
| Script tests | The five bundled scripts against fixtures, including false-positive controls | `python3 tests/run_tests.py` | Run; results in `docs/IMPLEMENTATION_REPORT.md` |
| Package validation | SKILL.md metadata and structure | `python3 echocraft/scripts/validate_skill.py echocraft` | Run |
| Official validator | Same, via the reference library | `pip install skills-ref` then `skills-ref validate echocraft` (or `python3 -c "from pathlib import Path; from skills_ref import validate; print(validate(Path('echocraft')))"`) | Run once, in the build environment |
| Secret scan | Package contains no credential patterns or private identifiers | `python3 echocraft/scripts/scan_secrets.py . --fail-on low` | Run |
| Documentation links | Relative links and repo paths in all markdown files exist | `python3 tests/check_links.py` | Run |
| Agent behaviour | Whether an agent follows the skill | `tests/MANUAL_EVALUATION.md` | **Not run** |

## Requirements
Python 3.8 or newer. No third-party packages for the scripts or tests. `skills-ref` is optional and only for the independent validator.

## Layout
- `tests/fixtures/` - small invented projects and tables. Contain no real data. `tidewrite/` is a fictional app with deliberate defects used in `examples/`.
- `tests/expected-findings/*.json` - one file per case: script, arguments, expected exit code, rule ids that must and must not appear, numeric assertions.
- `tests/run_tests.py` - runs every case; `-v` prints commands; an argument filters by name.

## Adding a case
1. Create a fixture under `tests/fixtures/<name>/`.
2. Add `tests/expected-findings/<name>.json` with `script`, `args` (use `{fixtures}`, `{skill}`, `{root}`, `{tmp}`), `expect_exit`, `must_include`, `must_not_include`, optional `asserts` (`eq`, `gte`, `lte`, `len_gte`, `len_eq`).
3. Add a *control* that must not trigger the rule, not only a case that must.
4. Run `python3 tests/run_tests.py`.

## Secrets in tests
The secret-scanner test builds fake credentials at run time in a temp directory so the repository never contains secret-shaped strings. The test also asserts those strings are never echoed in scanner output.

## Known limits
Scripts are regex-level heuristics. They miss minified code, dynamically built URLs, server configuration and runtime behaviour, and they can flag harmless code. They are aids to reading the source, not substitutes for a browser run, an accessibility audit or a security review.
