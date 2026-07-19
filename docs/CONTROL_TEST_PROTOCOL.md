# Matched-Control Test Protocol

## Status

This protocol is frozen before control-corpus gematria values or palindrome outcomes are generated. Its version is the Git commit that first adds this file. Control extraction, numerical analysis, and any later amendments must appear in subsequent commits so that outcome-dependent changes remain visible.

Protocol date: 2026-07-18.

## Research Question

The primary question is whether the source-controlled biblical divine-name corpus produces more base-12 palindromes than structurally matched Hebrew Bible expressions normally produce.

The test does not attempt to prove intentional encoding or theological causation. It estimates how unusual the observed concentration is under declared orthographic controls.

## Tested Corpus Layers

The following layers must be reported separately.

1. **Repository-locked primary biblical analysis set.** Use all 24 rows labeled `primary-biblical` in `data/corpus_registry.csv`, using `analysis_hebrew`. This set remains unchanged regardless of control results. It is the source-secure remainder of an inherited, previously inspected list rather than a corpus assembled independently of the numerical hypothesis.
2. **Expanded biblical sensitivity corpus.** Add all 56 rows marked `broad_biblical_scan=yes` in `data/divine_name_expansion_candidates.csv`, including every non-hit. Because these rows were assembled during discovery and contain nested expressions, this layer is exploratory.
3. **Restored Christian-inclusive corpus.** Add the four inherited `messianic-comparative` rows plus `Yeshua HaMashiach / ישוע המשיח`. The combined title is included because the author reports identifying it before the present audit, but the surviving manuscript does not preserve it. This remains a sensitivity layer rather than an independently selected Hebrew-Bible sample.
4. **Full Christian-expansion sensitivity corpus.** Add all Christian-comparative expansion candidates, including orthographic controls and non-hits, rather than selecting only palindromic titles.

Formula-level, later-traditional, translation-sensitive, and ordinary-mathematical discoveries remain labeled by their existing evidence tiers. They may be tabulated but may not be silently pooled into the primary statistic.

## Control Source Lock

Controls are derived from the [Open Scriptures Hebrew Bible](https://github.com/openscriptures/morphhb), a morphologically annotated Hebrew Bible based on the Westminster Leningrad Codex. The locked source revision is:

`3d15126fb1ef74867fc1434be1942e837932691f`

The extraction uses `wlc/*.xml` from that revision. The project identifies its lemma and morphology data as [CC BY 4.0](https://github.com/openscriptures/morphhb/blob/3d15126fb1ef74867fc1434be1942e837932691f/LICENSE.md).

## Control Units

The primary control pool consists of contiguous Hebrew word sequences contained within a single verse. Sequence lengths range from one word through the maximum word count required by a tested corpus layer.

The extraction rules are fixed as follows:

- use top-level `<w>` tokens in each verse and exclude readings nested inside `<note>` elements;
- retain the top-level ketiv token when a qere note is present;
- require Hebrew morphology (`H...`) for every token in a sequence and exclude Biblical Aramaic sequences;
- remove cantillation, vowel points, punctuation, XML separators, and non-Hebrew characters;
- preserve consonants and the five final letter forms `ךםןףץ`;
- never cross a verse boundary;
- deduplicate by normalized consonantal phrase, retaining first attestation and total frequency;
- exclude any sequence containing a complete forbidden test expression as a contiguous subsequence;
- treat every surviving phrase type as one eligible control unit, regardless of biblical frequency.

The forbidden-expression list is the union of nonempty Hebrew forms in `data/corpus_registry.csv` and `data/divine_name_expansion_candidates.csv`. This prevents a tested divine name or title from re-entering as its own control. The extraction report must disclose the resulting pool size and all exclusions.

## Structural Matching

Every tested row is matched without reference to gematria outcomes. The primary matching stratum requires:

- the same word count;
- the same ordered vector of Hebrew-letter word lengths;
- the same number of final-form letters.

If an exact stratum contains fewer than 50 unique control phrases, the following deterministic fallback applies:

1. retain exact word count, exact total letter count, and exact final-form count while relaxing the ordered word-length vector;
2. if fewer than 50 controls remain, retain exact word count and final-form count and admit the smallest available absolute total-length difference, first `1`, then `2`;
3. if the pool still contains fewer controls than the multiplicity required by a tested corpus, stop and report the unmatched stratum rather than inventing another rule.

The final match level and eligible-control count must be reported for every target row. A control phrase may not be selected twice within one simulated corpus.

## Numerical Operations

The existing source-controlled functions are reused without modification:

- standard gematria;
- Mispar Gadol with expanded values only for the five actual final forms;
- positional conversion to every base from 2 through 20;
- palindrome status requiring at least two digits;
- the current repeated digit-sum collapse stopping at 12.

No spelling variants, alternative gematria systems, digit reversals, concatenations, substring searches, or mathematical-constant searches may be introduced during this test.

## Outcomes

Two co-primary outcomes are fixed:

1. the number of standard-gematria values palindromic in base 12;
2. the number of Mispar Gadol values palindromic in base 12.

The report must also include these secondary outcomes:

- base-12 competition rank among bases 2 through 20 for both value systems;
- whether base 12 is the sole palindrome-count leader;
- the number of rows palindromic in base 12 on either value layer;
- per-base palindrome counts for all bases 2 through 20;
- strict collapse-to-8 and collapse-to-12 counts under the already defined rule.

The full distribution and negative results must be retained. Base 12 may not be reported without its competing bases.

## Simulation

- Generate exactly 100,000 matched control corpora for each tested layer.
- Use the fixed pseudorandom seed `20260718`.
- Sample without replacement within each simulated corpus.
- Preserve target-stratum multiplicity so that every simulated corpus has the same structural profile as its tested corpus.
- Compute empirical upper-tail probabilities as `(1 + number of simulations at least as extreme as observed) / (100000 + 1)`.
- Report raw empirical probabilities for both co-primary outcomes and Holm-adjusted values across those two tests.
- Report Monte Carlo counts and proportions rather than replacing them with qualitative labels.

Expanded and Christian-inclusive layers receive the same simulations for comparability, but their empirical probabilities remain exploratory because those layers were specified after pattern discovery and include non-independent expressions.

## Blind Workflow

1. Commit this protocol.
2. Build and validate a structural control-pool CSV containing no gematria, base-conversion, palindrome, or collapse columns.
3. Commit the extraction script, source lock, structural pool, and matching-availability report.
4. Only then add and run the numerical simulation script.
5. Generate machine-readable outcomes and a human-readable report directly from the committed inputs.
6. Record any protocol deviation in a dedicated section; never edit the original rule silently.

## Interpretation Limits

An unusually low empirical probability would show that the declared corpus has a base-12 palindrome concentration that is uncommon among these matched Hebrew expressions. It would not by itself establish design, antiquity, theological intent, or independence among nested names and formulas.

A typical control result would not erase the observed patterns. It would change their evidential role from statistical distinctiveness to descriptive and theological interpretation.

## Protocol Deviations

None at freeze time.
