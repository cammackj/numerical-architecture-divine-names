from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import (
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    collapse_base12_text,
    collapse_decimal,
    gematria,
    is_palindrome,
    make_rows,
    to_base,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"


NOTABLE_CONSTANTS = {
    3: "AB/minimal triad",
    7: "seven",
    8: "agency collapse",
    12: "completion collapse",
    13: "one/echad value",
    22: "Hebrew alphabet/YHWH base-12 signature",
    26: "YHWH standard",
    31: "El standard",
    37: "Genesis-factor candidate",
    42: "forty-two",
    52: "BEN/YHWH doubled",
    72: "seventy-two",
    73: "Chokmah/wisdom candidate",
    91: "YHWH+Adonai/Amen",
    137: "fine-structure candidate",
    153: "fish/triangular-17 candidate",
    314: "pi/Shaddai",
    345: "El Shaddai/Moses/3-4-5",
    358: "Mashiach/Nachash",
    386: "Yeshua",
    655: "Tanakh 929 -> 655_12 prefix candidate",
}

BASE12_STRINGS = {
    "22": "YHWH base-12 signature",
    "42": "forty-two string",
    "72": "seventy-two string",
    "222": "triple-2 identity string",
    "282": "Yeshua bridge string",
    "393": "Ehyeh Asher Ehyeh palindrome",
    "515": "El Olam Mispar Gadol palindrome",
    "7A7": "HaKadosh Baruch Hu Mispar Gadol palindrome",
    "313": "Elohei HaShamayim standard palindrome",
    "44": "BEN standard palindrome",
    "655": "Tanakh chapter prefix string",
}


COMPONENT_TESTS = [
    ("Ehyeh", "אהיה", "component", "I AM alone"),
    ("Asher", "אשר", "component", "middle term in Ehyeh formula"),
    ("Ehyeh + Ehyeh", "אהיה אהיה", "component-combination", "duplicated I AM"),
    ("Ehyeh Asher", "אהיה אשר", "component-combination", "partial formula"),
    ("Ehyeh Asher Ehyeh", "אהיה אשר אהיה", "existing-row", "full formula"),
    ("Roi", "ראי", "component", "component of El Roi"),
    ("Gibbor", "גבור", "component", "component of El Gibbor"),
    ("El Roi", "אל ראי", "existing-row", "God who sees"),
    ("El Gibbor", "אל גבור", "existing-row", "Mighty God"),
    ("YHWH Yireh", "יהוה יראה", "candidate-title", "YHWH sees/provides"),
    ("Elyon", "עליון", "component", "Most High component"),
    ("El Elyon", "אל עליון", "existing-row", "God Most High"),
    ("Immanuel", "עמנואל", "existing-row", "God with us"),
    ("Olam", "עולם", "component", "eternity/world component"),
    ("HaNe'eman", "הנאמן", "component", "faithful component"),
    ("El Olam", "אל עולם", "existing-row", "Everlasting God"),
    ("El HaNe'eman", "אל הנאמן", "existing-row", "Faithful God"),
    ("El Yeshuati", "אל ישועתי", "existing-row", "God of my salvation"),
    ("Shaddai", "שדי", "existing-row", "Shaddai alone"),
    ("El Shaddai", "אל שדי", "existing-row", "El Shaddai"),
    ("Shekhinah", "שכינה", "existing-row", "presence term"),
    ("HaShekhinah", "השכינה", "candidate-variant", "article form of Shekhinah"),
    ("HaKavod", "הכבוד", "candidate-title", "the Glory"),
    ("El HaKavod", "אל הכבוד", "existing-row", "God of glory"),
    ("Gadol", "גדול", "component", "great"),
    ("El Gadol", "אל גדול", "candidate-variant", "God great / great God without article"),
    ("HaGadol", "הגדול", "component", "the great"),
    ("El HaGadol", "אל הגדול", "existing-row", "The great God"),
    ("HaNorah", "הנורא", "component", "the awesome"),
    ("El HaNorah", "אל הנורא", "existing-row", "The awesome God"),
    ("HaShamayim", "השמים", "component", "the heavens"),
    ("HaAretz", "הארץ", "component", "the earth"),
    ("El HaShamayim", "אל השמים", "existing-row", "God of heaven"),
    ("El HaAretz", "אל הארץ", "existing-row", "God of earth"),
    ("Elohei", "אלוהי", "component", "construct prefix God of"),
    ("Avraham", "אברהם", "component", "patriarch"),
    ("Yitzchak", "יצחק", "component", "patriarch"),
    ("Yaakov", "יעקב", "component", "patriarch"),
    ("Elohei Avraham", "אלוהי אברהם", "existing-row", "God of Abraham"),
    ("Elohei Yitzchak", "אלוהי יצחק", "existing-row", "God of Isaac"),
    ("Elohei Yaakov", "אלוהי יעקב", "existing-row", "God of Jacob"),
    ("Yah", "יה", "candidate-title", "short divine name"),
    ("YHWH", "יהוה", "existing-row", "Tetragrammaton"),
    ("Adonai", "אדני", "existing-row", "Lord"),
    ("YHWH Adonai", "יהוה אדני", "candidate-combination", "YHWH + Adonai union"),
    ("YHWH Elohim", "יהוה אלהים", "candidate-combination", "creation formula"),
    ("YHWH Nissi", "יהוה נסי", "candidate-title", "YHWH my banner"),
    ("YHWH Shalom", "יהוה שלום", "candidate-title", "YHWH peace"),
    ("YHWH Tzevaot", "יהוה צבאות", "candidate-title", "YHWH of hosts"),
    ("El Chai", "אל חי", "candidate-title", "Living God"),
    ("Melekh HaOlam", "מלך העולם", "candidate-title", "King of the universe"),
    ("Avinu Malkeinu", "אבינו מלכנו", "candidate-title", "Our Father, our King"),
    ("Kadosh Yisrael", "קדוש ישראל", "candidate-title", "Holy One of Israel"),
]


@dataclass
class ConstantHit:
    source: str
    name: str
    hebrew: str
    basis: str
    value: str
    hit_type: str
    note: str


@dataclass
class SharedValue:
    basis: str
    value: int
    base12: str
    collapse: int
    names: str
    note: str


@dataclass
class ComponentRow:
    name: str
    hebrew: str
    category: str
    note: str
    standard: int
    mispar_gadol: int
    base12_standard: str
    base12_mispar_gadol: str
    collapse_standard: int
    collapse_mispar_gadol: int
    collapse_base12_standard: int
    collapse_base12_mispar_gadol: int
    standard_base10_palindrome: str
    mispar_base10_palindrome: str
    standard_base12_palindrome: str
    mispar_base12_palindrome: str
    constants_and_multiples: str
    pattern_notes: str


def factors(value: int) -> list[tuple[int, int]]:
    current = abs(value)
    out: list[tuple[int, int]] = []
    divisor = 2
    while divisor * divisor <= current:
        count = 0
        while current % divisor == 0:
            current //= divisor
            count += 1
        if count:
            out.append((divisor, count))
        divisor += 1 if divisor == 2 else 2
    if current > 1:
        out.append((current, 1))
    return out


def factor_text(value: int) -> str:
    return " * ".join(
        f"{prime}^{power}" if power > 1 else str(prime)
        for prime, power in factors(value)
    )


def constants_and_multiples(standard: int, mispar: int) -> list[str]:
    hits: list[str] = []
    for basis, value in [("standard", standard), ("mispar-gadol", mispar)]:
        for constant, label in NOTABLE_CONSTANTS.items():
            if value == constant:
                hits.append(f"{basis}={constant} ({label})")
            elif value % constant == 0 and 1 < value // constant <= 20:
                hits.append(f"{basis}={value // constant}*{constant} ({label})")
    return hits


def base12_hits(name: str, hebrew: str, standard: int, mispar: int) -> list[ConstantHit]:
    hits: list[ConstantHit] = []
    for basis, value, base12_text in [
        ("standard-base12", standard, to_base(standard)),
        ("mispar-gadol-base12", mispar, to_base(mispar)),
    ]:
        if base12_text in BASE12_STRINGS:
            hits.append(
                ConstantHit(
                    source="corpus",
                    name=name,
                    hebrew=hebrew,
                    basis=basis,
                    value=base12_text,
                    hit_type="base12-string",
                    note=BASE12_STRINGS[base12_text],
                )
            )
    return hits


def corpus_constant_hits() -> list[ConstantHit]:
    hits: list[ConstantHit] = []
    for row in make_rows():
        for basis, value in [
            ("standard", row.computed_standard),
            ("mispar-gadol", row.computed_mispar_gadol),
        ]:
            for constant, label in NOTABLE_CONSTANTS.items():
                if value == constant:
                    hits.append(
                        ConstantHit("corpus", row.name, row.hebrew, basis, str(value), "exact", label)
                    )
                elif value % constant == 0 and 1 < value // constant <= 20:
                    hits.append(
                        ConstantHit(
                            "corpus",
                            row.name,
                            row.hebrew,
                            basis,
                            str(value),
                            "multiple",
                            f"{value // constant} * {constant} ({label})",
                        )
                    )
        hits.extend(base12_hits(row.name, row.hebrew, row.computed_standard, row.computed_mispar_gadol))
    return hits


def shared_values() -> list[SharedValue]:
    out: list[SharedValue] = []
    rows = make_rows()
    for basis, getter in [
        ("standard", lambda row: row.computed_standard),
        ("mispar-gadol", lambda row: row.computed_mispar_gadol),
        ("base12-standard", lambda row: row.base12_standard),
        ("base12-mispar-gadol", lambda row: row.base12_mispar_gadol),
    ]:
        grouped: dict[str, list[str]] = {}
        for row in rows:
            grouped.setdefault(str(getter(row)), []).append(row.name)
        for value_text, names in sorted(grouped.items(), key=lambda item: (len(item[0]), item[0])):
            if len(names) < 2:
                continue
            if basis.startswith("base12"):
                decimal_value = int(value_text, 12)
                base12_text = value_text
                collapse = collapse_base12_text(value_text)
            else:
                decimal_value = int(value_text)
                base12_text = to_base(decimal_value)
                collapse = collapse_decimal(decimal_value)
            note = ""
            if set(names) == {"El Roi", "El Gibbor"}:
                note = "Exact seeing/might pair; also matched by candidate YHWH Yireh."
            elif set(names) == {"El Elyon", "Immanuel"}:
                note = "Transcendence/immanence pair."
            elif set(names) == {"El Olam", "El HaNe’eman"}:
                note = "Eternal/faithful stability pair."
            elif set(names) == {"El Yeshuati", "El HaNe’eman"}:
                note = "Salvation/faithfulness cross-link through Mispar Gadol."
            out.append(
                SharedValue(
                    basis=basis,
                    value=decimal_value,
                    base12=base12_text,
                    collapse=collapse,
                    names="; ".join(names),
                    note=note,
                )
            )
    return out


def component_pattern_notes(name: str, standard: int, mispar: int, base12_standard: str) -> list[str]:
    notes: list[str] = []
    if name == "Ehyeh":
        notes.append("I AM alone has no strict 8/12 or palindrome marker.")
    if name == "Ehyeh + Ehyeh":
        notes.append("Duplicated I AM gives exact 42.")
    if name == "Ehyeh Asher Ehyeh":
        notes.append("Full formula gives strict 12 and base-12 palindrome; combination matters.")
    if name in {"El Roi", "El Gibbor", "YHWH Yireh"} and standard == 242:
        notes.append("Shares 242 with seeing/provision/might pattern.")
    if name in {"El Elyon", "Immanuel"} and standard == 197:
        notes.append("Shares 197 transcendence/immanence pair.")
    if name in {"El Olam", "El HaNe'eman"} and standard == 177:
        notes.append("Shares 177 eternal/faithful pair.")
    if name == "El Yeshuati" and standard == 827:
        notes.append("Shares 827 with El HaNe'eman under Mispar Gadol.")
    if name == "Elohei":
        notes.append("Construct prefix equals 52, matching BEN/YHWH doubled.")
    if name == "Avraham" and standard == 248:
        notes.append("Avraham is 8 * El.")
    if name == "Yitzchak" and standard == 208:
        notes.append("Yitzchak is 8 * YHWH.")
    if name == "Yaakov" and standard == 182:
        notes.append("Yaakov is 7 * YHWH and matches El Kana.")
    if name == "YHWH Adonai" and standard == 91:
        notes.append("YHWH + Adonai gives 91 and 77_12.")
    if name == "YHWH Tzevaot" and standard == 525:
        notes.append("Candidate title gives strict 12 and base-10 palindrome.")
    if name == "Melekh HaOlam":
        notes.append("Candidate title has standard base-12 palindrome 181_12 and Mispar Gadol collapse 12.")
    if name == "Avinu Malkeinu":
        notes.append("Candidate title hits 8 in every tested layer.")
    if name == "HaKavod" and standard == 37:
        notes.append("The Glory alone gives exact 37.")
    if name == "El Gadol" and standard == 74:
        notes.append("No-article variant gives 2 * 37.")
    if name == "HaNorah" and standard == 262:
        notes.append("Component alone is a base-10 palindrome.")
    if base12_standard == "72":
        notes.append("Standard value converts to 72_12.")
    return notes


def component_rows() -> list[ComponentRow]:
    rows: list[ComponentRow] = []
    for name, hebrew, category, note in COMPONENT_TESTS:
        standard = gematria(hebrew, STANDARD_VALUES)
        mispar = gematria(hebrew, MISPAR_GADOL_VALUES)
        base12_standard = to_base(standard)
        base12_mispar = to_base(mispar)
        rows.append(
            ComponentRow(
                name=name,
                hebrew=hebrew,
                category=category,
                note=note,
                standard=standard,
                mispar_gadol=mispar,
                base12_standard=base12_standard,
                base12_mispar_gadol=base12_mispar,
                collapse_standard=collapse_decimal(standard),
                collapse_mispar_gadol=collapse_decimal(mispar),
                collapse_base12_standard=collapse_base12_text(base12_standard),
                collapse_base12_mispar_gadol=collapse_base12_text(base12_mispar),
                standard_base10_palindrome="yes" if is_palindrome(str(standard)) else "no",
                mispar_base10_palindrome="yes" if is_palindrome(str(mispar)) else "no",
                standard_base12_palindrome="yes" if is_palindrome(base12_standard) else "no",
                mispar_base12_palindrome="yes" if is_palindrome(base12_mispar) else "no",
                constants_and_multiples="; ".join(constants_and_multiples(standard, mispar)),
                pattern_notes="; ".join(component_pattern_notes(name, standard, mispar, base12_standard)),
            )
        )
    return rows


def write_csv(path: Path, rows: list[object]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def table_shared(rows: list[SharedValue]) -> str:
    selected = [row for row in rows if row.note]
    lines = [
        "| Basis | Value | Base-12 | Collapse | Names | Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in selected:
        lines.append(
            f"| {row.basis} | {row.value} | {row.base12} | {row.collapse} | {row.names} | {row.note} |"
        )
    return "\n".join(lines)


def table_components(rows: list[ComponentRow], names: list[str]) -> str:
    lookup = {row.name: row for row in rows}
    lines = [
        "| Name | Hebrew | Std | MG | B12 Std/MG | Collapses | Pal? | Constants / Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in names:
        row = lookup[name]
        collapses = (
            f"{row.collapse_standard}/{row.collapse_mispar_gadol}/"
            f"{row.collapse_base12_standard}/{row.collapse_base12_mispar_gadol}"
        )
        pals = []
        if row.standard_base10_palindrome == "yes":
            pals.append("std10")
        if row.mispar_base10_palindrome == "yes":
            pals.append("mg10")
        if row.standard_base12_palindrome == "yes":
            pals.append("std12")
        if row.mispar_base12_palindrome == "yes":
            pals.append("mg12")
        notes = "; ".join(part for part in [row.constants_and_multiples, row.pattern_notes] if part)
        lines.append(
            f"| {row.name} | {row.hebrew} | {row.standard} | {row.mispar_gadol} | "
            f"{row.base12_standard}/{row.base12_mispar_gadol} | {collapses} | "
            f"{', '.join(pals) if pals else '-'} | {notes or '-'} |"
        )
    return "\n".join(lines)


def write_report(shared: list[SharedValue], components: list[ComponentRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    content = f"""# Exploratory Mathematical Pattern Mining

This report was generated by `scripts/exploratory_pattern_mining.py`.

This is a prospecting document, not a manuscript-claim document. Its job is to keep broader mathematical leads visible so the cleanup does not become too narrow.

## Outputs

- `data/exploratory_constant_hits.csv`
- `data/exploratory_shared_values.csv`
- `data/exploratory_component_tests.csv`

## Strongest Newly Surfaced Patterns

### 1. Elohim Contains A Hidden 72 In Base 12

`Elohim / אלהים = 86_10 = 72_12`

The paper already notices the Mispar Gadol palindrome `646`, but the standard value's base-12 form is a direct `72_12` string. That may connect `Elohim` to the 72-name/emanation domain without changing its current Mispar Gadol argument.

### 2. Ehyeh Alone Does Not Work The Same Way The Full Formula Works

`Ehyeh / אהיה = 21`

It has no strict 8/12 collapse or palindrome marker under the current rules.

But:

- `אהיה + אהיה = 42`
- `אהיה אשר אהיה = 543 = 393_12`
- the full formula has strict decimal 12-collapse and a base-12 palindrome

So `I AM THAT I AM` appears to be a genuine combination effect. The full formula is doing something that `I AM` alone does not do.

### 3. A 242 Seeing/Might/Provision Pattern

The existing corpus already has:

- `El Roi / אל ראי = 242`
- `El Gibbor / אל גבור = 242`

A candidate missing title also lands there:

- `YHWH Yireh / יהוה יראה = 242`

All three are base-10 palindromes and strict 8-collapse forms. This is one of the strongest cross-title leads because it joins seeing, provision, and might around the same value.

### 4. Shared-Value Pairs Are More Important Than Expected

{table_shared(shared)}

### 5. 37 / 73 / 137 Constants Appear In Places Worth Testing

Potentially meaningful hits:

- `HaKavod / הכבוד = 37`
- `El Gadol / אל גדול = 74 = 2 * 37`
- `HaAretz / הארץ = 296 = 8 * 37`
- `Olam / עולם = 146 = 2 * 73`
- `HaNe'eman / הנאמן = 146 = 2 * 73`
- `El De'ot / אל דעות = 511 = 7 * 73 = 2^9 - 1`
- `Sar Shalom / שר שלום = 876 = 12 * 73`
- `שם בן מ״ב` under Mispar Gadol gives `1644 = 12 * 137`

These should be handled carefully. `37`, `73`, and `137` can become overfit magnets, but the knowledge/wisdom/peace links around `73` are interesting enough to test.

### 6. Patriarchal Pattern Around YHWH / El Multiples

The `Elohei...` prefix itself is:

`אלוהי = 52 = 2 * 26`

That means the construct prefix is already a YHWH-doubled / BEN value.

Component patterns:

- `Avraham / אברהם = 248 = 8 * 31`
- `Yitzchak / יצחק = 208 = 8 * 26`
- `Yaakov / יעקב = 182 = 7 * 26`
- `Elohei Yitzchak / אלוהי יצחק = 260 = 10 * 26`
- `Elohei Yaakov / אלוהי יעקב = 234 = 9 * 26`

This looks like a real cross-pattern between patriarch titles and the YHWH/El constants.

### 7. Candidate Titles Worth Testing For Inclusion

These are not automatically additions to the corpus. They are candidates for a controlled supplemental table.

{table_components(components, [
    "Yah",
    "YHWH Adonai",
    "YHWH Elohim",
    "YHWH Yireh",
    "YHWH Shalom",
    "YHWH Tzevaot",
    "El Chai",
    "Melekh HaOlam",
    "Avinu Malkeinu",
    "HaKavod",
    "HaNorah",
])}

## Combined-Versus-Component Cases

{table_components(components, [
    "Ehyeh",
    "Ehyeh + Ehyeh",
    "Ehyeh Asher",
    "Ehyeh Asher Ehyeh",
    "Shaddai",
    "El Shaddai",
    "Roi",
    "Gibbor",
    "El Roi",
    "El Gibbor",
    "YHWH Yireh",
    "Elohei",
    "Avraham",
    "Yitzchak",
    "Yaakov",
    "Elohei Avraham",
    "Elohei Yitzchak",
    "Elohei Yaakov",
])}

## Guardrails For Manuscript Use

- Treat this as hypothesis generation until checked against a controlled comparison corpus.
- Do not include a title merely because it produces a pleasing number; require textual/liturgical warrant.
- Keep component effects separate from primary-name results.
- Watch for cross-base ambiguity, especially with `655` as a decimal value versus `655_12` as a notation string.
- Prefer exact equalities and repeated cross-title structures over isolated factor coincidences.
"""
    (DOCS_DIR / "EXPLORATORY_PATTERN_MINING.md").write_text(content, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    constant_hits = corpus_constant_hits()
    shared = shared_values()
    components = component_rows()
    write_csv(DATA_DIR / "exploratory_constant_hits.csv", constant_hits)
    write_csv(DATA_DIR / "exploratory_shared_values.csv", shared)
    write_csv(DATA_DIR / "exploratory_component_tests.csv", components)
    write_report(shared, components)
    print(f"wrote {DATA_DIR / 'exploratory_constant_hits.csv'}")
    print(f"wrote {DATA_DIR / 'exploratory_shared_values.csv'}")
    print(f"wrote {DATA_DIR / 'exploratory_component_tests.csv'}")
    print(f"wrote {DOCS_DIR / 'EXPLORATORY_PATTERN_MINING.md'}")


if __name__ == "__main__":
    main()
