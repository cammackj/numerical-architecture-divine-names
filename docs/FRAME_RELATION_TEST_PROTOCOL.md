# Named-Frame Relation Audit Protocol

## Status and Purpose

This is an exploratory, outcome-aware audit motivated by the known observation

`YHWH = 22_12` and `Yeshua = 282_12`.

John 14:11 prompted a more general question: do other admitted divine names, titles, or formulas have odd-length base-12 palindromes whose outer digits reproduce the complete base-12 value of another admitted expression?

The motivating YHWH--Yeshua relation was known before this protocol. The audit therefore cannot assign it a discovery probability. The protocol is being frozen before the complete registered corpus and expansion output are scanned for additional relations.

## Source Tables

The audit will read only generated, source-controlled values already present in:

- `data/master_results.csv`, containing the 40 analyzable manuscript objects and their declared corpus layers;
- `data/divine_name_expansion_results.csv`, containing all 82 tested expansion candidates, including non-hits.

Rows will retain their source table, corpus layer, object class, attestation status, Hebrew form, representative source, and value-system label. Duplicate expressions across the two tables will be identified in the output rather than silently counted as independent discoveries.

## Fixed Definitions

For each row and for each value system separately:

1. Convert the admitted value to base 12 using digits `0`--`9`, `A`, and `B`.
2. A host is eligible when its base-12 form is a palindrome of odd length at least three.
3. Remove the single middle digit from the host. The remaining ordered digits are its **outer frame**.
4. A **named-frame relation** occurs when that exact outer-frame string is the complete base-12 value of at least one other admitted expression.
5. A **self-center relation** occurs when the numerical value of the host's middle base-12 digit equals the conventional base-10 digital root of the host's gematria value.
6. Hosts sharing the same outer frame form a **frame family**. Their pairwise absolute differences will be calculated in decimal and base 12.

Standard gematria and Mispar Gadol are primary separate analyses. A secondary cross-layer view may group identical displayed base-12 frames across the two systems, but every row must retain its basis label and mixed-basis families must be identified as such.

## Frozen Difference Anchors

Pairwise frame-family differences will be compared only with the manuscript's existing numerical reference set:

`{8, 12, 22, 26, 31, 37, 42, 52, 72, 73, 91, 137, 153, 314, 345, 358, 386, 655}`.

This list is inherited from the repository's exploratory constant registry. No new reference value will be added after the pairwise differences are seen. Unlisted differences may still be reported descriptively, but they will not be labeled anchor hits.

## Complete YHWH-Frame Enumeration

The audit will enumerate all twelve three-digit palindromes of the form `2d2_12`, where `d` ranges from `0` through `B`. For each value it will record:

- decimal value;
- conventional base-10 digital root;
- numerical base-12 digit sum;
- whether the center equals the decimal digital root;
- whether the base-12 digits sum to 12;
- whether both conditions hold.

This is a complete finite enumeration, not a random simulation. It can establish uniqueness within the declared `2d2_12` family, but it cannot establish why a named expression occupies any particular member.

## Layer Sensitivities

Results will be summarized for:

- the 24-row primary biblical manuscript layer;
- all 40 manuscript rows;
- the 56-row biblical expansion;
- the 18-row Christian-comparative expansion;
- the 8-row later-traditional expansion;
- the union of all declared rows, with duplicate identities visible.

The report must state which relations survive under standard gematria, which require Mispar Gadol, and which appear only in the secondary mixed-basis view.

## Interpretation Limits

An exact frame relation establishes a relationship between displayed numeral strings. It does not establish literary dependence, theological identity, intentional encoding, or statistical surprise.

The full scan may reveal that such frames are common, confined to a few values, or sensitive to corpus and value system. Negative and weakening results will be retained. Scriptural interpretation will be considered only after the numerical output is complete, and it will remain distinct from the arithmetic result.
