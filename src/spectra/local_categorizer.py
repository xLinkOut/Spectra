"""Offline local categoriser — rules + merchant memory + fuzzy match."""

from __future__ import annotations

import logging
import re
from typing import Any

from spectra.ai import CategorisedTransaction

logger = logging.getLogger("spectra.local")


# ── Merchant name extraction ─────────────────────────────────────

_STRIP_PREFIXES = re.compile(
    r"(?i)^(?:"
    r"POS\s*\d*\s*|"
    r"ADDEBITO\s+SDD\s+|"
    r"ADDEBITO\s+DIRETTO\s+|"
    r"PAGAMENTO\s+(?:SU\s+POS\s+(?:ESTERO\s+)?)?|"
    r"PRELIEVO\s+(?:BANCOMAT\s+)?|"
    r"COMMISSIONE\s+|"
    r"CANONE\s+|"
    r"ACCREDITO\s+|"
    r"BONIFICO\s+(?:ISTANTANEO\s+)?(?:DA\s+VOI\s+DISPOSTO\s+)?A\s+FAVORE\s+DI\s+|"
    r"BONIFICO\s+(?:ISTANTANEO\s+)?A\s+VOSTRO\s+FAVORE\s+DISPOSTO\s+DA\s+|"
    r"RICARICA\s+(?:TELEFONICA\s+)?"
    r")"
)

_STRIP_SUFFIXES = re.compile(
    r"(?i)(?:"
    r"\s+(?:IT|DE|FR|ES|NL|GB|US|EU|COM|SPA|SRL|SARL|GMBH|LTD|INC|AG|AB|BV|SA)\s*$|"
    r"\s+\d{2}/\d{2}/\d{2,4}$|"
    r"\s+CARTA\s.*$|"
    r"\s+ATM\s+\d+.*$|"
    r"\s+VIA\s+.*$"
    r")"
)

_STRIP_NOISE = re.compile(
    r"(?i)(?:"
    r"\bCarta\s+n\.?\s*\d*[\*X]+[\d\*X\s]+\b|"
    r"\b[A-Z0-9]{15,}\b|"
    r"\bABI\s+\d+\b|"
    r"\bCAB\s+\d+\b|"
    r"\bCOD\.?\s*\d+/?\d*\b|"
    r"\(\s*ctv\..*?\)|"
    r"\b\d{2}[/.]\d{2}[/.]\d{2,4}\b|"
    r"\b\d{4,}\b"
    r")"
)


def _extract_merchant_name(raw: str) -> str:
    """Extract a clean merchant name from a raw banking description."""
    text = raw.strip()

    # Strip banking prefixes
    text = _STRIP_PREFIXES.sub("", text)

    # Strip noise (card masks, trace IDs, dates, long numbers)
    text = _STRIP_NOISE.sub(" ", text)

    # Strip suffixes (country codes, legal forms, trailing dates)
    text = _STRIP_SUFFIXES.sub("", text)

    # Collapse whitespace and pipes
    text = re.sub(r"\s*\|\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .|,;:-")

    if not text:
        return raw.strip()

    # Title-case for readability
    return text.title()


# ── Keyword rules ────────────────────────────────────────────────

