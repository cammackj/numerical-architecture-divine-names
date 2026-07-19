# Source-Critical Corpus Definition

This document freezes the first source-controlled corpus for the project. The row-level authority is `data/corpus_registry.csv`.

The inherited manuscript contains 43 objects, but they are not all the same kind of object. Treating 41 of them as interchangeable "literal headings" allowed biblical divine names, later rabbinic epithets, liturgical formulas, Christian messianic readings, false syntactic matches, and Kabbalistic value-labels to enter the same counts. The source-critical model keeps those materials, but separates them before numerical testing.

## Attestation Rule

A row enters the primary biblical corpus only when all of the following hold:

1. A specific Tanakh passage establishes the consonantal form or supplies a clearly documented orthographic correction.
2. The form functions as a designation of Israel's God in that passage, not merely as the same sequence of Hebrew letters.
3. The valued string is the attested object itself, not a description of a longer formula or an abbreviation whose letters were chosen to state a value.
4. Spelling, word division, articles, and final forms are fixed before numerical analysis.
5. A correction is logged as a correction. The inherited value is never silently retained after the source form changes.

Niqqud, cantillation, spaces, hyphens, and quotation marks do not receive gematria values. Consonants and final-letter positions do. The representative sources in the registry demonstrate attestation; they are not claims that each passage is the earliest historical use.

The exact-phrase check used Sefaria's [Search API](https://developers.sefaria.org/reference/post-search-wrapper), restricted to Tanakh for biblical candidates, and then inspected the verse context. Raw hit counts were not treated as attestation because `אל` can be either the noun *El* or the preposition *to*.

## Corpus Layers

| Layer | Rows | Use |
| --- | ---: | --- |
| Primary biblical | 24 | Repository-locked primary analysis after source-form corrections |
| Later traditional | 5 | Rabbinic and liturgical sensitivity layer |
| Messianic comparative | 4 | Christian-theological comparison, kept separate from the Hebrew Bible's immediate object class |
| Foreign deity or ambiguous | 1 | Historical comparison only |
| Constructed or false match | 3 | Excluded unless replaced by a separately attested full formula |
| Kabbalistic formula labels | 2 | Analyze as formulas or traditions, not literal names |
| Kabbalistic expansion labels | 4 | Analyze as value-bearing expansion abbreviations, not literal-name observations |

The 24-row primary corpus is therefore not a claim that these are the only biblical divine names. It is the defensible subset recoverable from the inherited 43-row list under a uniform rule. A future completeness study can add omitted names and titles, but it must use an inclusion rule fixed before examining their numerical results.

## Material Corrections

### Five Elohei Forms

The displayed rows use plene `אלוהי`, but the cited biblical consonantal forms are:

- `אלהי השמים`
- `אלהי הארץ`
- `אלהי אברהם`
- `אלהי יצחק`
- `אלהי יעקב`

Removing the vav changes every numerical result in these rows. The source-controlled calculations use the biblical forms.

### Article Corrections

`אל הנאמן` and `אל הגדול` are not the exact cited forms. The source texts have:

- `האל הנאמן` in [Deuteronomy 7:9](https://www.sefaria.org/Deuteronomy.7.9?lang=bi)
- `האל הגדול` in [Nehemiah 1:5](https://www.sefaria.org/Nehemiah.1.5?lang=bi)

The article is part of the valued string and cannot be dropped after the numerical result is known.

### False `El` Matches

`אל השמים` and `אל הארץ` occur as token sequences, but in the representative passages `אל` means *to*. They are not titles "God of the Heavens" and "God of the Earth." They are excluded. The attested biblical titles are `אלהי השמים` and, in [Genesis 24:3](https://www.sefaria.org/Genesis.24.3?lang=bi), `אלהי הארץ`.

### El HaNorah

No exact Tanakh occurrence of `אל הנורא` was found. The adjective appears in longer constructions such as `האל הגדול הגבור והנורא` in [Nehemiah 9:32](https://www.sefaria.org/Nehemiah.9.32?lang=bi). The short form is excluded unless the full formula is added as a separately valued object.

### Later Orthography

The inherited `ריבונו של עולם` includes a yod not found in the representative classical Talmud text. [Menachot 29b](https://www.sefaria.org/Menachot.29b.5?lang=bi) has `רבונו של עולם`, which equals 740 rather than 750. The row remains valuable as a rabbinic address formula, but its inherited 12-collapse is orthography-dependent.

`עמנואל` is represented in [Isaiah 7:14](https://www.sefaria.org/Isaiah.7.14?lang=bi) as two words, `עמנו אל`. The consonant sequence and gematria total remain unchanged.

### Expansion Labels

The four expansion names are conventionally labeled `ע"ב`, `ס"ג`, `מ"ה`, and `ב"ן`; a representative Kabbalistic source lists all four together in [Sha'ar HaHakdamot](https://www.sefaria.org/Sha'ar_HaHakdamot%2C_Zeir_Anpin_and_Nukba.18.1?lang=bi).

The inherited AB row displays `אב = 3`, which is not the intended `ע"ב = 72`. Correcting that error does not create an independently discovered exact-value hit: these abbreviations state the values by design. All four belong in an expansion appendix, outside literal-name and base-ranking counts.

## Interpretive Layers Preserved

The source model does not discard the later or Christian material.

- `Shekhinah`, `HaMakom`, `HaRachaman`, `HaKadosh Baruch Hu`, and `Ribbono Shel Olam` form a later traditional layer.
- `Yeshua`, `Immanuel`, `Mashiach`, and `Sar Shalom` form a messianic comparative layer.
- This is a source-provenance label, not a judgment that Yeshua is a lesser or non-divine name. Within the manuscript's Christian framework, Yeshua is admitted as a divine personal name because Christians confess Jesus as God; the separate layer prevents that theological premise from being silently imposed on a Hebrew-Bible-only sample.
- The `Yeshua = 386 = 282_12` result remains mathematically intact and must be included in every explicitly Christian-inclusive ranking.
- The 42-letter and 72-name traditions, plus the four YHWH expansions, remain research objects of a different mathematical type.

This separation strengthens rather than weakens interpretive discussion: a result can now be described as biblical, rabbinic, liturgical, Christian-comparative, or Kabbalistic without implying that all five categories were selected by the same textual rule.

## Reproducibility

Run:

```powershell
python scripts/corpus_sensitivity.py
```

The script recalculates every `analysis_hebrew` form directly from the registry and writes:

- `data/corpus_corrected_values.csv`
- `data/corpus_sensitivity_summary.csv`
- `docs/CORPUS_SENSITIVITY.md`

The inherited master table remains preserved for provenance until the manuscript derivations are regenerated from the source-controlled forms.
