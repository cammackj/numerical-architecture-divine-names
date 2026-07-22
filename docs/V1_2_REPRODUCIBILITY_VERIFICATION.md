# Version 1.2.0 Reproducibility Verification

## Verification Scope

This record documents the public-package verification performed on July 22,
2026. The public baseline before the update was commit `7276fe2`. The reviewed
private candidate PDF had SHA-256
`332B4C97FD230BAB9FD6C5238D33869273509978D95FB8DE49A483CCDEB0BD8A`.

Version 1.2.0 preserves the version 1.1.0 primary corpus, value systems,
arithmetic rules, matched-control design, seeded simulations, and evidence
hierarchy. The changed numerical scope consists of the deterministic chapter
closure census and the expression-row versus distinct-value base-ranking
sensitivity. The matched-control generator changed only in its explanatory
report text, but the complete frozen simulation was rerun as a release check.

## Environment

- Operating environment: Windows PowerShell
- Python: 3.12.4
- Git: 2.30.0.windows.2
- XeTeX: 4.18, MiKTeX 26.2
- Verification date: 2026-07-22
- Time zone: America/Denver

## Analysis Results

The following commands completed successfully from the public repository:

```powershell
python scripts/audit_numerical_claims.py
python research/scripts/chapter_closure_exploration.py
python scripts/distinct_value_base_ranking.py
python scripts/matched_control_analysis.py
```

The numerical audit reproduced the existing master results and flags without a
tracked change. The frozen matched-control simulation completed all four layers
with 100,000 samples each and reproduced every existing numerical CSV
byte-for-byte. Its standard and Mispar Gadol primary corrected probabilities
remain `0.135059` and `0.090579`; the restored Christian-inclusive values remain
`0.030240` and `0.016940`.

The new closure generator enumerated all 1,584 three-digit base-12 integers.
Exactly 132 admit the declared one-digit right palindromic closure. It reproduced
the unique `6556_12` conjunction described in the manuscript and the complete
registered title contacts.

The new base-ranking generator reproduced these primary results:

- expression rows: base 12 ranks third under standard gematria and second under
  Mispar Gadol; base 3 leads both with six rows;
- distinct values: base 12 shares first with bases 3, 7, and 20 under standard
  gematria and with base 3 under Mispar Gadol;
- restored Christian-inclusive distinct values: base 12 leads alone under both
  systems.

The existing synthetic `2x + 501` control was not rerun because neither its
code nor its inputs changed. Its complete output remains in
`docs/ROBUSTNESS_TEST_RESULTS.md`; version 1.2.0 changes only the source and
scope wording around the already calculated Ehyeh subtotal.

## Artifact Hashes

| Artifact | SHA-256 |
| --- | --- |
| `research/CHAPTER_CLOSURE_EXPLORATION.md` | `CECDE5EFCAC9EF1FFD9A7AAC2DCCBA513CE6B11363780ED5F808F106E72C7AA7` |
| `research/data/chapter_closure_finite_scan.csv` | `02832513E8D6D1D60AD4FFC08F02D1DE348EC68F2A88851B9043FE63ED69A65F` |
| `research/data/chapter_closure_registry_contacts.csv` | `E53A02B47259947B766248F9CD42BCF29C9C46C3012319AD665E327402DA274E` |
| `docs/DISTINCT_VALUE_BASE_RANKING.md` | `4D403678BB3C39DD9ADE712A5255697DD03176EAE6ACC8FE7CF51F1E7852B3DA` |
| `data/distinct_value_base_ranking.csv` | `CCEAF57836D845DF52D67138053ED0CEEE955FB312E0C244682C47842633A961` |
| `docs/MATCHED_CONTROL_RESULTS.md` | `1931BA79038EC6D27659ACBCFC2E86168CC40D1B7610BD47AE6F8ED325546C49` |
| `data/control_simulation_summary.csv` | `1B988C4F8E4D42CAD4C7300597E9C0607202C90B04B43222850F1E41E29FEEAA` |
| `Numerical_Architecture_of_the_Divine_Names.pdf` | `B1F4131FED09F941801C4CD897D4136F907FA7C7122799BD66BAA57B553C404E` |

## PDF Verification

The public manuscript rebuilt successfully in two XeLaTeX passes:

- Pages: 98
- Page size: US Letter
- LaTeX warnings, overfull boxes, underfull boxes, undefined references, or
  fatal errors: none
- Publication PDF SHA-256:
  `B1F4131FED09F941801C4CD897D4136F907FA7C7122799BD66BAA57B553C404E`
- Extracted-text SHA-256:
  `1C95BA1A2A8079DF6C0D801A3EB567A1E80C5567017F5359545579B8EC3CB69C`
- Extracted characters: 183,875

The public PDF and the author-approved private review PDF have identical
extracted text. All 98 pages were rendered independently at 100 DPI; every
public page matched its approved counterpart pixel-for-pixel.

## Release Metadata

`CITATION.cff` parses as YAML and identifies version 1.2.0 with release date
2026-07-22. Because a version DOI cannot exist before archival publication, the
release candidate uses the reproducibility-package concept DOI
`10.5281/zenodo.21448554` and the working-paper concept DOI
`10.5281/zenodo.21459464`. The live metadata will be updated with the new exact
version DOIs after Zenodo creates them.

## Scope Boundary

The public package includes the chapter-closure report, generator, and two
tables; the distinct-value ranking report, generator, and table; and the formal
Ehyeh review. It does not include the private research atlas, broader canon and
book searches, pair-sum and figurate explorations, or the arbitrary *Abba*
label association.

## Conclusion

The version 1.2.0 public package reproduces every changed analysis and the
approved 98-page manuscript. The earlier version 1.0.0 and 1.1.0 snapshots and
their DOIs remain unchanged.

