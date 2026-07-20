# Psalm 22 Exploration

## Status

Post-publication exploratory analysis integrated into manuscript version
`1.1.0`. The archived `v1.0.0` remains unchanged.

## Frozen Source And Search Boundary

The Hebrew calculations use the same locked Open Scriptures Hebrew Bible
revision as the manuscript's matched controls:
`3d15126fb1ef74867fc1434be1942e837932691f`. The declared searches are:

1. every contiguous two-word window in the first Masoretic verse of all 150
   Psalms;
2. every contiguous two-word window in the locked Tanakh;
3. every normalized Tanakh token containing the consonantal sequence `ישוע`;
4. whole-Psalm and whole-verse metrics under the same tokenization.

The Psalm's Hebrew text and superscription are visible at Sefaria:
https://www.sefaria.org/Psalms.22?lang=he

## Ayelet HaShachar

The recognized two-word designation in the superscription is:

`אילת השחר`

Its two words have standard values 441 and 513. Together:

`441 + 513 = 954 = 676_12`

The phrase has eight normalized consonants in a `4 + 4` structure and no final
forms, so standard gematria and Mispar Gadol are identical. Its base-12
representation is an exact palindrome.

There is also a narrower cross-basis fact:

`676 = 26^2`

This means the visible base-12 digit string is the ordinary decimal square of
YHWH's value 26. It does **not** mean `954 = 26^2`; `676_12` denotes 954.

## Psalm-Opening Controls

The complete first-verse scan contains 964 two-word windows.
Of those, 70 are standard-value base-12 palindromes
and 75 are Mispar Gadol base-12 palindromes. Palindrome
status alone is therefore not rare.

Exactly 1 first-verse window combines a base-12
palindrome with a visible all-decimal digit string that is a perfect square
under either value system:

| Reference | Phrase | Value | Base 12 | Visible square |
| --- | --- | ---: | ---: | ---: |
| Ps.22.1 | `אילת השחר` | 954 | `676` | `26^2` |

Within the narrower `4-4`, no-final-form stratum, there are 79
windows and 7 standard-value palindromes
(7 under Mispar Gadol). *Ayelet HaShachar* is
the only phrase in that stratum at value 954.

## Whole-Tanakh Controls

The full Tanakh contains 282,294
contiguous two-word windows. The palindrome-plus-visible-square condition
occurs 571 times under standard gematria and 502
times under Mispar Gadol. A visible square root of 26 occurs
84 times under standard gematria and
158 times under Mispar Gadol. Thus the numerical property
is unique within Psalm openings, not within arbitrary Tanakh phrases.

For the exact `4-4`, no-final-form structure, the Tanakh contains
15,636 windows;
1,539 are standard-value
base-12 palindromes. 7 windows equal 954:

| Reference | Phrase | Value | Base 12 |
| --- | --- | ---: | ---: |
| 1Sam.2.20 | `אשתו ואמר` | 954 | `676` |
| 2Chr.3.15 | `ראשו אמות` | 954 | `676` |
| Exod.24.17 | `אכלת בראש` | 954 | `676` |
| Ezek.41.9 | `אמות ואשר` | 954 | `676` |
| Hag.1.15 | `לחדש בששי` | 954 | `676` |
| Judg.12.7 | `וימת יפתח` | 954 | `676` |
| Ps.22.1 | `אילת השחר` | 954 | `676` |

The exact lexical phrase `אילת השחר` itself occurs once in the locked Tanakh.

## The Yeshua Sequence

The opening lament contains the normalized token:

`מישועתי`

meaning "from my salvation" or "far from my salvation" in context. Its
letters contain `ישוע` contiguously:

`מ + ישוע + תי`

The complete token has value `836 = 598_12` and is not a palindrome. The
embedded sequence alone is the manuscript's `Yeshua = 386 = 282_12`.

Across the locked Tanakh, 114 tokens in
113 verses contain `ישוע`, using
28 normalized token forms. Of these,
72 belong to the ordinary salvation noun,
29 to the proper name Jeshua, and
43 occur in Psalms. The exact form `מישועתי` occurs once.

The sequence is therefore not a rare letter sequence in biblical Hebrew:
it is built into the normal noun *yeshuah*, "salvation." What is textually
specific is its occurrence in this unique prefixed form, in the same opening
verse whose first clause the Gospels place on Jesus' lips.

## Whole-Psalm Checks And Negative Results

Under the locked OSHB tokenization, Psalm 22 has:

- 32 Masoretic verses, including the superscription;
- 253 word tokens, giving
  `191_12`, a base-12 palindrome;
- 1012 normalized consonants, giving
  `704_12`, not a palindrome;
- standard total 59640 =
  `2A620_12`, not a palindrome;
- Mispar Gadol total 81080 =
  `3AB08_12`, not a palindrome.

The word-count palindrome is one of 12 among the 150
Psalms, although Psalm 22 is the only Psalm with exactly 253 tokens. Word
counts depend on tokenization and are secondary evidence. No complete Psalm
has a palindromic full-text gematria total in base 12, and Psalm 22 has
0 complete verses with such a total.

The result is therefore localized. It belongs to the recognized two-word
superscription phrase, not to the complete superscription, opening cry, full
verse, or full Psalm:

| Expression | Hebrew | Standard | Base 12 | MG | Base 12 | Palindrome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Ayelet | `אילת` | 441 | `309` | 441 | `309` | no |
| HaShachar | `השחר` | 513 | `369` | 513 | `369` | no |
| Ayelet HaShachar | `אילת השחר` | 954 | `676` | 954 | `676` | yes |
| Al Ayelet HaShachar | `על אילת השחר` | 1054 | `73A` | 1054 | `73A` | no |
| Complete superscription | `למנצח על אילת השחר מזמור לדוד` | 1609 | `B21` | 1609 | `B21` | no |
| Yeshua | `ישוע` | 386 | `282` | 386 | `282` | yes |
| From my salvation | `מישועתי` | 836 | `598` | 836 | `598` | no |
| Opening cry | `אלי אלי למה עזבתני` | 696 | `4A0` | 696 | `4A0` | no |

## Christian Textual Context

The USCCB notes on Matthew 27 identify Psalm 22 as the Old Testament passage
most frequently drawn upon in that Passion narrative. They connect Matthew
27:35, 39-40, 43, and 46 with Psalm 22:19, 8, 9, and 2. John 19:24 explicitly
quotes Psalm 22:19, and Hebrews 2:12 applies Psalm 22:23 to Jesus.

- https://bible.usccb.org/bible/matthew/27
- https://bible.usccb.org/bible/john/19
- https://bible.usccb.org/bible/hebrews/2

The chapter label itself is convention-sensitive: this is Psalm 22 under
Masoretic numbering and Psalm 21 under the Septuagint convention.
https://www.oca.org/liturgics/outlines/septuagint-numbering-psalms

The phrase-level and lexical findings survive that numbering difference.

## Evidential Assessment

The strongest result is the superscription phrase. It is a recognized textual
unit, not a synthetic rearrangement; it is stable under both declared value
systems; and it is the only two-word Psalm-opening window whose base-12
palindrome visibly reproduces a perfect square, specifically `26^2`.

The `ישוע` containment is theologically resonant but statistically less rare.
It should be described as an exact consonantal containment inside the word for
"my salvation," not as a hidden proper name or a second gematria palindrome.

Both findings were recognized after extensive exploration. The finite scans
define their comparison sets but do not convert them into confirmatory tests.
Their source, cross-basis wording, negative variants, and post-hoc status are
now documented beside them in version `1.1.0` without
opening an unrestricted search through every biblical phrase.
