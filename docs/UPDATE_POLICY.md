# Version and Update Policy

## Purpose

This project is expected to continue developing after its first archival
release. New names, cross-patterns, source corrections, controls, or
interpretive refinements may appear. The release process must allow that work
without silently changing an artifact that has already been cited.

The governing distinction is simple:

- the `main` branch is the living research record;
- every numbered GitHub and Zenodo release is an immutable snapshot.

## Version Numbers

The project uses semantic version numbers in the form `MAJOR.MINOR.PATCH`.

### Patch releases: `1.0.1`, `1.0.2`, and so on

Use a patch release for corrections that do not alter the admitted Hebrew
forms, numerical results, corpus membership, or substantive interpretation.
Examples include typographical corrections, repaired source links, citation
metadata, and layout improvements.

### Minor releases: `1.1.0`, `1.2.0`, and so on

Use a minor release for substantive additions that preserve the declared core
method. Examples include newly tested names or titles, additional exploratory
patterns, new controls, new appendices, or a meaningful expansion of the
discussion. The release notes must identify which findings are new and whether
any earlier assessment changed.

### Major releases: `2.0.0`, `3.0.0`, and so on

Use a major release when the primary corpus, arithmetic rules, value systems,
evidence hierarchy, or central conclusions change enough that readers should
not treat the new manuscript as a direct continuation of the previous one.

## Required Checks for Every Release

Each release must include:

1. the reader-facing PDF;
2. the complete TeX source needed to rebuild it;
3. the source registries, generated result tables, and analysis scripts;
4. updated citation metadata and this changelog;
5. release notes describing every substantive change;
6. a clean two-pass PDF build and visual inspection;
7. a citation, source-link, arithmetic, and cross-section consistency check;
8. rerun analyses whenever their code or numerical inputs changed.

Source-only or prose-only corrections do not require rerunning an unaffected
simulation, but the release record must say why it was unaffected.

## GitHub and Zenodo

When the connected public GitHub repository is enabled in Zenodo, a new GitHub
release is archived as a new Zenodo version. Each archived version receives a
version-specific DOI, and Zenodo also provides a concept DOI representing the
project across all versions.

- Cite the version DOI when reproducibility requires the exact files used.
- Cite the concept DOI when referring to the continuing project as a whole.
- Record both identifiers in the public README after the first archive exists.
- Do not replace files inside an earlier archival release to incorporate later
  discoveries or ordinary corrections. Publish a new version instead.

The version DOI remains attached to its immutable snapshot. The concept DOI
resolves to the latest version while preserving links to the earlier records.
Zenodo documents this distinction in its
[DOI versioning guide](https://zenodo.org/help/versioning) and documents the
GitHub workflow in its
[release-archiving guide](https://help.zenodo.org/docs/github/archive-software/github-upload/).

## DOI Placement After the First Release

The first Zenodo archive creates the DOI, so the first archived PDF does not
need to print its own identifier. After Zenodo processes `v1.0.0`:

1. add the concept DOI and the `v1.0.0` version DOI to the public README;
2. update the live `CITATION.cff` with the appropriate release identifier;
3. add the DOI to the manuscript source for the next file-changing release;
4. do not create a new release solely to place a badge or DOI inside otherwise
   unchanged files unless the author specifically decides that is worthwhile.

## Research Corrections

If a future check changes a Hebrew form, value, hit count, control result, or
interpretive conclusion, the new release must state:

- what the previous version said;
- what the corrected version says;
- which generated artifacts changed;
- whether the correction strengthens, weakens, or leaves the larger pattern
  unchanged.

Historical claims may remain in audit tables when clearly labeled as inherited
or superseded. They must not survive as current claims elsewhere in the paper.

## Release Boundary

Work may accumulate on the private repository and the public `main` branch
without immediately producing a DOI. A numbered release should be created only
when the manuscript, generated evidence, changelog, citation metadata, and PDF
have passed the required checks together.
