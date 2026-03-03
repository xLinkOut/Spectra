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
    r"\b\d{4,}\b|"
    r"\*+"        # bare asterisks (e.g. "Massaua Ci*")
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
    text = re.sub(r"\s+", " ", text).strip(" .|,;:-*")

    # Deduplicate repeated words (e.g. "Massaua Ci Massaua Ci Torino" → "Massaua Ci Torino")
    words = text.split()
    seen: list[str] = []
    for w in words:
        if w.lower() not in [s.lower() for s in seen]:
            seen.append(w)
    text = " ".join(seen)

    if not text:
        return raw.strip()

    # Title-case for readability
    return text.title()


# ── Keyword rules ────────────────────────────────────────────────

_KEYWORD_RULES: list[tuple[re.Pattern, str, str | None]] = [
    # (pattern, category, optional clean_name override)

    # ── Digital Subscriptions ──────────────────────────────────
    (re.compile(r"(?i)\bnetflix\b"), "Digital Subscriptions", "Netflix"),
    (re.compile(r"(?i)\bspotify\b"), "Digital Subscriptions", "Spotify"),
    (re.compile(r"(?i)apple\.com|\bitunes\b|apple\s+(?:music|tv|one|store)\b"), "Digital Subscriptions", "Apple"),
    (re.compile(r"(?i)\b(?:disney\s*\+|disneyplus)\b"), "Digital Subscriptions", "Disney+"),
    (re.compile(r"(?i)\bamazon\s*prime\b"), "Digital Subscriptions", "Amazon Prime"),
    (re.compile(r"(?i)\byoutube\s*premium\b"), "Digital Subscriptions", "YouTube Premium"),
    (re.compile(r"(?i)\b(?:chatgpt|openai)\b"), "Digital Subscriptions", "OpenAI"),
    (re.compile(r"(?i)\bgithub\b"), "Digital Subscriptions", "GitHub"),
    (re.compile(r"(?i)\bdropbox\b"), "Digital Subscriptions", "Dropbox"),
    (re.compile(r"(?i)\b(?:google\s*(?:one|storage|workspace|cloud))\b"), "Digital Subscriptions", "Google"),
    (re.compile(r"(?i)\bicloud\b"), "Digital Subscriptions", "iCloud"),
    (re.compile(r"(?i)\badobe\b"), "Digital Subscriptions", "Adobe"),
    (re.compile(r"(?i)\b(?:microsoft\s*365|office\s*365)\b"), "Digital Subscriptions", "Microsoft 365"),
    (re.compile(r"(?i)\bnotion\b"), "Digital Subscriptions", "Notion"),
    (re.compile(r"(?i)\bslack\b"), "Digital Subscriptions", "Slack"),
    (re.compile(r"(?i)\bzoom\b"), "Digital Subscriptions", "Zoom"),
    (re.compile(r"(?i)\blinkedin\s*premium\b"), "Digital Subscriptions", "LinkedIn Premium"),
    (re.compile(r"(?i)\b(?:tv\.apple|apple\s*tv)\b"), "Digital Subscriptions", "Apple TV+"),
    (re.compile(r"(?i)\bdazn\b"), "Digital Subscriptions", "DAZN"),
    (re.compile(r"(?i)\b(?:paramount\+|paramount\s*plus)\b"), "Digital Subscriptions", "Paramount+"),
    (re.compile(r"(?i)\b(?:sky\s*(?:glass|tv|italia|q))\b"), "Digital Subscriptions", "Sky"),
    (re.compile(r"(?i)\b(?:porkbun|namecheap|godaddy|hover\.com|gandi\.net|registro\.it)\b"), "Digital Subscriptions", None),
    (re.compile(r"(?i)\b(?:nordvpn|expressvpn|protonvpn|surfshark)\b"), "Digital Subscriptions", None),
    (re.compile(r"(?i)\b(?:aws|amazon\s?web\s?services|gcp|azure|digitalocean|heroku|linode|vultr|hetzner|ovh|vercel|netlify|cloudflare)\b"), "Digital Subscriptions", None),
    (re.compile(r"(?i)\b(?:1password|bitwarden|lastpass)\b"), "Digital Subscriptions", None),
    (re.compile(r"(?i)\btwitch\b"), "Digital Subscriptions", "Twitch"),
    (re.compile(r"(?i)\b(?:claude\.ai|anthropic)\b"), "Digital Subscriptions", "Anthropic"),
    (re.compile(r"(?i)\bmidjourney\b"), "Digital Subscriptions", "Midjourney"),
    (re.compile(r"(?i)\bsetapp\b"), "Digital Subscriptions", "Setapp"),

    # ── Transport ─────────────────────────────────────────────
    (re.compile(r"(?i)\buber\b(?!\s*eat)"), "Transport", "Uber"),
    (re.compile(r"(?i)\bbolt\b(?!\s*food)"), "Transport", "Bolt"),
    (re.compile(r"(?i)\b(?:lift|lyft)\b"), "Transport", "Lyft"),
    (re.compile(r"(?i)\b(?:cabify|grab|gokjek|didi|ola|yandex\s?go)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:trenitalia|italo\s*(?:treno|treni|spa)?)\b"), "Transport", None),
    (re.compile(r"(?i)\bflixbus\b"), "Transport", "FlixBus"),
    (re.compile(r"(?i)\b(?:atm\s*milano|tper|gtt\s|ztl)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:tfl(?: travel charge)?|mta|ratp|bvg|sncf|renfe|sbb|cff|ffs|ns)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:eni\s*station|q8|agip|ip\s*station|totalenergies|shell|bp)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:autostrad|telepass|viacard)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:taxi|taxify|radiotaxi)\b"), "Transport", "Taxi"),
    (re.compile(r"(?i)\b(?:googlemaps|google\s*maps|waze)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:treno|ferrovi|rail|db\s*bahn|amtrak|ferrovia)\b"), "Transport", None),
    (re.compile(r"(?i)\b(?:monopattino|bici|bike|scooter|free\s*now|tier|lime|bird)\b"), "Transport", None),

    # ── Travel ────────────────────────────────────────────────
    (re.compile(r"(?i)\b(?:ryanair|easyjet|vueling|wizzair|lufthansa|alitalia|ita\s*airways)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:turkish\s*airlines|klm|air\s*france|british\s*airways|iberia|tap)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:trip\.com|booking[\s.]?com|airbnb|expedia|hotels[\s.]?com|trivago|lastminute)\b"), "Travel", None),
    # Hotel patterns — match BEFORE utilities to avoid conflicts
    (re.compile(r"(?i)\b(?:hotel\b|\balbergo\b|\bb&b\b|\bbed\s+and\s+breakfast\b|\bhostel)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:resort\b|\bmotel\b|\blodge\b|\bcamping\b|\bvilla)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:aeroporto|airport|aerport|aeroport)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:hertz|avis|europcar|sixt|enterprise\s*rent|maggiore)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:traghetto|traghetti|tirrenia|grimaldi\s*lines|gnv|ferry|ferries)\b"), "Travel", None),
    (re.compile(r"(?i)\b(?:frecciarossa|frecciargento|frecciabianca|intercity)\b"), "Travel", "Trenitalia"),

    # ── Entertainment ─────────────────────────────────────────
    (re.compile(r"(?i)\b(?:cinema|cine\s|cityplex|uci\s*cinema|the\s*space\s*cinema|pathe|vue)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:stadio|stadium|bigliett|arena)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:concerto|concert|teatro|opera|museum|musei|musee)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:ticketone|ticketmaster|vivaticket|eventbrite)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:steam|playstation|xbox|nintendo|epic\s*games|psn)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:ac\s*milan|inter\s*milan|juventus|roma\s*calcio|napoli\s*calcio)\b"), "Entertainment", None),
    (re.compile(r"(?i)\b(?:parco\s*(?:divertimenti|tematico|acquatico)|gardaland|mirabilandia|disneyland)\b"), "Entertainment", None),

    # ── Groceries (Specific category extracted from Food) ─────
    (re.compile(r"(?i)\b(?:esselunga|coop\s|conad|lidl|aldi|eurospin|pam\s|penny)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:tesco|sainsbury|asda|waitrose|morrisons|marks\s?(?:&|and)\s?spencer)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:rewe|edeka|kaufland|netto|migros|denner)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:auchan|leclerc|intermarche|monoprix|carrefour)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:mercadona|pingo\s?doce|continente)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:walmart|target|kroger|whole\s?foods|trader\s?joe|seven\s*eleven|7-eleven)\b"), "Groceries", None),
    (re.compile(r"(?i)\b(?:supermercato|supermkt|grocery|alimentari|supermarket|markt|market|supermercado|hypermarché)\b"), "Groceries", None),

    # ── Food & Dining ─────────────────────────────────────────
    (re.compile(r"(?i)\b(?:uber\s*eats?|deliveroo|glovo|just\s*eats?|foodora|doordash|grubhub|postmates|rappi|pedidosya|swiggy|zomato|ubereats)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\bstarbucks\b"), "Food & Dining", "Starbucks"),
    (re.compile(r"(?i)\b(?:mc\s?donalds?|burger\s?king|kfc|wendys?|subway\s*sandwich)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:ristorante|trattoria|pizzeria|osteria|enoteca|restaurant)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:bar\s+|\bcaffe|\bcaffè|\bcafeteria|\bpasticceria|\bcafe\b|\Bcafé\b\bcosta\s*coffee|greggs|tim\s*hortons|dunkin)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:sushi|ramen|sushiko|udon|yakitori)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:poke|poké)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:bakery|panetteria|forno|boulangerie|patisserie|pret\s*a\s*manger)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:gelateria|gelato)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\b(?:domino|papa\s*johns?|pizza\s*hut)\b"), "Food & Dining", None),
    (re.compile(r"(?i)\bautogrill\b"), "Food & Dining", "Autogrill"),
    (re.compile(r"(?i)\bwolt\b"), "Food & Dining", "Wolt"),

    # ── Shopping ──────────────────────────────────────────────
    (re.compile(r"(?i)\bamzn|amazon\b(?!\s*prime|.*web\s*services)"), "Shopping", "Amazon"),
    (re.compile(r"(?i)\b(?:mercadolibre|shopee|lazada|rakuten|aliexpress|temu|shein|asos|zalando)\b"), "Shopping", None),
    (re.compile(r"(?i)\bikea\b"), "Shopping", "IKEA"),
    (re.compile(r"(?i)\b(?:zara|h&m|uniqlo|decathlon|primark|c&a|muji|macys)\b"), "Shopping", None),
    (re.compile(r"(?i)\b(?:mediaworld|unieuro|euronics|trony|best\s*buy)\b"), "Shopping", None),
    (re.compile(r"(?i)\b(?:epay|erbolario|kiko|sephora|nyx|mac\s*cosmetics)\b"), "Shopping", None),
    (re.compile(r"(?i)\b(?:farfetch|yoox|net-a-porter)\b"), "Shopping", None),
    (re.compile(r"(?i)\betsy\b"), "Shopping", "Etsy"),
    (re.compile(r"(?i)\bvinted\b"), "Shopping", "Vinted"),
    (re.compile(r"(?i)\bebay\b"), "Shopping", "eBay"),
    (re.compile(r"(?i)\b(?:action\s*store|tiger\s*store|normal\s*store)\b"), "Shopping", None),
    (re.compile(r"(?i)\b(?:obi\s|leroy\s*merlin|brico|home\s*depot|b&q)\b"), "Shopping", None),
    (re.compile(r"(?i)\bpaypal\b(?!.*subscription|.*abbonament)"), "Shopping", "PayPal"),

    # ── Health & Fitness ──────────────────────────────────────
    (re.compile(r"(?i)\b(?:farmacia|pharmacy|pharmacie|apotheke|boots|superdrug|watsons|cvs|walgreens)\b"), "Health", None),
    (re.compile(r"(?i)\b(?:rossmann|dm(?:-drogerie)?)\b"), "Health", None),
    (re.compile(r"(?i)\b(?:palestra|gym|fitness|wellness|crossfit|pilates|yoga|gymshark)\b"), "Health & Fitness", None),
    (re.compile(r"(?i)\b(?:dottore|medico|clinica|ospedale|poliambulatorio|clinic|hospital)\b"), "Health", None),
    (re.compile(r"(?i)\b(?:dentist|odontoiatr|dental)\b"), "Health", None),
    (re.compile(r"(?i)\b(?:psicologo|psicologa|terapista|fisioterapi|physio)\b"), "Health", None),
    (re.compile(r"(?i)\b(?:optik|ottic|visita\s*oculistica|optician)\b"), "Health", None),

    # ── Insurance ─────────────────────────────────────────────
    (re.compile(r"(?i)\b(?:assicurazion|insurance|axa|allianz|generali|zurich|unipol|unipolsai|direct\s*line|bupa)\b"), "Insurance", None),
    (re.compile(r"(?i)\b(?:rc\s*auto|polizza|premio\s*assicurat)\b"), "Insurance", None),

    # ── Utilities ─────────────────────────────────────────────
    (re.compile(r"(?i)\b(?:vodafone|tim\s|wind\s*tre|iliad|fastweb|tiscali|o2|ee|at&t|verizon|t-mobile|orange|bouygues|movistar)\b"), "Utilities", None),
    (re.compile(r"(?i)\b(?:enel\b|\ba2a\b|\biren\b|\bhera\b|\bacea\b|\bsnam\b|\btelecom\b|british\s*gas|edf)\b"), "Utilities", None),
    (re.compile(r"(?i)\b(?:gas\s*(?:luce|natural|delivery)|bolletta|utenza|water|electricity)\b"), "Utilities", None),
    (re.compile(r"(?i)\b(?:affitto|canone\s*locazione|pigione|noleggio\s*appartamento|rent)\b"), "Utilities", None),
    (re.compile(r"(?i)\b(?:condominio|spese\s*condominiali)\b"), "Utilities", None),
    (re.compile(r"(?i)\b(?:internet\s*provider|fibra|adsl|broadband)\b"), "Utilities", None),

    # ── Cash Deposit / ATM ────────────────────────────────────
    (re.compile(r"(?i)\b(?:versamento\s*contanti|versamento\s*su\s*sportello|deposito\s*contanti|cash\s*deposit)\b"), "Cash Deposit", "Cash Deposit"),
    (re.compile(r"(?i)\b(?:prelievo|bancomat|atm\s*cash|cash\s*withdrawal)\b"), "Cash Withdrawal", "ATM Withdrawal"),
    (re.compile(r"(?i)\bprelievo\s*con\s*carta\b"), "Cash Withdrawal", "ATM Withdrawal"),

    # ── Taxes & Government ────────────────────────────────────
    (re.compile(r"(?i)\b(?:f24|agenzia\s*entrate|tasse|tributi|imu|tari|tasi|hmrc|irs|tax)\b"), "Taxes", None),
    (re.compile(r"(?i)\b(?:comune\s*di|regione\s*|provincia\s*di|asl|council)\b"), "Taxes", None),
    (re.compile(r"(?i)\b(?:bollo\s*auto|pra|dvla)\b"), "Taxes", None),

    # ── Education ─────────────────────────────────────────────
    (re.compile(r"(?i)\b(?:universit|politecnico|accademia|corso\s+di|college|school)\b"), "Education", None),
    (re.compile(r"(?i)\b(?:udemy|coursera|skillshare|duolingo|busuu)\b"), "Education", None),
    (re.compile(r"(?i)\b(?:libri|feltrinelli|mondadori|amazon\s*books|ibs\.it|waterstones|barnes\s*&\s*noble)\b"), "Education", None),

    # ── Income & Transfers ────────────────────────────────────
    (re.compile(r"(?i)\b(?:stipendio|salary|payroll|retribuzione|wages)\b"), "Salary", None),
    (re.compile(r"(?i)\b(?:pensione|pension)\b"), "Pension", None),
    (re.compile(r"(?i)\b(?:bonifico\s*(?:ricevuto|in\s*entrata)|accredito\s*bonifico)\b"), "Transfer In", None),
    (re.compile(r"(?i)\b(?:rimborso|refund|cashback)\b"), "Reimbursement", None),
    (re.compile(r"(?i)\brevolut\s*\**\s*top\s?-\s?up\b"), "Transfer", "Revolut Top-Up"),
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
        income_cats = {
            "Salary", "Pension", "Transfer In", "Cash Deposit", "Cash Withdrawal",
            "Other Income", "Investment Return", "Reimbursement", "Taxes",
        }
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
