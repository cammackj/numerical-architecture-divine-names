# The Numerical Architecture of the Divine Names and the Canonical Tanakh

This repository accompanies Joshua Cammack's research manuscript on gematria,
base-12 palindromes, divine names and titles, and the numerical structure of the
canonical Tanakh.

> **Status:** living research record. The `main` branch may change as additional
> patterns are tested or existing interpretations are refined. Numbered GitHub
> and Zenodo releases are preserved as immutable archival snapshots.

The project began with an initial draft in December 2025. The current manuscript
is the substantially revised July 2026 version. Its author is
[Joshua Cammack](https://orcid.org/0009-0006-0482-4893), ORCID
`0009-0006-0482-4893`.

## Archival Releases

Version 1.1.0 adds the bounded Psalm 22 investigation and the complete
two-digit base-12 repdigit ladder:

- concept DOI for the continuing project: [10.5281/zenodo.21448554](https://doi.org/10.5281/zenodo.21448554);
- immutable GitHub snapshot: [`v1.1.0`](https://github.com/cammackj/numerical-architecture-divine-names/releases/tag/v1.1.0).

The version-specific DOI for 1.1.0 will be added after Zenodo creates the new
archive. Version 1.0.0 remains preserved under DOI
[10.5281/zenodo.21448555](https://doi.org/10.5281/zenodo.21448555) and GitHub
tag [`v1.0.0`](https://github.com/cammackj/numerical-architecture-divine-names/releases/tag/v1.0.0).

## Manuscript

The current reader-facing paper is available as
[`Numerical_Architecture_of_the_Divine_Names.pdf`](Numerical_Architecture_of_the_Divine_Names.pdf).
The complete XeLaTeX source is in [`tex/`](tex/).

The paper presents exact calculations, finite enumerations, matched controls,
sensitivity analyses, and exploratory findings while leaving their theological
meaning for the reader to consider. The technical appendices and repository
records distinguish arithmetic results from interpretive conclusions.

## Repository Contents

- `tex/` contains the manuscript source and figures.
- `scripts/` contains the calculation, enumeration, control, and sensitivity code.
- `data/` contains the source registry and machine-readable results.
- `docs/` contains frozen protocols and generated technical reports.
- `research/` contains only the two post-publication analyses admitted to
  version 1.1.0 and their complete generated tables.
- `REPRODUCIBILITY.md` explains how to rebuild the paper and rerun the analyses.

A complete source-level rebuild of the original release was performed on July
19, 2026. The two version 1.1.0 additions and final 95-page PDF were verified on
July 20, 2026. The new verification is recorded in
[`docs/V1_1_REPRODUCIBILITY_VERIFICATION.md`](docs/V1_1_REPRODUCIBILITY_VERIFICATION.md),
while [`docs/REPRODUCIBILITY_VERIFICATION.md`](docs/REPRODUCIBILITY_VERIFICATION.md)
preserves the version 1.0.0 baseline.
The final pre-release citation, source-link, and cross-manuscript consistency
pass is recorded in [`docs/PUBLICATION_AUDIT.md`](docs/PUBLICATION_AUDIT.md).

The `main` branch remains the living research record after publication. Numbered
GitHub and Zenodo releases are immutable snapshots governed by
[`docs/UPDATE_POLICY.md`](docs/UPDATE_POLICY.md), and reader-visible changes are
recorded in [`CHANGELOG.md`](CHANGELOG.md).

The original Word document, internal editorial notes, referee working papers,
and revision planning files are intentionally excluded from this public record.

## Build the Paper

The manuscript requires XeLaTeX or LuaLaTeX because it contains Hebrew and
Unicode mathematical notation.

```powershell
Set-Location tex
xelatex main.tex
xelatex main.tex
```

The resulting `main.pdf` should match the content of the PDF at the repository
root, subject to ordinary PDF metadata differences.

## Reuse and Citation

Citation metadata for version 1.1.0 is provided in
[`CITATION.cff`](CITATION.cff). Until Zenodo supplies the new version-specific
DOI, it uses the all-version concept DOI.

The manuscript, figures, documentation, and the author's copyrightable data
contributions are licensed under CC BY 4.0. Python analysis code is licensed
under MIT. See [`LICENSE.md`](LICENSE.md) for the component boundaries and
[`NOTICE.md`](NOTICE.md) for third-party attribution.
