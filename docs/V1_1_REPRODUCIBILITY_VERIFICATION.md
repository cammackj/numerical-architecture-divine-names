# Version 1.1.0 Reproducibility Verification

## Verification Scope

This record documents the public-package verification performed on July 20,
2026. The public baseline before the update was commit `54a63fc`; the approved
private manuscript candidate was commit `6932cc4`.

Version 1.1.0 preserves the version 1.0.0 corpus, arithmetic rules, primary
scripts, seeded simulations, and evidence hierarchy. The changed numerical
scope consists of the deterministic Psalm 22 and repdigit-ladder analyses.
Those two generators were rerun from the public repository. The unaffected
version 1.0.0 analyses were not rerun; their complete source-level verification
remains in `docs/REPRODUCIBILITY_VERIFICATION.md`.

## Environment

- Operating environment: Windows PowerShell
- Python: 3.12.4
- Git: 2.30.0.windows.2
- XeTeX: 4.18, MiKTeX 26.2
- Verification date: 2026-07-20
- Time zone: America/Denver

## Locked Source

The Psalm analysis used the Open Scriptures MorphHB repository at the required
commit:

`3d15126fb1ef74867fc1434be1942e837932691f`

The script rejected any different source revision. It regenerated 964
Psalm-opening windows, the complete whole-Tanakh two-word comparison, 114
Yeshua-sequence tokens, Psalm metrics, and every declared expression variant.

## Analysis Results

Both public generators compiled and completed successfully:

```powershell
python research/scripts/psalm22_exploration.py --morphhb-source C:\path\to\morphhb
python research/scripts/repdigit_ladder_exploration.py
```

The Psalm analysis reproduced the manuscript counts and negative variants. The
repdigit analysis reproduced all eleven rungs, the six source-secure occupied
rungs, six distinct-addend relations, the complete 462-member six-rung census,
the 165-member eight-rung census, and the empty admitted `66_12` registry check.
It also verified that the one value-78 Psalm-opening window is the incomplete
Psalm 111:1 sequence documented in the manuscript.

Key regenerated artifact hashes are:

| Artifact | SHA-256 |
| --- | --- |
| `research/PSALM_22_EXPLORATION.md` | `5992AD6043585A4066927B4F3B9074341227B2D231C6F056FAC37DA705324AC1` |
| `research/REPDIGIT_LADDER_EXPLORATION.md` | `21C8C038A7C10344EC3B8E29D5DFE6D141CC3968FA7E0D7B9818733B151A64D1` |
| `research/data/psalm_first_verse_two_word_windows.csv` | `7865C993748D4D3B8F41E4A727D729D715452B49CCFF96256723036DA2558629` |
| `research/data/tanakh_two_word_palindromic_square_strings.csv` | `0AEE3E2CB2F8C4C61B539D1324A3337472E471F4B4623C4246A6D61C1972E742` |
| `research/data/ayelet_hashachar_exact_value_controls.csv` | `63860EAFF1BEE132B8B5130A3A03ED77A77A75B02A203D408EDFC1FE7570CAC6` |
| `research/data/yeshua_sequence_occurrences.csv` | `13BE67C5B2E28B6EF92D7F742ECA1703D409D74CDDF1CAEB057FC674D2C8424A` |
| `research/data/psalm_metrics.csv` | `7AC2BDC504D6E735613E9C907F3CAA93B9B9E043A7A77011B006EAAE6DB7931B` |
| `research/data/psalm22_expression_variants.csv` | `69447DD4AE0837A3905A5A6BB0C278436166E8DDA787FECE7B0138BF5BC48AB1` |
| `research/data/repdigit_ladder.csv` | `38703FD6E5D1214E89FA3963CB761B11D7A92A898E1E30F3CEA0A99525A1A835` |
| `research/data/repdigit_additive_relations.csv` | `8445E17E87C036A43FCBC0466770867D1204718BC4721B39763258CFD49E4F37` |
| `research/data/repdigit_subset_enumeration.csv` | `688C8198359BB2CBB15518142DE3FEE62A81CB51688A47662F3DD70A3C142D52` |

## PDF Verification

The public manuscript rebuilt successfully in two XeLaTeX passes:

- Pages: 95
- Page size: US Letter
- LaTeX warnings, overfull boxes, underfull boxes, undefined controls, or fatal
  errors: none
- Publication PDF SHA-256:
  `85BBD1309433E12BF2F1AED06D77F7903EBD580CEF0AAAA062078C58DBC94EBF`
- Extracted-text SHA-256:
  `30FD8C31E579B2F4B607D4DF37A2C7E6332D6B29C8FC7D99892DEE739C72488A`

The rebuilt PDF and the author-approved candidate have the same 176,511
extracted characters. Rendered pages 1, 2, 3, 10, 11, 28, 31, and 95 match the
approved PDF pixel-for-pixel at 150 DPI. Those pages cover the title-page DOI,
abstract, introduction, complete ladder table, finite test, conclusion, and
final appendix page.

## Release Metadata

`CITATION.cff` parses as YAML and identifies version 1.1.0 with release date
2026-07-20. The release snapshot initially used the concept DOI because the
version DOI did not exist until after publication. The live metadata now records
version DOI `10.5281/zenodo.21450852` and retains concept DOI
`10.5281/zenodo.21448554` as the all-version identifier. The earlier version DOI
remains attached only to the immutable 1.0.0 archive.

## Zenodo Verification

Zenodo record `21450852` reports version `v1.1.0`, open access, CC BY 4.0,
ORCID `0009-0006-0482-4893`, and the exact GitHub `v1.1.0` tag relationship.
Its archived ZIP has MD5 checksum
`62f7727e44c75493f00991f540f6b968`. The archive contains the manuscript PDF,
LaTeX source, citation metadata, release notes, both research reports, both
generators, and all nine generated tables. The archived PDF SHA-256 is
`85BBD1309433E12BF2F1AED06D77F7903EBD580CEF0AAAA062078C58DBC94EBF`,
an exact match to the verified release asset.

## Conclusion

The version 1.1.0 public package reproduces both newly admitted analyses and the
approved 95-page manuscript. No private atlas thread or unrelated exploratory
result is included in the release.
