# Network and Formula Robustness Protocol

## Status

This protocol freezes post-result stress tests before their outcomes are calculated. It follows the joint-pattern results committed at `a65c2ee`. The original names, anchors, and contact routes were selected from already observed patterns, so these analyses remain exploratory even when their rules precede the new robustness outcomes.

Protocol date: 2026-07-19.

The locked source, control pool, structural matches, gematria functions, target nodes, anchors, and six contact routes remain those defined in:

- `docs/CONTROL_TEST_PROTOCOL.md`;
- `docs/JOINT_PATTERN_TEST_PROTOCOL.md`.

No new name, anchor, route, spelling, gematria system, or mathematical constant may be added during this analysis.

## 1. Leave-One-Node-Out Networks

The six-node target network contains YHWH, Yeshua, Yeshua HaMashiach, Ehyeh Asher Ehyeh, Eloah, and Elohim.

Each node will be removed in turn. For every resulting five-node network, the analysis will report:

- distinct node-anchor incidences;
- pairwise node links sharing at least one anchor;
- occupied anchors;
- nodes contacting at least one anchor;
- base-12 palindrome count.

The two declared robustness metrics are node-anchor incidences and pairwise shared-anchor links. Each omitted network will be compared with 100,000 structurally matched control networks using the original seed `20260719`. The full six-node draws will be generated once, without replacement within each draw, and the corresponding control slot will be removed so every omission uses the same baseline sample.

Raw empirical upper-tail probabilities use the add-one rule. Holm adjustment will be applied across the twelve declared node-omission tests: six omissions times two robustness metrics.

The Yeshua omission is of particular substantive interest, but its probability receives no special exemption from the family correction.

## 2. Leave-One-Anchor-Out Networks

Each anchor in `{8, 12, 22, 42, 72}` will be removed in turn while all six nodes and routes remain fixed. The two robustness metrics and 100,000 matched draws remain unchanged.

Holm adjustment will be applied across the ten declared anchor-omission tests.

## 3. Leave-One-Route-Out Networks

Each frozen contact route will be removed in turn:

1. exact decimal value;
2. exact base-12 digit string;
3. first base-12 digit sum;
4. palindromic center;
5. palindromic outer frame;
6. repeated outer-component sum.

Contacts supported by another surviving route remain present. Holm adjustment will be applied across the twelve declared route-omission tests.

These omission analyses test dependence, not prospective confirmation. A result that disappears after removing one element is concentrated in that element; a result that remains elevated across omissions is structurally distributed.

## 4. Yeshua Consonant-Family Adjustment

The 7,677 one-word, four-letter, zero-final structural controls for Yeshua will be grouped by sorted consonant multiset. All forms in one multiset family necessarily share standard gematria.

The report will give:

- total distinct consonant families;
- exact `282` families;
- forms and first attestations in every exact family;
- the exact-family count after excluding the family containing Yeshua's consonants.

Form-level and family-level proportions will both be retained. The family adjustment prevents multiple permutations of one gematria-equivalent consonant set from being interpreted as independent collisions.

The already frozen proper-name sensitivity will not be redefined. Its two exact hits will simply be identified as members of the Yeshua consonant family.

## 5. Attainable-Anchor Placebo Sets

The purpose of this test is to account for freedom in noticing a favorable five-anchor set.

For each of the six target nodes, every numerical output made available by the six frozen routes will be collected before filtering against the theological anchors. Candidate anchors must be integers from 2 through 99. The candidate pool will then be separated into:

- attainable one-digit anchors from 2 through 9;
- attainable two-digit anchors from 10 through 99.

Every placebo set containing exactly one attainable one-digit anchor and four distinct attainable two-digit anchors will be enumerated. This matches the digit-length structure of `{8, 12, 22, 42, 72}` while restricting the placebo universe to numbers that the selected nodes could actually contact under the declared rules.

For each set, the fixed six-node target network will be rescored for:

- node-anchor incidences;
- pairwise shared-anchor links;
- occupied anchors;
- nodes contacting at least one anchor.

The report will give the exact number and proportion of attainable placebo sets equaling or exceeding the theological anchor set on each metric and jointly on both declared metrics. This is an exact finite enumeration, not a Monte Carlo probability.

The generalized center route connects an odd-length palindrome to whichever one-digit center value is present. All other routes retain their original definitions.

## 6. Asher-Specific Formula Controls

The prior formula test matched the broad `X Y X` structure. This extension fixes the middle term to Asher, `אשר`.

### Attested Controls

The locked Hebrew control pool will be enumerated for exact surface sequences `X אשר X`. Results will be reported for:

1. the exact target structure, with four-letter outer words and zero final forms;
2. every attested three-word `X אשר X` sequence, regardless of outer length.

The completion event remains fixed: `X` is not palindromic in base 12, while the complete `X אשר X` value is palindromic in base 12.

### Synthetic Template Controls

Every structurally eligible one-word control for standalone Ehyeh will be inserted into the arithmetic template `X + Asher + X`, whether or not the resulting phrase is biblically attested. Tested divine expressions remain excluded by the existing control rules.

The completion rate will be reported at three levels:

- deduplicated Hebrew surface forms;
- consonant-multiset families;
- distinct standard-gematria values of `X`.

This synthetic test isolates the arithmetic effect of the fixed Asher value and repeated outer component. It does not claim that the generated strings are meaningful Hebrew declarations.

## Reproducibility and Interpretation

All machine-readable results and the human-readable report must be generated from one script. The script must validate that its baseline six-node network reproduces the committed joint-pattern metrics before reporting any omission result.

These tests may show that a pattern is robust, concentrated in one node or rule, common under alternative anchors, or sensitive to grammar. None can independently establish design or theological intention because they stress-test a network discovered before this protocol existed.
