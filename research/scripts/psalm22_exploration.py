from __future__ import annotations

import argparse
import csv
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_numerical_claims import (  # noqa: E402
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    gematria,
    is_palindrome,
    to_base,
)
from build_control_pool import (  # noqa: E402
    local_name,
    normalize_hebrew,
    verse_words,
)


RESEARCH_ROOT = PROJECT_ROOT / "research"
DATA_DIR = RESEARCH_ROOT / "data"
REPORT_OUT = RESEARCH_ROOT / "PSALM_22_EXPLORATION.md"
FIRST_WINDOW_OUT = DATA_DIR / "psalm_first_verse_two_word_windows.csv"
SQUARE_WINDOW_OUT = DATA_DIR / "tanakh_two_word_palindromic_square_strings.csv"
EXACT_CONTROL_OUT = DATA_DIR / "ayelet_hashachar_exact_value_controls.csv"
YESHUA_OUT = DATA_DIR / "yeshua_sequence_occurrences.csv"
PSALM_METRIC_OUT = DATA_DIR / "psalm_metrics.csv"
EXPRESSION_OUT = DATA_DIR / "psalm22_expression_variants.csv"

SOURCE_COMMIT = "3d15126fb1ef74867fc1434be1942e837932691f"
TARGET_PHRASE = "אילת השחר"
YESHUA = "ישוע"
FINAL_FORMS = set("ךםןףץ")


@dataclass(frozen=True)
class FirstVerseWindow:
    reference: str
    position: int
    phrase: str
    word_lengths: str
    total_letters: int
    final_form_count: int
    standard_value: int
    standard_base12: str
    standard_base12_palindrome: str
    standard_visible_square_root: str
    mispar_gadol_value: int
    mispar_gadol_base12: str
    mispar_gadol_base12_palindrome: str
    mispar_visible_square_root: str


@dataclass(frozen=True)
class SquareWindow:
    basis: str
    reference: str
    position: int
    phrase: str
    word_lengths: str
    total_letters: int
    final_form_count: int
    value: int
    base12: str
    visible_square_root: int


@dataclass(frozen=True)
class ExactValueControl:
    reference: str
    position: int
    phrase: str
    standard_value: int
    standard_base12: str
    mispar_gadol_value: int
    mispar_gadol_base12: str


@dataclass(frozen=True)
class YeshuaOccurrence:
    reference: str
    token: str
    sequence_position: int
    prefix: str
    sequence: str
    suffix: str
    lemma: str
    base_lemma: str
    morphology: str
    lexical_class: str
    source_file: str


@dataclass(frozen=True)
class PsalmMetric:
    psalm: int
    verse_count_mt: int
    word_count_oshb: int
    word_count_base12: str
    word_count_base12_palindrome: str
    letter_count_oshb: int
    letter_count_base12: str
    letter_count_base12_palindrome: str
    standard_value: int
    standard_base12: str
    standard_base12_palindrome: str
    mispar_gadol_value: int
    mispar_gadol_base12: str
    mispar_gadol_base12_palindrome: str


@dataclass(frozen=True)
class ExpressionVariant:
    label: str
    hebrew: str
    word_count: int
    letter_count: int
    standard_value: int
    standard_base12: str
    standard_base12_palindrome: str
    mispar_gadol_value: int
    mispar_gadol_base12: str
    mispar_gadol_base12_palindrome: str
    contains_yeshua_sequence: str


