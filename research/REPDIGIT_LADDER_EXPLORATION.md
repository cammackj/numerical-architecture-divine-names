# Base-12 Repdigit Ladder Exploration

## Status

Post-publication exploratory analysis integrated into manuscript version
`1.1.0`. The archived `v1.0.0` remains unchanged.

## Mathematical Identity

Every two-digit repeated-digit numeral in base 12 satisfies:

`dd_12 = 12d + d = 13d`

The two-digit divine-name palindromes are therefore members of one exact
11-rung ladder rather than unrelated conversions.

## Observed Ladder

| Rung | Decimal | Base 12 | Core | Extended | Occupants |
| ---: | ---: | ---: | --- | --- | --- |
| 1 | 13 | `11` | yes | yes | Echad |
| 2 | 26 | `22` | yes | yes | YHWH |
| 3 | 39 | `33` | yes | yes | YHWH Echad |
| 4 | 52 | `44` | yes | yes | Elohei; BEN |
| 5 | 65 | `55` | yes | yes | Adonai |
| 6 | 78 | `66` | no | no | - |
| 7 | 91 | `77` | yes | yes | Adonai YHWH; Amen lexical form |
| 8 | 104 | `88` | no | no | - |
| 9 | 117 | `99` | no | yes | Malakh YHWH |
| 10 | 130 | `AA` | no | no | - |
| 11 | 143 | `BB` | no | yes | Ben HaElohim defective |

The core six rungs are `1, 2, 3, 4, 5, 7`. They use exact biblical names,
formulas, or components, but they are not six independent lexical names:
`Echad` and `Elohei` are components, and `YHWH Echad` and `Adonai YHWH` contain
already counted names. The extended set adds the Christian divine-agent
reading at rung 9 and a translation-sensitive defective title at rung 11.

The missing sixth rung is explicit: `66_12 = 78_10`, but neither the corrected
manuscript registry nor the 82-row expansion registry contains an admitted
name, title, formula, or component at value 78 under either value system. The
Psalm-opening scan contains one mechanical two-word window at that value,
`יהוה בכל` in Psalm 111:1, but it cuts the ordinary phrase "YHWH, with all
[my heart]" before its completion. It is retained as a boundary check rather
than promoted into a divine title. Rungs 8 and 10 are also unoccupied.

## Additive Closure

Because the ladder is linear in 13, addition of occupied rungs becomes
carry-free addition of repeated base-12 digits whenever the result remains
below 12.

### Core relations

| Rungs | Decimal equation | Base-12 equation | Named nodes |
| --- | --- | --- | --- |
| 1 + 2 = 3 | `13 + 26 = 39` | `11 + 22 = 33` | Echad + YHWH -> YHWH Echad |
| 1 + 3 = 4 | `13 + 39 = 52` | `11 + 33 = 44` | Echad + YHWH Echad -> Elohei; BEN |
| 1 + 4 = 5 | `13 + 52 = 65` | `11 + 44 = 55` | Echad + Elohei; BEN -> Adonai |
| 2 + 3 = 5 | `26 + 39 = 65` | `22 + 33 = 55` | YHWH + YHWH Echad -> Adonai |
| 2 + 5 = 7 | `26 + 65 = 91` | `22 + 55 = 77` | YHWH + Adonai -> Adonai YHWH; Amen lexical form |
| 3 + 4 = 7 | `39 + 52 = 91` | `33 + 44 = 77` | YHWH Echad + Elohei; BEN -> Adonai YHWH; Amen lexical form |

### Extended relations

| Rungs | Decimal equation | Base-12 equation | Named nodes |
| --- | --- | --- | --- |
| 1 + 2 = 3 | `13 + 26 = 39` | `11 + 22 = 33` | Echad + YHWH -> YHWH Echad |
| 1 + 3 = 4 | `13 + 39 = 52` | `11 + 33 = 44` | Echad + YHWH Echad -> Elohei; BEN |
| 1 + 4 = 5 | `13 + 52 = 65` | `11 + 44 = 55` | Echad + Elohei; BEN -> Adonai |
| 2 + 3 = 5 | `26 + 39 = 65` | `22 + 33 = 55` | YHWH + YHWH Echad -> Adonai |
| 2 + 5 = 7 | `26 + 65 = 91` | `22 + 55 = 77` | YHWH + Adonai -> Adonai YHWH; Amen lexical form |
| 2 + 7 = 9 | `26 + 91 = 117` | `22 + 77 = 99` | YHWH + Adonai YHWH; Amen lexical form -> Malakh YHWH |
| 2 + 9 = 11 | `26 + 117 = 143` | `22 + 99 = BB` | YHWH + Malakh YHWH -> Ben HaElohim defective |
| 3 + 4 = 7 | `39 + 52 = 91` | `33 + 44 = 77` | YHWH Echad + Elohei; BEN -> Adonai YHWH; Amen lexical form |
| 4 + 5 = 9 | `52 + 65 = 117` | `44 + 55 = 99` | Elohei; BEN + Adonai -> Malakh YHWH |
| 4 + 7 = 11 | `52 + 91 = 143` | `44 + 77 = BB` | Elohei; BEN + Adonai YHWH; Amen lexical form -> Ben HaElohim defective |

## Finite Subset Comparison

Among all `C(11, 6) = 462` six-rung subsets of `1..11`, the core set
has 6 distinct-addend closure relations. This is the
maximum possible. Only 2 subsets attain that maximum:
{1, 2, 3, 4, 5, 6}, {1, 2, 3, 4, 5, 7}. The descriptive finite proportion is
`2/462 = 0.004329`.

The eight-rung extended set has 10 relations. Among
all `C(11, 8) = 165` subsets, 31 have at
least that many, for a descriptive proportion of
`0.187879`. Its closure is therefore less exceptional than
the core six-rung set.

## Interpretation Boundary

This is a genuine algebraic organization, not six separate base-conversion
coincidences. It also has a strong selection caveat: the ladder was recognized
because these rows were already known to be two-digit base-12 palindromes, and
the core set mixes complete names with components and nested formulas. The
finite subset proportions describe the occupied rung pattern; they are not
sampling probabilities for independently selected divine names.

The strongest defensible result is structural: the source-secure biblical
nodes occupy the maximally additively closed six-rung subset `{1,2,3,4,5,7}`
of the 11 possible two-digit base-12 repdigits.
