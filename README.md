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

## Archival Release

Version 1.0.0 is preserved on GitHub and Zenodo:

- version DOI for the exact release: [10.5281/zenodo.21448555](https://doi.org/10.5281/zenodo.21448555);
- concept DOI for the continuing project: [10.5281/zenodo.21448554](https://doi.org/10.5281/zenodo.21448554);
- immutable GitHub snapshot: [`v1.0.0`](https://github.com/cammackj/numerical-architecture-divine-names/releases/tag/v1.0.0).

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
- `REPRODUCIBILITY.md` explains how to rebuild the paper and rerun the analyses.

A complete source-level rebuild was performed on July 19, 2026. The source lock,
artifact hashes, simulation checks, and PDF verification are recorded in
[`docs/REPRODUCIBILITY_VERIFICATION.md`](docs/REPRODUCIBILITY_VERIFICATION.md).
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

Citation metadata for version 1.0.0, including its version and concept DOIs, is
provided in [`CITATION.cff`](CITATION.cff).

The manuscript, figures, documentation, and the author's copyrightable data
contributions are licensed under CC BY 4.0. Python analysis code is licensed
under MIT. See [`LICENSE.md`](LICENSE.md) for the component boundaries and
[`NOTICE.md`](NOTICE.md) for third-party attribution.