def source_revision(source: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def visible_square_root(representation: str) -> int | None:
    if not representation.isdigit():
        return None
    displayed = int(representation)
    root = math.isqrt(displayed)
    return root if root * root == displayed else None


def word_data(verse: ET.Element) -> list[tuple[str, ET.Element]]:
    return [
        (normalize_hebrew("".join(word.itertext())), word)
        for word in verse_words(verse)
    ]


def first_verse_windows(psalm_root: ET.Element) -> list[FirstVerseWindow]:
    rows: list[FirstVerseWindow] = []
    first_verses = [
        verse
        for verse in psalm_root.iter()
        if local_name(verse.tag) == "verse"
        and verse.attrib.get("osisID", "").endswith(".1")
    ]
    if len(first_verses) != 150:
        raise ValueError(f"Expected 150 Psalm first verses, found {len(first_verses)}")

    for verse in first_verses:
        words = [normalized for normalized, _ in word_data(verse)]
        for position in range(len(words) - 1):
            pair = words[position : position + 2]
            phrase = " ".join(pair)
            standard = gematria(phrase, STANDARD_VALUES)
            mispar = gematria(phrase, MISPAR_GADOL_VALUES)
            standard_base12 = to_base(standard)
            mispar_base12 = to_base(mispar)
            standard_square = visible_square_root(standard_base12)
            mispar_square = visible_square_root(mispar_base12)
            rows.append(
                FirstVerseWindow(
                    reference=verse.attrib["osisID"],
                    position=position + 1,
                    phrase=phrase,
                    word_lengths="-".join(str(len(word)) for word in pair),
                    total_letters=sum(len(word) for word in pair),
                    final_form_count=sum(char in FINAL_FORMS for char in "".join(pair)),
                    standard_value=standard,
                    standard_base12=standard_base12,
                    standard_base12_palindrome=(
                        "yes" if is_palindrome(standard_base12) else "no"
                    ),
                    standard_visible_square_root=(
                        str(standard_square) if standard_square is not None else ""
                    ),
                    mispar_gadol_value=mispar,
                    mispar_gadol_base12=mispar_base12,
                    mispar_gadol_base12_palindrome=(
                        "yes" if is_palindrome(mispar_base12) else "no"
                    ),
                    mispar_visible_square_root=(
                        str(mispar_square) if mispar_square is not None else ""
                    ),
                )
            )
    return rows


def lexical_class(base_lemma: str) -> str:
    return {
        "3444": "salvation-noun",
        "3442": "Jeshua-proper-name",
        "50": "Abishua-proper-name",
        "474": "Elishua-proper-name",
        "7768": "verb-form",
        "3467": "deliverance-related-form",
        "3443": "proper-name-variant",
    }.get(base_lemma, "other")


def scan_tanakh(
    xml_files: list[Path],
) -> tuple[
    list[SquareWindow],
    list[ExactValueControl],
    list[YeshuaOccurrence],
    dict[str, int],
]:
    square_rows: list[SquareWindow] = []
    exact_rows: list[ExactValueControl] = []
    yeshua_rows: list[YeshuaOccurrence] = []
    counts = Counter()

    for xml_file in xml_files:
        root = ET.parse(xml_file).getroot()
        for verse in (node for node in root.iter() if local_name(node.tag) == "verse"):
            reference = verse.attrib.get("osisID", "")
            data = word_data(verse)
            words = [normalized for normalized, _ in data]

            for normalized, element in data:
                if YESHUA not in normalized:
                    continue
                position = normalized.index(YESHUA)
                lemma = element.attrib.get("lemma", "")
                base_lemma = lemma.split("/")[-1]
                yeshua_rows.append(
                    YeshuaOccurrence(
                        reference=reference,
                        token=normalized,
                        sequence_position=position + 1,
                        prefix=normalized[:position],
                        sequence=YESHUA,
                        suffix=normalized[position + len(YESHUA) :],
                        lemma=lemma,
                        base_lemma=base_lemma,
                        morphology=element.attrib.get("morph", ""),
                        lexical_class=lexical_class(base_lemma),
                        source_file=xml_file.name,
                    )
                )

            for position in range(len(words) - 1):
                pair = words[position : position + 2]
                phrase = " ".join(pair)
                lengths = tuple(len(word) for word in pair)
                finals = sum(char in FINAL_FORMS for char in "".join(pair))
                counts["tanakh_two_word_windows"] += 1
                counts["target_phrase_occurrences"] += int(phrase == TARGET_PHRASE)

                values = (
                    ("standard", gematria(phrase, STANDARD_VALUES)),
                    ("mispar-gadol", gematria(phrase, MISPAR_GADOL_VALUES)),
                )
                for basis, value in values:
                    representation = to_base(value)
                    root_value = visible_square_root(representation)
                    if is_palindrome(representation) and root_value is not None:
                        square_rows.append(
                            SquareWindow(
                                basis=basis,
                                reference=reference,
                                position=position + 1,
                                phrase=phrase,
                                word_lengths=f"{lengths[0]}-{lengths[1]}",
                                total_letters=sum(lengths),
                                final_form_count=finals,
                                value=value,
                                base12=representation,
                                visible_square_root=root_value,
                            )
                        )

                if lengths != (4, 4) or finals != 0:
                    continue
                counts["tanakh_4_4_no_final_windows"] += 1
                standard = values[0][1]
                mispar = values[1][1]
                standard_base12 = to_base(standard)
                mispar_base12 = to_base(mispar)
                counts["tanakh_4_4_standard_palindromes"] += int(
                    is_palindrome(standard_base12)
                )
                counts["tanakh_4_4_mispar_palindromes"] += int(
                    is_palindrome(mispar_base12)
                )
                if standard == 954 or mispar == 954 or phrase == TARGET_PHRASE:
                    exact_rows.append(
                        ExactValueControl(
                            reference=reference,
                            position=position + 1,
                            phrase=phrase,
                            standard_value=standard,
                            standard_base12=standard_base12,
                            mispar_gadol_value=mispar,
                            mispar_gadol_base12=mispar_base12,
                        )
                    )

    return square_rows, exact_rows, yeshua_rows, dict(counts)


def psalm_metrics(psalm_root: ET.Element) -> tuple[list[PsalmMetric], int]:
    chapters: dict[int, list[tuple[str, list[str]]]] = defaultdict(list)
    psalm22_palindromic_verses = 0
    for verse in (node for node in psalm_root.iter() if local_name(node.tag) == "verse"):
        reference = verse.attrib["osisID"]
        chapter = int(reference.split(".")[1])
        words = [normalized for normalized, _ in word_data(verse)]
        chapters[chapter].append((reference, words))

        if chapter == 22:
            text = " ".join(words)
            standard_base12 = to_base(gematria(text, STANDARD_VALUES))
            mispar_base12 = to_base(gematria(text, MISPAR_GADOL_VALUES))
            psalm22_palindromic_verses += int(
                is_palindrome(standard_base12) or is_palindrome(mispar_base12)
            )

    rows: list[PsalmMetric] = []
    for chapter, verses in sorted(chapters.items()):
        words = [word for _, verse_words_list in verses for word in verse_words_list]
        text = " ".join(words)
        word_count = len(words)
        letter_count = sum(len(word) for word in words)
        standard = gematria(text, STANDARD_VALUES)
        mispar = gematria(text, MISPAR_GADOL_VALUES)
        word_base12 = to_base(word_count)
        letter_base12 = to_base(letter_count)
        standard_base12 = to_base(standard)
        mispar_base12 = to_base(mispar)
        rows.append(
            PsalmMetric(
                psalm=chapter,
                verse_count_mt=len(verses),
                word_count_oshb=word_count,
                word_count_base12=word_base12,
                word_count_base12_palindrome=(
                    "yes" if is_palindrome(word_base12) else "no"
                ),
                letter_count_oshb=letter_count,
                letter_count_base12=letter_base12,
                letter_count_base12_palindrome=(
                    "yes" if is_palindrome(letter_base12) else "no"
                ),
                standard_value=standard,
                standard_base12=standard_base12,
                standard_base12_palindrome=(
                    "yes" if is_palindrome(standard_base12) else "no"
                ),
                mispar_gadol_value=mispar,
                mispar_gadol_base12=mispar_base12,
                mispar_gadol_base12_palindrome=(
                    "yes" if is_palindrome(mispar_base12) else "no"
                ),
            )
        )
    return rows, psalm22_palindromic_verses


def expression_variant(label: str, hebrew: str) -> ExpressionVariant:
    normalized_words = [
        normalized
        for raw in hebrew.split()
        if (normalized := normalize_hebrew(raw))
    ]
    normalized = " ".join(normalized_words)
    standard = gematria(normalized, STANDARD_VALUES)
    mispar = gematria(normalized, MISPAR_GADOL_VALUES)
    standard_base12 = to_base(standard)
    mispar_base12 = to_base(mispar)
    return ExpressionVariant(
        label=label,
        hebrew=normalized,
        word_count=len(normalized_words),
        letter_count=sum(len(word) for word in normalized_words),
        standard_value=standard,
        standard_base12=standard_base12,
        standard_base12_palindrome=(
            "yes" if is_palindrome(standard_base12) else "no"
        ),
        mispar_gadol_value=mispar,
        mispar_gadol_base12=mispar_base12,
        mispar_gadol_base12_palindrome=(
            "yes" if is_palindrome(mispar_base12) else "no"
        ),
        contains_yeshua_sequence="yes" if YESHUA in normalized.replace(" ", "") else "no",
    )


def expression_variants() -> list[ExpressionVariant]:
    return [
        expression_variant("Ayelet", "אילת"),
        expression_variant("HaShachar", "השחר"),
        expression_variant("Ayelet HaShachar", TARGET_PHRASE),
        expression_variant("Al Ayelet HaShachar", "על אילת השחר"),
        expression_variant(
            "Complete superscription",
            "למנצח על אילת השחר מזמור לדוד",
        ),
        expression_variant("Yeshua", YESHUA),
        expression_variant("From my salvation", "מישועתי"),
        expression_variant(
            "Opening cry",
            "אלי אלי למה עזבתני",
        ),
    ]


def write_csv(path: Path, rows: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dictionaries = [asdict(row) for row in rows]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dictionaries[0].keys()))
        writer.writeheader()
        writer.writerows(dictionaries)


