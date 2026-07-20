# Version 1.1.0 Bounded Analyses

This directory contains the two post-publication analyses admitted to manuscript
version 1.1.0. It excludes the private research atlas and every broader book,
canon, pair-sum, and figurate exploration.

## Included Threads

- `PSALM_22_EXPLORATION.md` records the frozen Psalm-opening and whole-Tanakh
  comparisons behind the *Ayelet HaShachar* result and the Yeshua consonantal
  containment.
- `REPDIGIT_LADDER_EXPLORATION.md` records the complete `13 * digit` ladder,
  its empty rungs, additive relations, finite subset census, and the `66_12`
  boundary check.
- `scripts/` contains the two generators.
- `data/` contains every generated table used by those reports.

Run the Psalm analysis first because the ladder's `66_12` boundary verifies a
row in the generated Psalm-opening table:

```powershell
python research/scripts/psalm22_exploration.py --morphhb-source C:\path\to\morphhb
python research/scripts/repdigit_ladder_exploration.py
```

The MorphHB checkout must be at commit
`3d15126fb1ef74867fc1434be1942e837932691f`.
