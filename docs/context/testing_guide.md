# Testing Guide

## Test Framework
- **pytest** (Implicitly used for the `tests/` directory).

## Test Directory
- `tests/`

## Targeted Test Commands
```bash
pytest tests/test_text_splitter.py
```

## Full Test Commands
```bash
pytest tests/
```

## Known Test Gaps
The `README.md` explicitly states: *"No tests, minimal error handling - you've been warned"*.
- Currently, only the `text_splitter.py` has test coverage.
- The entire pipeline orchestration, vector retrieval, LLM interaction, and PDF parsing lack automated tests.
- High reliance on manual end-to-end testing and evaluation datasets.

## Strategy for New Features
When adding or modifying features, implement unit tests for deterministic functions (like parsing, text splitting) and use the `data/test_set/` for end-to-end integration manual checks.
