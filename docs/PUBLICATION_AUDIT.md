# Publication Audit

## Final Citation, Source, and Consistency Pass

Date: July 19, 2026

This pass checks the manuscript as a reader-facing paper and the repository as
its supporting record. It does not add a new argument or reinterpret the
results. Its purpose is to make sure that the citations resolve, the linked
sources support the uses made of them, and the numerical summaries agree with
the generated data.

## Citation and Source Results

- The manuscript contains 12 citation keys and 12 bibliography entries.
- No citation key is missing a bibliography entry.
- No bibliography entry is unused.
- The TeX source and the two source registries contain 110 unique external
  addresses. All 110 returned a successful response during this audit, with no
  unintended redirect.
- The cited passages for the 22 foundation letters, the 42-letter Name, the
  three 72-letter verses, the AB/SAG/MAH/BEN labels, Josephus's 22 books, the
  later 24-book enumeration, and the received 929-chapter division were checked
  at the content level.
- The source registries now give a live source address for every attested
  candidate. The only rows without one are three deliberately synthetic plene
  spelling controls, each labeled `orthographic-control`.

## Corrections Made

1. The Yeshua HaMashiach witness now points to the exact phrase in Biblica's
   Hebrew translation at Matthew 1:1, hosted by YouVersion. The earlier direct
   Biblica Mark link was bot-blocked and less precise.
2. The Sefer Yetzirah bibliography link now covers the stated 2:1-2 range rather
   than only 2:2.
3. The Avinu Malkeinu registry link now opens the exact prayer text rather than
   redirecting to a general festival-siddur page.
4. Source locks were added for HaMashiach, Ben HaAdam, HaShem, Ein Sof, and
   Qudsha Berikh Hu. The plene Son of God control was also moved to an exact
   modern Hebrew New Testament witness.

These changes affect provenance metadata only. They do not change any Hebrew
input used in a calculation.

## Numerical and Structural Consistency

Every deterministic generator that consumes the corrected source registry was
rerun after the source corrections. Only source labels and addresses changed.

- inherited derivation objects: 43;
- analyzable source-admitted objects: 40;
- frozen primary biblical corpus: 24;
- expansion registry: 82 candidates, divided into 56 biblical, 18
  Christian-comparative, and 8 later-traditional rows;
- expansion hits: 9 biblical, 8 Christian-comparative, and 3 later-traditional;
- primary base-12 palindromes: 4 under standard gematria and 5 under Mispar
  Gadol, ranked third and second respectively among bases 2-20;
- restored 29-row Christian-inclusive layer: 6 standard and 7 Mispar Gadol
  base-12 palindromes, with base 12 ranked first under both systems;
- named-frame audit: 30 eligible value layers and 23 named-frame matches;
- repeated-frame enumeration: 132 complete cases and exactly two joint
  solutions, `282_12` and `525_12`;
- matched control pool: 470,793 unique normalized phrase types;
- Yeshua-value controls: 20 surface forms, including 12 rearrangements of the
  Yeshua consonants and 8 forms in four other consonant families;
- alternative-anchor audit: 196 of 840 sets meet or exceed both original
  network scores;
- Asher-template audit: 591 of 7,677 surface forms, 271 of 3,583 consonant
  families, and 53 of 786 outer values complete as base-12 palindromes.

The main paper, figures, conclusion, and technical appendices state these values
consistently. Earlier errors remain visible only where the appendix explicitly
labels them as inherited displays or historical claims.

## Remaining Publication Tasks

- choose manuscript, code, and data licenses;
- update `CITATION.cff` for version 1.0.0 and the final release date;
- obtain the author's approval of the exact release tree and PDF;
- create the GitHub release and verify the Zenodo archive and DOI metadata;
- add the DOI to the manuscript and repository after Zenodo assigns it.

External websites can change after this audit. The locked Hebrew Bible commit,
source-controlled registries, generated tables, and archived release are the
long-term reproducibility record.