_KEYWORD_RULES: list[tuple[re.Pattern, str, str | None]] = [
    # (pattern, category, optional clean_name override)
    # ── Digital Subscriptions ──
    (re.compile(r"(?i)\bnetflix\b"), "Digital Subscriptions", "Netflix"),
    (re.compile(r"(?i)\bspotify\b"), "Digital Subscriptions", "Spotify"),
    (re.compile(r"(?i)\bapple\.com|itunes|apple\s+(?:music|tv|one|store)\b"), "Digital Subscriptions", "Apple"),
    (re.compile(r"(?i)\bdisney\s*\+|disneyplus\b"), "Digital Subscriptions", "Disney+"),
    (re.compile(r"(?i)\bamazon\s*prime\b"), "Digital Subscriptions", "Amazon Prime"),
    (re.compile(r"(?i)\byoutube\s*premium\b"), "Digital Subscriptions", "YouTube Premium"),
    (re.compile(r"(?i)\bchatgpt|openai\b"), "Digital Subscriptions", "OpenAI"),
    (re.compile(r"(?i)\bgithub\b"), "Digital Subscriptions", "GitHub"),
    (re.compile(r"(?i)\bdropbox\b"), "Digital Subscriptions", "Dropbox"),
    (re.compile(r"(?i)\bgoogle\s*(?:one|storage|cloud)\b"), "Digital Subscriptions", "Google One"),
    (re.compile(r"(?i)\bicloud\b"), "Digital Subscriptions", "iCloud"),
    (re.compile(r"(?i)\badobe\b"), "Digital Subscriptions", "Adobe"),
    (re.compile(r"(?i)\bmicrosoft\s*365|office\s*365\b"), "Digital Subscriptions", "Microsoft 365"),
    (re.compile(r"(?i)\bnotion\b"), "Digital Subscriptions", "Notion"),

    # ── Transport ──
    (re.compile(r"(?i)\buber\b(?!\s*eat)"), "Transport", "Uber"),
    (re.compile(r"(?i)\bbolt\b(?!\s*food)"), "Transport", "Bolt"),
    (re.compile(r"(?i)\blift|lyft\b"), "Transport", "Lyft"),
    (re.compile(r"(?i)\btrenitalia\b"), "Transport", "Trenitalia"),
    (re.compile(r"(?i)\bitalo\s*(?:treno|spa)?\b"), "Transport", "Italo"),
    (re.compile(r"(?i)\bflixbus\b"), "Transport", "FlixBus"),
    (re.compile(r"(?i)\batm\s*milano\b"), "Transport", "ATM Milano"),
    (re.compile(r"(?i)\beni\s*station|q8|agip|ip\s*station|totalenergies|shell\b"), "Transport", None),
    (re.compile(r"(?i)\bautostrad|telepass\b"), "Transport", None),
    (re.compile(r"(?i)\btaxi\b"), "Transport", "Taxi"),

    # ── Food & Dining ──
    (re.compile(r"(?i)\buber\s*eat|deliveroo|glovo|just\s*eat\b"), "Food & Dining", None),
    (re.compile(r"(?i)\bstarbucks\b"), "Food & Dining", "Starbucks"),
    (re.compile(r"(?i)\bmcdonald|burger\s*king|kfc\b"), "Food & Dining", None),
    (re.compile(r"(?i)\bristorante|trattoria|pizzeria|osteria|bar\s|caffè|caffe\b"), "Food & Dining", None),
    (re.compile(r"(?i)\besselunga|coop\s|conad|lidl|aldi|eurospin|carrefour|pam\b"), "Food & Dining", None),

    # ── Shopping ──
    (re.compile(r"(?i)\bamazon\b(?!\s*prime)"), "Shopping", "Amazon"),
    (re.compile(r"(?i)\bikea\b"), "Shopping", "IKEA"),
    (re.compile(r"(?i)\bzara|h&m|uniqlo|decathlon|zalando\b"), "Shopping", None),
    (re.compile(r"(?i)\bmediaworld|unieuro|euronics\b"), "Shopping", None),

    # ── Travel ──
    (re.compile(r"(?i)\bryanair|easyjet|vueling|wizzair|lufthansa|alitalia|ita\s*airways\b"), "Travel", None),
    (re.compile(r"(?i)\bbooking\.com|airbnb|expedia|hotels\.com\b"), "Travel", None),

    # ── Health ──
    (re.compile(r"(?i)\bfarmacia|pharmacy|pharmacie\b"), "Health", None),
    (re.compile(r"(?i)\bpalestra|gym|fitness\b"), "Health & Fitness", None),

    # ── Insurance ──
    (re.compile(r"(?i)\bassicurazion|insurance|axa|allianz|generali|zurich|unipol\b"), "Insurance", None),

    # ── Utilities ──
    (re.compile(r"(?i)\bvodafone|tim\s|wind\s*tre|iliad|fastweb|enel|a2a|iren|hera\b"), "Utilities", None),

    # ── Income (amount > 0 checked separately, but keyword also helps) ──
    (re.compile(r"(?i)\bstipendio|salary|payroll|retribuzione\b"), "Salary", None),
    (re.compile(r"(?i)\bpensione|pension\b"), "Pension", None),
]


def _match_keyword(description: str) -> tuple[str, str | None] | None:
    """Try to match a description against keyword rules.

    Returns (category, clean_name_override) or None.
    """
    for pattern, category, clean_override in _KEYWORD_RULES:
        if pattern.search(description):
            return category, clean_override
    return None


# ── Fuzzy matching ───────────────────────────────────────────────


