# Joint-Pattern Test Protocol

## Status

This protocol freezes the next exploratory tests before their matched-control outcomes are calculated. The hypotheses arise from already known manuscript patterns, so the resulting probabilities are descriptive and must not be called preregistered confirmation.

Protocol date: 2026-07-19.

The control source, normalization, and structural matching rules remain those defined in `docs/CONTROL_TEST_PROTOCOL.md`. Controls come from the locked Open Scriptures Hebrew Bible revision `3d15126fb1ef74867fc1434be1942e837932691f` and contain no tested divine expression as a complete contiguous subsequence.

## Test 1: The Yeshua Joint Signature

### Target

The target is Yeshua, `ישוע`, under standard gematria. It has value 386 and base-12 representation `282`.

The matched stratum is fixed before outcome calculation:

- one word;
- four Hebrew letters;
- zero final-form letters;
- exact structural match.

Because the target has no final form, standard gematria and the manuscript's Mispar Gadol convention give the same value. The test therefore uses one value layer rather than counting the same result twice.

### Fixed Outcomes

The primary composite event is:

1. a three-digit base-12 representation;
2. palindromic form;
3. outer digits `22`;
4. center digit `8`;
5. first base-12 digit sum equal to 12.

These conditions are not independent. In a three-digit string, outer digits `22` plus center digit `8` already determine `282` and its digit sum. The report must therefore describe the composite as the exact `282` signature, not as five independent coincidences.

The report will also give nested counts for:

- any three-digit base-12 value;
- any three-digit base-12 palindrome;
- any three-digit `2?2` palindrome;
- any three-digit value with first digit sum 12;
- exact `282`.

Two reference universes will be reported:

1. all positive integers with three-digit base-12 representations, from 144 through 1727;
2. all eligible Hebrew control phrases in the fixed structural stratum.

The matched-control proportion is a type-level proportion in the deduplicated pool. No simulation is required for a single target because the complete eligible stratum can be enumerated.

### Post-Result Semantic Sensitivity

This sensitivity was added after the structural-control result was known but before proper-name gematria outcomes were calculated. It must therefore be reported separately from the frozen primary composite test.

The locked MorphHB XML marks an unprefixed, unsuffixed Hebrew proper name with morphology code `HNp`. The semantic sensitivity will enumerate top-level, non-note `<w>` tokens satisfying all of the following:

- morphology is exactly `HNp`;
- the normalized surface form contains exactly four Hebrew consonants;
- the surface form contains no final-form letter;
- the form is deduplicated across occurrences;
- every expression in the repository's corpus and expansion registries is excluded.

The report will give the same nested base-12 outcomes as the structural control and retain every exact `282` proper-name control with its first attestation and corpus frequency. MorphHB's `Np` class includes proper names broadly and does not by itself distinguish personal names from place names. The sensitivity therefore tests a semantic proper-name stratum, not a personal-name-only ontology.

## Test 2: Formula Completion

### Target

The target is Ehyeh Asher Ehyeh, `אהיה אשר אהיה`. Its first component, Ehyeh, is not palindromic in base 12, while the full formula is.

The exact matched stratum is:

- three words;
- ordered word lengths `4-3-4`;
- zero final-form letters.

### Fixed Structural Question

A control is a repeated-frame phrase when its first and third normalized tokens are identical, giving the form `X Y X`.

The fixed completion event is:

- the first token's standard-gematria value is not palindromic in base 12; and
- the complete phrase's standard-gematria value is palindromic in base 12.

The exact stratum will be divided into repeated-frame and nonrepeated phrases. The report will give counts, proportions, an odds ratio, and a two-sided Fisher exact probability for the difference. If a zero cell occurs, the raw table remains primary and any continuity-corrected odds ratio must be labeled.

A breadth sensitivity will repeat the comparison across all three-word control phrases, regardless of word-length vector or final-form count. Standard gematria remains the declared value system; Mispar Gadol may be reported only as a labeled sensitivity.

This test measures arithmetic propensity in repeated lexical frames. It does not test whether the middle word is grammatically equivalent to Asher or whether a control phrase has the same theological function.

## Test 3: Fixed-Anchor Network

### Target Nodes

The network contains six expressions selected because they already carry the cross-patterns under discussion:

1. YHWH, `יהוה`;
2. Yeshua, `ישוע`;
3. Yeshua HaMashiach, `ישוע המשיח`;
4. Ehyeh Asher Ehyeh, `אהיה אשר אהיה`;
5. Eloah, `אלוה`;
6. Elohim, `אלהים`.

The fixed anchors are `{8, 12, 22, 42, 72}`. Standard gematria is used throughout this test.

### Fixed Contact Rules

A node is connected to an anchor when at least one of the following is true:

1. its decimal gematria equals the anchor;
2. its base-12 representation exactly equals the decimal glyph string of the anchor;
3. the first sum of its displayed base-12 digits equals the anchor;
4. its odd-length base-12 palindrome has a center digit equal to the single-digit anchor 8;
5. its base-12 palindrome has outer digits whose two-glyph string equals the anchor;
6. it is an exact three-token repeated frame `X Y X`, and twice the standard-gematria value of `X` equals the anchor.

Multiple rules connecting the same node to the same anchor count as one node-anchor incidence. No additional anchors, value systems, reversals, approximations, mathematical constants, or substring rules may be added after calculation.

### Fixed Network Outcomes

The two primary descriptive outcomes are:

1. total distinct node-anchor incidences;
2. pairwise node links, where two nodes are linked if they contact at least one common anchor.

Secondary outcomes are:

- number of occupied anchors;
- number of nodes contacting at least one anchor;
- number of standard-gematria base-12 palindromes;
- route-specific contact counts.

### Matched Comparison

Each target node is replaced by one control from its existing structural stratum in `data/control_match_registry.csv`. One hundred thousand six-node control networks will be sampled using seed `20260719`. Sampling is without replacement when target nodes share a stratum.

Empirical upper-tail probabilities use `(1 + simulations at least as large as observed) / (100000 + 1)`. Holm adjustment will be reported across the two primary network outcomes. These probabilities quantify the fixed score within the matched control design; they do not remove the post-discovery selection of the six target nodes or the five anchors.

## Interpretation Limits

The Yeshua test can establish the exact mathematical uniqueness of `282` within the three-digit base-12 universe and its prevalence in matched Hebrew controls. It cannot assign a probability to divine intention.

The completion test can show whether lexical repetition makes palindrome completion more common. It cannot decide whether the full biblical declaration was composed for numerical reasons.

The network test can show whether the six selected expressions have more fixed anchor contacts than matched phrases. Because the nodes, anchors, and rules were motivated by previously observed results, even a small empirical probability remains exploratory. A genuinely confirmatory follow-up would require a newly selected corpus and an independently frozen feature vocabulary.
