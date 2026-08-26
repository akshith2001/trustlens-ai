# Contributing to TrustLens AI

## Research integrity first

- Never tune against or overwrite the locked final-test artifacts.
- Keep synthetic evidence clearly separated from external validation.
- Report negative, null and contradictory findings.
- Do not introduce real personal, financial, medical or employment data.
- Treat cost ratios and thresholds as declared research assumptions.

## Development setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

Run both benchmark commands after changing models, metrics or data handling:

```bash
trustlens-benchmark
trustlens-benchmark-suite
```

Benchmark output changes must be explained in the pull request. Locked final
files must remain unchanged unless a new, independently defined study is being
created under a new artifact name and protocol.

## Pull requests

Include the motivation, methods affected, tests added, evidence changed,
limitations and any compatibility impact. Keep changes focused and use plain,
auditable Python over unnecessary abstraction.