def _fuzzy_match(
    name: str,
    known_merchants: dict[str, str],
    threshold: int = 85,
) -> tuple[str, str] | None:
    """Find the closest known merchant using fuzzy string matching.

    Returns (matched_merchant_name, category) or None.
    """
    if not known_merchants or not name:
        return None

    try:
        from rapidfuzz import fuzz
    except ImportError:
        logger.debug("rapidfuzz not installed — skipping fuzzy match")
        return None

    best_score = 0
    best_merchant = ""
    best_category = ""

    for merchant, category in known_merchants.items():
        score = fuzz.token_sort_ratio(name.lower(), merchant.lower())
        if score > best_score:
            best_score = score
            best_merchant = merchant
            best_category = category

    if best_score >= threshold:
        logger.debug("Fuzzy match: %r → %r (score=%d)", name, best_merchant, best_score)
        return best_merchant, best_category

    return None


# ── Public API ───────────────────────────────────────────────────


def categorise_local(
    transactions: list[dict[str, Any]],
    existing_categories: list[str],
    merchant_db: dict[str, str],
    ml_classifier: Any | None = None,
) -> list[CategorisedTransaction]:
    """Categorise transactions using the local deterministic cascade.

    Parameters
    ----------
    transactions:
        List of dicts with keys: raw_description, amount, currency, date
    existing_categories:
        Categories already present in the spreadsheet (used for context).
    merchant_db:
        Dict of {clean_name: category} from the local DB.
    ml_classifier:
        Optional trained sklearn Pipeline for fallback classification.

    Returns
    -------
    List of CategorisedTransaction objects.
    """
    import hashlib

    if not transactions:
        logger.info("No transactions to categorise")
        return []

    logger.info("Categorising %d transaction(s) locally", len(transactions))

    results: list[CategorisedTransaction] = []
    stats = {"exact": 0, "fuzzy": 0, "keyword": 0, "ml": 0, "fallback": 0}

    for t in transactions:
        raw = t["raw_description"]
        amount = float(t.get("amount", 0))
        currency = t.get("currency", "EUR")
        date = t.get("date", "")

        # Generate ID
        raw_id = f"{date}:{raw}:{amount}"
        txn_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()

        # Step 1: Extract clean merchant name
        clean_name = _extract_merchant_name(raw)

        # Step 2: Exact merchant memory
        if clean_name in merchant_db:
            category = merchant_db[clean_name]
            stats["exact"] += 1
            logger.debug("Exact match: %r → %s", clean_name, category)
        else:
            # Step 3: Fuzzy match against known merchants
            fuzzy_result = _fuzzy_match(clean_name, merchant_db)
            if fuzzy_result:
                matched_name, category = fuzzy_result
                clean_name = matched_name  # Use the canonical name
                stats["fuzzy"] += 1
            else:
                # Step 4: Keyword rules
                kw_result = _match_keyword(raw)
                if kw_result:
                    category, name_override = kw_result
                    if name_override:
                        clean_name = name_override
                    stats["keyword"] += 1
                    logger.debug("Keyword match: %r → %s", raw[:50], category)
                else:
                    # Step 5: Optional ML classifier
                    if ml_classifier is not None:
                        try:
                            from spectra.ml_classifier import predict
                            pred_cat, confidence = predict(ml_classifier, raw)
                            if confidence >= 0.6:
                                category = pred_cat
                                stats["ml"] += 1
                                logger.debug("ML match: %r → %s (%.0f%%)", raw[:50], category, confidence * 100)
                            else:
                                category = "Uncategorized"
                                stats["fallback"] += 1
                        except Exception:
                            category = "Uncategorized"
                            stats["fallback"] += 1
                    else:
                        # Step 6: Fallback
                        category = "Uncategorized"
                        stats["fallback"] += 1

        # Income override: if positive amount and not already an income category
        income_cats = {"Salary", "Pension", "Transfer In", "Cash Deposit", "Other Income", "Investment Return"}
        if amount > 0 and category not in income_cats and category != "Uncategorized":
            category = "Other Income"

        recurring = ""
        results.append(
            CategorisedTransaction(
                id=txn_id,
                original_description=raw,
                clean_name=clean_name,
                category=category,
                amount=amount,
                currency=currency,
                date=date,
                recurring=recurring,
                original_amount=None,
                original_currency=None,
            )
        )

    logger.info(
        "Local categorisation: %d exact, %d fuzzy, %d keyword, %d ML, %d fallback",
        stats["exact"], stats["fuzzy"], stats["keyword"], stats["ml"], stats["fallback"],
    )


    return results
