# Version 1.0.0

Release date: July 19, 2026

This is the first archival release of *The Numerical Architecture of the Divine
Names and the Canonical Tanakh* and its reproducibility record. The project began
with an initial manuscript draft in December 2025 and was substantially revised
in July 2026.

## Included in This Release

- the 91-page reader-facing manuscript and complete XeLaTeX source;
- exact registries and machine-readable analytical results;
- scripts for the arithmetic audits, finite enumerations, sensitivity analyses,
  matched controls, and robustness tests;
- frozen protocols and reports distinguishing confirmatory, robustness, and
  exploratory work;
- a source lock to Open Scriptures MorphHB commit
  `3d15126fb1ef74867fc1434be1942e837932691f`;
- the final publication and reproducibility audit records.

## Verification

The complete source-dependent analysis was rebuilt on July 19, 2026. Every
declared analysis completed successfully, and the manuscript rebuilt to 91 pages
without LaTeX warnings or layout errors. Details and artifact hashes are in
`docs/REPRODUCIBILITY_VERIFICATION.md`.

## Scope

The paper presents reproducible numerical observations and their evidential
limits. It does not ask the calculations alone to decide their theological
meaning; that judgment remains with the reader.

## Licensing

The manuscript, documentation, figures, and the author's copyrightable data
contributions are licensed under CC BY 4.0. Python analysis code is licensed
under MIT. Third-party source terms and attribution are recorded in `NOTICE.md`.

## Citation and Future Versions

Citation metadata is provided in `CITATION.cff`. Version 1.0.0 will remain an
immutable archival snapshot. Later corrections or new discoveries will be
released as new numbered versions under `docs/UPDATE_POLICY.md`. Version and
concept DOIs will be added to the live repository after Zenodo archives the
GitHub release.
