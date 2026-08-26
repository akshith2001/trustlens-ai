# Changelog

All notable research-software changes are documented here.

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
