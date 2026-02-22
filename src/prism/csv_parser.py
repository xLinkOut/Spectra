"""Universal CSV parser — reads bank export files from any institution."""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("prism.csv_parser")


# ── Column name mappings ──────────────────────────────────────────
# Maps common bank column names → standard field names

_DATE_ALIASES = {
    "data", "date", "data operazione", "data contabile",
    "data valuta", "booking date", "transaction date",
    "data movimento", "data addebito", "data accredito",
    "data esecuzione", "datum",
}
_DESCRIPTION_ALIASES = {
    "descrizione", "description", "causale", "dettagli",
    "details", "merchant", "commerciante", "motivo",
    "remittance", "transaction description", "narrative",
    "wording", "reference", "note", "notes", "memo",
    "causale pagamento", "descrizione operazione",
}
_AMOUNT_ALIASES = {
    "importo", "amount", "valore", "value", "ammontare",
    "importo eur", "amount eur", "saldo", "totale",
    "dare/avere", "accredito/addebito", "entrate/uscite",
    "net amount",
}
_CREDIT_ALIASES = {
    "accredito", "credit", "entrate", "income", "in", "avere",
    "entrata", "versamento",
}
_DEBIT_ALIASES = {
    "addebito", "debit", "uscite", "expense", "out", "dare",
    "uscita", "prelievo", "pagamento",
}


@dataclass
class ParsedTransaction:
    """A single transaction parsed from a CSV row."""
    id: str         # hash of date+description+amount (for dedup)
    date: str       # YYYY-MM-DD
    amount: float   # negative = expense, positive = income
    currency: str
    raw_description: str
    counterpart: str = ""


def _normalize(s: str) -> str:
    """Lowercase, strip, remove extra spaces."""
    return re.sub(r"\s+", " ", s.strip().lower())


def _detect_delimiter(sample: str) -> str:
    """Detect CSV delimiter from a sample of the file."""
    counts = {
        ";": sample.count(";"),
        ",": sample.count(","),
        "\t": sample.count("\t"),
        "|": sample.count("|"),
    }
    return max(counts, key=lambda k: counts[k])


