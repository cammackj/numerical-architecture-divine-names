# Reproducibility Guide

## Environment

- Python 3.12 or later
- NumPy 2.4.3
- XeLaTeX or LuaLaTeX

Install the Python dependency from the repository root:

```powershell
python -m pip install -r requirements.txt
```

The scripts use fixed seeds where simulation is involved. Generated CSV files
are UTF-8 encoded and are committed so that the reported results can be inspected
without rerunning the analyses.

## Source Registry and Direct Calculations

`data/corpus_registry.csv` is the row-level authority for admitted Hebrew forms,
corpus layers, attestations, and source links. Run the direct analyses from the
repository root:

```powershell
python scripts/audit_numerical_claims.py
python scripts/corpus_sensitivity.py
python scripts/collapse_sensitivity.py
python scripts/base_comparison.py
python scripts/divine_name_expansion_scan.py
python scripts/exploratory_pattern_mining.py
python scripts/mathematical_constant_audit.py
python scripts/variant_audit.py
python scripts/strict_cluster_reclassification.py
python scripts/build_master_results_table.py
python scripts/build_derivations_section.py
python scripts/frame_relation_analysis.py
```

Each script writes its machine-readable results to `data/` and, where applicable,
a human-readable report to `docs/`.

## Matched Controls

The committed control pool was extracted from the Open Scriptures Hebrew Bible
at the exact MorphHB commit recorded in `data/control_source_lock.csv`. Rebuilding
the pool requires a local checkout of that repository:

```powershell
python scripts/build_control_pool.py --source C:\path\to\morphhb
```

After the pool has been rebuilt or verified, run:

```powershell
python scripts/matched_control_analysis.py
python scripts/joint_pattern_analysis.py --morphhb-source C:\path\to\morphhb
python scripts/network_robustness_analysis.py
```

The relevant preregistered or frozen rules are preserved in:

- `docs/CONTROL_TEST_PROTOCOL.md`
- `docs/JOINT_PATTERN_TEST_PROTOCOL.md`
- `docs/ROBUSTNESS_TEST_PROTOCOL.md`
- `docs/FRAME_RELATION_TEST_PROTOCOL.md`
- `docs/REPEATED_FRAME_CENTER_PROTOCOL.md`

## Build the PDF

Run XeLaTeX twice so cross-references and the table of contents settle:

```powershell
Set-Location tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

The publication PDF at the repository root is copied from the successful build
only after the manuscript has been reviewed.
