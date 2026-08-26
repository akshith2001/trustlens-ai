# Changelog

All notable research-software changes are documented here.

## 0.4.0 - 2026-08-26

### Added

- Independent five-fold credit-domain validation on the CC0 FICO HELOC cleaned
  dataset, with reproducible JSON and Markdown evidence.
- API-key-authenticated FastAPI governance, monitoring and registry endpoints.
- Checksum-backed model registry, append-only experiment ledger and bounded
  aggregate runtime monitoring with drift/OOD alert rules.
- Hardened Docker Compose deployment and container build/run/SBOM CI workflow.

### Changed

- Raise enforced statement coverage from 75% to 90%.
- Consolidate current dependency updates, including GitHub Actions and developer
  tooling major versions.

### Limitations

- The independent dataset's collection period is undocumented, so the result is
  not presented as contemporary or prospective validation.
- Monitoring infrastructure is implemented and tested but has no live-traffic
  evidence or external alert-delivery integration.

## 0.3.1 - 2026-08-26

### Security and CI

- Require setuptools 83 or newer to resolve PYSEC-2026-3447 in CI.
- Upgrade checkout, Python setup and CodeQL actions to Node 24-compatible major
  versions.

## 0.3.0 - 2026-08-26

### Added

- Cross-domain public reference benchmark using two packaged, real datasets.
- Four-model comparison with discrimination, calibration, shift and proxy-slice
  diagnostics.
- Reproducible JSON and Markdown reference-benchmark artifacts.
- Container deployment, health check, Dependabot and contribution templates.

### Clarified

- Reference results validate benchmark mechanics across domains; they are not
  external credit-domain validation or evidence for operational use.
- Proxy feature slices are diagnostics, not protected-attribute fairness audits.

### Preserved

- Existing locked final-test metrics, uncertainty and error-analysis artifacts.

## 0.2.0 - 2026-08-26

### Added

- Versioned development benchmark with deterministic model ranking.
- Controlled synthetic robustness suite with bootstrap intervals, paired cost
  comparisons and covariate-shift stress tests.
- Machine-readable benchmark artifacts and generated Markdown report.
- Locked dataset SHA-256 verification.
- Privacy-aware, hash-chained governance audit records.
- CI benchmark smoke tests and repository contribution/security guidance.

### Changed

- Reproducibility documentation now distinguishes development, locked final and
  controlled synthetic evidence.
- Removed brittle hard-coded test counts from report generators.

### Preserved

- Existing locked final-test metrics, uncertainty and error-analysis artifacts.

## 0.1.0 - 2026-08-22

- Initial human-governed credit-risk research prototype.