def _parse_amount(raw: str) -> float:
    """Parse an amount string handling Italian and English formats."""
    # Remove currency symbols and whitespace
    s = re.sub(r"[€$£\s]", "", raw.strip())
    # Strip leading '+' (some banks like ISyBank use +1.500,00 for credits)
    positive = s.startswith("+")
    s = s.lstrip("+")
    # Handle negative in parentheses: (100.00) → -100.00
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    # Italian format: 1.234,56 → 1234.56
    if re.match(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$", s):
        s = s.replace(".", "").replace(",", ".")
    # Remove thousands separator (English: 1,234.56)
    elif re.match(r"^-?\d{1,3}(,\d{3})*(\.\d+)?$", s):
        s = s.replace(",", "")
    # Simple comma as decimal: 1234,56
    else:
        s = s.replace(",", ".")
    try:
        result = float(s)
        return abs(result) if positive else result
    except ValueError:
        raise ValueError(f"Cannot parse amount: {raw!r}")


def _parse_date(raw: str) -> str:
    """Normalize date to YYYY-MM-DD from common formats."""
    s = raw.strip()
    # Try common formats
    formats = [
        (r"^(\d{4})-(\d{2})-(\d{2})$", "{1}-{2}-{3}"),       # ISO: 2026-02-22
        (r"^(\d{2})/(\d{2})/(\d{4})$", "{3}-{2}-{1}"),       # EU: 22/02/2026
        (r"^(\d{2})-(\d{2})-(\d{4})$", "{3}-{2}-{1}"),       # EU: 22-02-2026
        (r"^(\d{2})\.(\d{2})\.(\d{4})$", "{3}-{2}-{1}"),     # DE: 22.02.2026
        (r"^(\d{2})/(\d{2})/(\d{2})$", "20{3}-{2}-{1}"),     # Short: 22/02/26
        (r"^(\d{8})$", "{0:4}-{0:2}-{0:2}"),                  # Compact: 20260222
    ]
    for pattern, _ in formats:
        m = re.match(pattern, s)
        if m:
            groups = m.groups()
            if len(groups) == 3:
                # Detect if first group is year
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                else:
                    return f"{groups[2]}-{groups[1]}-{groups[0]}"
    # Compact: 20260222
    if re.match(r"^\d{8}$", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return s  # Return as-is if we can't parse


def _make_id(date: str, description: str, amount: float) -> str:
    """Create a stable ID for dedup (hash of key fields)."""
    import hashlib
    key = f"{date}|{description.strip().lower()}|{amount:.2f}"
    return "CSV-" + hashlib.sha1(key.encode()).hexdigest()[:16]


def _map_columns(headers: list[str]) -> dict[str, int]:
    """Map standard field names to column indices."""
    mapping: dict[str, int] = {}
    normalized = [_normalize(h) for h in headers]

    for i, h in enumerate(normalized):
        if h in _DATE_ALIASES:
            mapping.setdefault("date", i)
        elif h in _DESCRIPTION_ALIASES:
            mapping.setdefault("description", i)
        elif h in _AMOUNT_ALIASES:
            mapping.setdefault("amount", i)
        elif h in _CREDIT_ALIASES:
            mapping.setdefault("credit", i)
        elif h in _DEBIT_ALIASES:
            mapping.setdefault("debit", i)

    return mapping


def parse_csv(
    file_path: str | Path,
    currency: str = "EUR",
    encoding: str = "utf-8-sig",  # utf-8-sig handles BOM from Excel exports
) -> list[ParsedTransaction]:
    """Parse a bank CSV export into a list of ParsedTransaction objects.

    Supports any bank format — auto-detects:
    - Delimiter (comma, semicolon, tab, pipe)
    - Column names (Italian and English)
    - Amount format (Italian/English number format, debit/credit split)
    - Date format (ISO, European, compact)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    # Read raw bytes to detect delimiter and encoding
    try:
        raw = path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        raw = path.read_text(encoding="latin-1")

    delimiter = _detect_delimiter(raw[:2000])
    logger.info("Detected delimiter: %r for file: %s", delimiter, path.name)

    reader = csv.reader(raw.splitlines(), delimiter=delimiter)
    rows = list(reader)

    # Skip empty leading rows (some banks add bank name / account info before headers)
    header_idx = 0
    for i, row in enumerate(rows):
        if len([c for c in row if c.strip()]) >= 3:
            header_idx = i
            break

    headers = rows[header_idx]
    data_rows = rows[header_idx + 1:]
    col = _map_columns(headers)

    logger.info(
        "Headers: %s → mapped: %s", headers, col
    )

    if "date" not in col:
        raise ValueError(
            f"Cannot find date column in CSV headers: {headers}\n"
            "Please check that your CSV has a date column."
        )
    if "description" not in col:
        raise ValueError(
            f"Cannot find description column in CSV headers: {headers}"
        )
    if "amount" not in col and ("credit" not in col and "debit" not in col):
        raise ValueError(
            f"Cannot find amount column in CSV headers: {headers}"
        )

    transactions: list[ParsedTransaction] = []
    skipped = 0

    for row_num, row in enumerate(data_rows, start=header_idx + 2):
        # Skip empty rows
        if not any(c.strip() for c in row):
            continue
        # Skip rows that are too short
        if len(row) <= max(col.values()):
            continue

        try:
            raw_date = row[col["date"]].strip()
            if not raw_date:
                continue

            date = _parse_date(raw_date)
            description = row[col["description"]].strip() if "description" in col else ""

            # Amount: either a single column or split credit/debit
            if "amount" in col:
                raw_amount = row[col["amount"]].strip()
                if not raw_amount:
                    continue
                amount = _parse_amount(raw_amount)
            else:
                raw_credit = row[col["credit"]].strip() if "credit" in col else ""
                raw_debit = row[col["debit"]].strip() if "debit" in col else ""
                credit = _parse_amount(raw_credit) if raw_credit else 0.0
                debit = _parse_amount(raw_debit) if raw_debit else 0.0
                # Credits are positive, debits are negative
                amount = abs(credit) - abs(debit)

            tx_id = _make_id(date, description, amount)

            transactions.append(
                ParsedTransaction(
                    id=tx_id,
                    date=date,
                    amount=amount,
                    currency=currency,
                    raw_description=description,
                )
            )
        except (ValueError, IndexError) as e:
            logger.warning("Skipping row %d: %s — %s", row_num, row, e)
            skipped += 1

    logger.info(
        "Parsed %d transactions (%d skipped) from %s",
        len(transactions), skipped, path.name,
    )
    return transactions
