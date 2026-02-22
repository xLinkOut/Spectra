"""Pipeline orchestrator — CSV → AI → Google Sheets."""

from __future__ import annotations

import argparse
import logging
import sys

from prism.ai import CategorisedTransaction, categorise
from prism.config import Settings, load_settings
from prism.csv_parser import ParsedTransaction, parse_csv
from prism.db import BookmarkDB
from prism.sheets import SheetsClient

logger = logging.getLogger("prism")


def run(settings: Settings, csv_file: str, currency: str, dry_run: bool) -> None:
    """Process a bank CSV export → AI → Google Sheets."""

    # ── Step 1: Parse CSV ────────────────────────────────────────
    logger.info("📂 Reading CSV: %s", csv_file)
    parsed = parse_csv(csv_file, currency=currency)

    if not parsed:
        logger.info("✅ No transactions found in CSV")
        return

    # ── Step 2: Filter duplicates ────────────────────────────────
    with BookmarkDB(settings.db_path) as db:
        new_txns = [t for t in parsed if not db.is_seen(t.id)]
        logger.info("📥 %d total, %d new", len(parsed), len(new_txns))

        if not new_txns:
            logger.info("✅ All transactions already imported — nothing to do")
            return

        # ── Step 3: Read existing categories from Sheet ──────────
        if dry_run:
            existing_categories: list[str] = []
        else:
            sheets = SheetsClient(
                spreadsheet_id=settings.spreadsheet_id,
                credentials_b64=settings.google_sheets_credentials_b64,
                credentials_file=settings.google_sheets_credentials_file,
            )
            existing_categories = sheets.get_existing_categories()

        logger.info("📂 Existing categories: %s", existing_categories or "(none)")

        # ── Step 4: Categorise via LLM ───────────────────────────
        flat = [
            {
                "raw_description": t.raw_description,
                "amount": t.amount,
                "currency": t.currency,
                "date": t.date,
            }
            for t in new_txns
        ]

        if settings.ai_provider == "gemini":
            api_key, model = settings.gemini_api_key, settings.gemini_model
        else:
            api_key, model = settings.openai_api_key, settings.openai_model

        categorised = categorise(
            flat, existing_categories,
            provider=settings.ai_provider, api_key=api_key, model=model,
        )

        if not categorised:
            logger.warning("⚠️  LLM returned no results")
            return

        # ── Step 5: Write or print ───────────────────────────────
        if dry_run:
            print(f"\n{'='*72}")
            print(f" PRISM — {len(categorised)} categorised transactions")
            print(f"{'='*72}")
            for t in categorised:
                sign = "+" if t.amount > 0 else ""
                print(f"\n  {t.date}  {sign}{t.amount:.2f} {t.currency}")
                print(f"  Original : {t.original_description}")
                print(f"  Clean    : {t.clean_name}")
                print(f"  Category : {t.category}")
            print(f"\n{'='*72}\n")
            logger.info("🧪 DRY RUN — nothing written")
        else:
            sheets.append_transactions(categorised)
            db.mark_seen_batch([t.id for t in new_txns])
            logger.info("✅ Done — %d rows written to Google Sheets", len(categorised))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="prism",
        description="Prism — Bank CSV → AI → Google Sheets",
    )
    parser.add_argument("--file", "-f", required=True, help="Path to bank CSV export")
    parser.add_argument("--currency", default="EUR", help="Currency code (default: EUR)")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing to Sheets")

    args = parser.parse_args()
    settings = load_settings()

    try:
        run(settings, csv_file=args.file, currency=args.currency, dry_run=args.dry_run)
    except Exception:
        logger.exception("❌ Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