def variants_table(rows: list[ExpressionVariant]) -> str:
    lines = [
        "| Expression | Hebrew | Standard | Base 12 | MG | Base 12 | Palindrome |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        palindrome = (
            row.standard_base12_palindrome == "yes"
            or row.mispar_gadol_base12_palindrome == "yes"
        )
        lines.append(
            f"| {row.label} | `{row.hebrew}` | {row.standard_value} | "
            f"`{row.standard_base12}` | {row.mispar_gadol_value} | "
            f"`{row.mispar_gadol_base12}` | {'yes' if palindrome else 'no'} |"
        )
    return "\n".join(lines)


def exact_control_table(rows: list[ExactValueControl]) -> str:
    lines = [
        "| Reference | Phrase | Value | Base 12 |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.reference} | `{row.phrase}` | {row.standard_value} | "
            f"`{row.standard_base12}` |"
        )
    return "\n".join(lines)


def write_report(
    first_windows: list[FirstVerseWindow],
    square_windows: list[SquareWindow],
    exact_controls: list[ExactValueControl],
    yeshua_rows: list[YeshuaOccurrence],
    tanakh_counts: dict[str, int],
    metrics: list[PsalmMetric],
    psalm22_palindromic_verses: int,
    variants: list[ExpressionVariant],
) -> None:
    target = next(row for row in first_windows if row.phrase == TARGET_PHRASE)
    first_square_phrases = {
        (row.reference, row.position, row.phrase)
        for row in first_windows
        if (
            row.standard_base12_palindrome == "yes"
            and row.standard_visible_square_root
        )
        or (
            row.mispar_gadol_base12_palindrome == "yes"
            and row.mispar_visible_square_root
        )
    }
    structural = [
        row
        for row in first_windows
        if row.word_lengths == "4-4" and row.final_form_count == 0
    ]
    psalm22 = next(row for row in metrics if row.psalm == 22)
    word_count_palindromes = sum(
        row.word_count_base12_palindrome == "yes" for row in metrics
    )
    whole_psalm_palindromes = sum(
        row.standard_base12_palindrome == "yes"
        or row.mispar_gadol_base12_palindrome == "yes"
        for row in metrics
    )
    yeshua_forms = Counter(row.token for row in yeshua_rows)
    lexical_counts = Counter(row.lexical_class for row in yeshua_rows)
    psalm_occurrences = sum(row.reference.startswith("Ps.") for row in yeshua_rows)
    first_standard_palindromes = sum(
        row.standard_base12_palindrome == "yes" for row in first_windows
    )
    first_mispar_palindromes = sum(
        row.mispar_gadol_base12_palindrome == "yes" for row in first_windows
    )
    structural_standard_palindromes = sum(
        row.standard_base12_palindrome == "yes" for row in structural
    )
    structural_mispar_palindromes = sum(
        row.mispar_gadol_base12_palindrome == "yes" for row in structural
    )
    square_standard = sum(row.basis == "standard" for row in square_windows)
    square_mispar = sum(row.basis == "mispar-gadol" for row in square_windows)
    square_root_26_standard = sum(
        row.basis == "standard" and row.visible_square_root == 26
        for row in square_windows
    )
    square_root_26_mispar = sum(
        row.basis == "mispar-gadol" and row.visible_square_root == 26
        for row in square_windows
    )

    content = f"""# Psalm 22 Exploration

## Status

Post-publication exploratory analysis integrated into manuscript version
`1.1.0`. The archived `v1.0.0` remains unchanged.

## Frozen Source And Search Boundary

The Hebrew calculations use the same locked Open Scriptures Hebrew Bible
revision as the manuscript's matched controls:
`{SOURCE_COMMIT}`. The declared searches are:

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

The complete first-verse scan contains {len(first_windows)} two-word windows.
Of those, {first_standard_palindromes} are standard-value base-12 palindromes
and {first_mispar_palindromes} are Mispar Gadol base-12 palindromes. Palindrome
status alone is therefore not rare.

Exactly {len(first_square_phrases)} first-verse window combines a base-12
palindrome with a visible all-decimal digit string that is a perfect square
under either value system:

| Reference | Phrase | Value | Base 12 | Visible square |
| --- | --- | ---: | ---: | ---: |
| {target.reference} | `{target.phrase}` | {target.standard_value} | `{target.standard_base12}` | `26^2` |

Within the narrower `4-4`, no-final-form stratum, there are {len(structural)}
windows and {structural_standard_palindromes} standard-value palindromes
({structural_mispar_palindromes} under Mispar Gadol). *Ayelet HaShachar* is
the only phrase in that stratum at value 954.

## Whole-Tanakh Controls

The full Tanakh contains {tanakh_counts['tanakh_two_word_windows']:,}
contiguous two-word windows. The palindrome-plus-visible-square condition
occurs {square_standard} times under standard gematria and {square_mispar}
times under Mispar Gadol. A visible square root of 26 occurs
{square_root_26_standard} times under standard gematria and
{square_root_26_mispar} times under Mispar Gadol. Thus the numerical property
is unique within Psalm openings, not within arbitrary Tanakh phrases.

For the exact `4-4`, no-final-form structure, the Tanakh contains
{tanakh_counts['tanakh_4_4_no_final_windows']:,} windows;
{tanakh_counts['tanakh_4_4_standard_palindromes']:,} are standard-value
base-12 palindromes. {len(exact_controls)} windows equal 954:

{exact_control_table(exact_controls)}

The exact lexical phrase `אילת השחר` itself occurs once in the locked Tanakh.

## The Yeshua Sequence

The opening lament contains the normalized token:

`מישועתי`

meaning "from my salvation" or "far from my salvation" in context. Its
letters contain `ישוע` contiguously:

`מ + ישוע + תי`

The complete token has value `836 = 598_12` and is not a palindrome. The
embedded sequence alone is the manuscript's `Yeshua = 386 = 282_12`.

Across the locked Tanakh, {len(yeshua_rows)} tokens in
{len(set(row.reference for row in yeshua_rows))} verses contain `ישוע`, using
{len(yeshua_forms)} normalized token forms. Of these,
{lexical_counts['salvation-noun']} belong to the ordinary salvation noun,
{lexical_counts['Jeshua-proper-name']} to the proper name Jeshua, and
{psalm_occurrences} occur in Psalms. The exact form `מישועתי` occurs once.

The sequence is therefore not a rare letter sequence in biblical Hebrew:
it is built into the normal noun *yeshuah*, "salvation." What is textually
specific is its occurrence in this unique prefixed form, in the same opening
verse whose first clause the Gospels place on Jesus' lips.

## Whole-Psalm Checks And Negative Results

Under the locked OSHB tokenization, Psalm 22 has:

- {psalm22.verse_count_mt} Masoretic verses, including the superscription;
- {psalm22.word_count_oshb} word tokens, giving
  `{psalm22.word_count_base12}_12`, a base-12 palindrome;
- {psalm22.letter_count_oshb} normalized consonants, giving
  `{psalm22.letter_count_base12}_12`, not a palindrome;
- standard total {psalm22.standard_value} =
  `{psalm22.standard_base12}_12`, not a palindrome;
- Mispar Gadol total {psalm22.mispar_gadol_value} =
  `{psalm22.mispar_gadol_base12}_12`, not a palindrome.

The word-count palindrome is one of {word_count_palindromes} among the 150
Psalms, although Psalm 22 is the only Psalm with exactly 253 tokens. Word
counts depend on tokenization and are secondary evidence. No complete Psalm
has a palindromic full-text gematria total in base 12, and Psalm 22 has
{psalm22_palindromic_verses} complete verses with such a total.

The result is therefore localized. It belongs to the recognized two-word
superscription phrase, not to the complete superscription, opening cry, full
verse, or full Psalm:

{variants_table(variants)}

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
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--morphhb-source",
        required=True,
        type=Path,
        help="Path to the locked openscriptures/morphhb checkout",
    )
    args = parser.parse_args()

    source = args.morphhb_source.resolve()
    revision = source_revision(source)
    if revision != SOURCE_COMMIT:
        raise ValueError(f"OSHB source revision {revision} != locked {SOURCE_COMMIT}")
    xml_files = sorted((source / "wlc").glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No wlc/*.xml files under {source}")
    psalm_path = source / "wlc" / "Ps.xml"
    psalm_root = ET.parse(psalm_path).getroot()

    first_windows = first_verse_windows(psalm_root)
    square_windows, exact_controls, yeshua_rows, tanakh_counts = scan_tanakh(xml_files)
    metrics, psalm22_palindromic_verses = psalm_metrics(psalm_root)
    variants = expression_variants()

    if len(first_windows) != 964:
        raise ValueError(f"Expected 964 first-verse windows, found {len(first_windows)}")
    if len(yeshua_rows) != 114:
        raise ValueError(f"Expected 114 Yeshua-sequence tokens, found {len(yeshua_rows)}")
    if sum(row.token == "מישועתי" for row in yeshua_rows) != 1:
        raise ValueError("Expected one exact מישועתי token")
    target_rows = [row for row in first_windows if row.phrase == TARGET_PHRASE]
    if len(target_rows) != 1:
        raise ValueError(f"Expected one Psalm-opening target, found {len(target_rows)}")
    target = target_rows[0]
    if (
        target.reference != "Ps.22.1"
        or target.position != 3
        or target.standard_value != 954
        or target.standard_base12 != "676"
        or target.standard_visible_square_root != "26"
    ):
        raise ValueError(f"Unexpected Psalm 22 target row: {target}")
    first_square_phrases = {
        (row.reference, row.position, row.phrase)
        for row in first_windows
        if (
            row.standard_base12_palindrome == "yes"
            and row.standard_visible_square_root
        )
        or (
            row.mispar_gadol_base12_palindrome == "yes"
            and row.mispar_visible_square_root
        )
    }
    expected_square_phrases = {("Ps.22.1", 3, TARGET_PHRASE)}
    if first_square_phrases != expected_square_phrases:
        raise ValueError(f"Unexpected Psalm-opening square hits: {first_square_phrases}")
    if tanakh_counts.get("target_phrase_occurrences") != 1:
        raise ValueError("Expected one exact Ayelet HaShachar phrase in the Tanakh")
    if len(exact_controls) != 7 or any(
        row.standard_value != 954 or row.mispar_gadol_value != 954
        for row in exact_controls
    ):
        raise ValueError("Expected seven exact value-954 structural controls")

    write_csv(FIRST_WINDOW_OUT, first_windows)
    write_csv(SQUARE_WINDOW_OUT, square_windows)
    write_csv(EXACT_CONTROL_OUT, exact_controls)
    write_csv(YESHUA_OUT, yeshua_rows)
    write_csv(PSALM_METRIC_OUT, metrics)
    write_csv(EXPRESSION_OUT, variants)
    write_report(
        first_windows,
        square_windows,
        exact_controls,
        yeshua_rows,
        tanakh_counts,
        metrics,
        psalm22_palindromic_verses,
        variants,
    )
    for path in (
        REPORT_OUT,
        FIRST_WINDOW_OUT,
        SQUARE_WINDOW_OUT,
        EXACT_CONTROL_OUT,
        YESHUA_OUT,
        PSALM_METRIC_OUT,
        EXPRESSION_OUT,
    ):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
