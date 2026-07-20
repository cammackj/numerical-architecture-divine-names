# Reproducibility Verification

## Verification Scope

This record documents a complete source-level rebuild performed on July 19, 2026.
The tested public research baseline was commit
`e2d82167dff05b741a2239832512a69d49db7d77`. The private working baseline was
commit `1442b0fcb20c0adcc050b7d41cb5cad47369c16d`.

The rebuild covered the locked Hebrew source extraction, every deterministic
analysis, all seeded simulations, the joint-pattern proper-name sensitivity, the
network robustness study, and the complete XeLaTeX manuscript.

## Environment

- Operating environment: Windows PowerShell
- Python: 3.12.4
- NumPy: 2.4.3
- Git: 2.30.0.windows.2
- XeTeX: 4.18, MiKTeX 26.2
- Verification date: 2026-07-19
- Time zone: America/Denver

## Locked Source

The Open Scriptures MorphHB repository was checked out in detached-HEAD mode at:

`3d15126fb1ef74867fc1434be1942e837932691f`

The rebuild independently recovered the source lock already recorded in
`data/control_source_lock.csv`:

- WLC XML files: 40
- WLC tree SHA-256:
  `4e2d54cfbdb1817ceebf37f09e6a45c1e33c29e09186a50c8ac3733d8f8ce060`
- Control targets: 179
- Unique normalized control phrases: 470,793

Key regenerated artifact hashes:

| Artifact | SHA-256 |
| --- | --- |
| `data/control_phrase_pool.csv` | `FE7E8E1FF338C5F6E6B409110F685244ED02CFE562B18799DA9662C16F414D6D` |
| `data/control_match_registry.csv` | `5473BB77843CC9F85B308F5C6AFA6799B69FBF6F713F5CEE7ECA19E53A079EFE` |
| `data/control_simulation_summary.csv` | `1B988C4F8E4D42CAD4C7300597E9C0607202C90B04B43222850F1E41E29FEEAA` |
| `data/joint_signature_proper_name_counts.csv` | `0C1D19A9A1401E219B3F83ACB22800219A44E0C3547D3A7F2B6C2094CF4D8838` |
| `data/network_robustness_results.csv` | `DEC8F0D1D6BF679123BC6F5EAA5218268483007EAF33240D9793218E0E483AFC` |

## Analysis Results

All declared analysis stages completed successfully:

1. Direct gematria and inherited-claim audit
2. Corpus, collapse, and base sensitivity analyses
3. Divine-name expansion and exploratory pattern scans
4. Mathematical-constant and spelling-variant audits
5. Strict layer reclassification and master table generation
6. Frame-relation and repeated-center enumeration
7. Matched controls with 100,000 simulations and seed `20260718`
8. Joint-pattern controls with 100,000 simulations and seed `20260719`
9. MorphHB proper-name sensitivity
10. Network, consonant-family, placebo-anchor, and Asher-template robustness tests

After regeneration, all 108 shared tracked files under `data/`, `docs/`,
`scripts/`, and `tex/` matched the public repository by normalized Git blob
hash.

## Maintenance Finding

Seven generated files in the private working repository were stale. They predated
the corrected Hebrew forms in `data/corpus_registry.csv`, including the corrected
`רבונו`, construct `אלהי`, and `ע"ב = 72` records:

- `data/exploratory_constant_hits.csv`
- `data/exploratory_shared_values.csv`
- `data/mathematical_constant_hits.csv`
- `data/variant_audit.csv`
- `docs/EXPLORATORY_PATTERN_MINING.md`
- `docs/MATHEMATICAL_CONSTANT_AUDIT.md`
- `docs/VARIANT_AUDIT.md`

Regenerating them produced exact matches to the corrected files already present
in the public repository. The public research record did not require numerical
changes; the private saved outputs were brought into agreement with it.

## PDF Verification

The manuscript rebuilt successfully in two XeLaTeX passes:

- Pages: 91
- Page size: US Letter
- LaTeX warnings, overfull boxes, underfull boxes, undefined controls, or fatal
  errors: none
- Extracted-text SHA-256 for both rebuilt and public PDFs:
  `A9B2C2067F60438A35AEDA3CBA91EF8AE98F4D8E9F826B89DC4BA31553050373`
- Pages visually inspected: 1, 10, 22, 31, 81, and 91
- Those six rendered pages matched the public PDF pixel-for-pixel

The raw PDF binary hashes differ because XeLaTeX writes build-time metadata.
Content and sampled rendering were identical.

## Conclusion

The public repository at the tested baseline passes this reproducibility rebuild.
The result establishes same-environment regeneration from the locked source and
fixed seeds. It is not yet an independent cross-platform replication by another
researcher.
