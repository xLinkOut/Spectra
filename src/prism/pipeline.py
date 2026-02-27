"""Pipeline orchestrator — CSV/PDF → AI → Google Sheets."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from prism.ai import CategorisedTransaction, categorise
from prism.config import Settings, load_settings
from prism.csv_parser import ParsedTransaction, parse_csv
from prism.dashboard import refresh_dashboard
from prism.db import BookmarkDB
from prism.sheets import SheetsClient

logger = logging.getLogger("prism")


def _parse_file(file_path: str, currency: str) -> list[ParsedTransaction]:
    """Auto-detect CSV or PDF and parse accordingly."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        from prism.pdf_parser import parse_pdf
        return parse_pdf(file_path, currency=currency)
    else:
        return parse_csv(file_path, currency=currency)

def run(settings: Settings, file: str, currency: str, dry_run: bool) -> None:
    """Process a bank CSV or PDF export → AI → Google Sheets."""

    ext = Path(file).suffix.upper()
    logger.info("📂 Reading %s: %s", ext, file)
    parsed = _parse_file(file, currency=currency)

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

        # ── Step 3: Read existing categories and Overrides ───────
        if dry_run:
            existing_categories: list[str] = []
            overrides = db.get_overrides()
        else:
            sheets = SheetsClient(
                spreadsheet_id=settings.spreadsheet_id,
                credentials_b64=settings.google_sheets_credentials_b64,
                credentials_file=settings.google_sheets_credentials_file,
            )
            existing_categories = sheets.get_existing_categories()
            logger.info("Syncing manual overrides from Sheets...")
            overrides = sheets.fetch_overrides()
            db.save_overrides(overrides)

        logger.info("📂 Existing categories: %s", existing_categories or "(none)")

        # ── Step 3b: Local Override Matching (skip LLM if mapped) ────
        to_llm = []
        pre_categorised: list[CategorisedTransaction] = []
        
        for t in new_txns:
            # ParsedTransaction (from csv/pdf) uses raw_description
            od = t.raw_description
            if od in overrides:
                # We have a manual classification for this exact description
                pre_categorised.append(
                    CategorisedTransaction(
                        id=t.id,
                        original_description=od,
                        clean_name=overrides[od]["clean_name"],
                        category=overrides[od]["category"],
                        amount=t.amount,
                        currency=t.currency,
                        date=t.date,
                    )
                )
            else:
                to_llm.append(t)
                
        if pre_categorised:
            logger.info("Applied overrides to %d transaction(s) locally", len(pre_categorised))

        # ── Step 4: AI Matching (only for unknown txns) ─────────────
        categorised = []
        if to_llm:
            flat = [
                {"raw_description": t.raw_description, "amount": t.amount, "currency": t.currency, "date": t.date}
                for t in to_llm
            ]

            if settings.ai_provider == "gemini":
                api_key, model = settings.gemini_api_key, settings.gemini_model
            else:
                api_key, model = settings.openai_api_key, settings.openai_model

            llm_results = categorise(
                flat, existing_categories,
                provider=settings.ai_provider, api_key=api_key, model=model,
                base_currency=settings.base_currency,
            )
            
            if not llm_results:
                logger.warning("⚠️  LLM returned no results for %d transactions", len(to_llm))
            else:
                categorised.extend(llm_results)
                
        # Merge pre-categorised (overrides) and LLM-categorised
        categorised.extend(pre_categorised)

        if not categorised:
            logger.warning("No transactions were categorised.")
            return

        # ── Step 4b: Deterministic recurring detection ────────────
        from prism.recurring import apply_recurring_tags
        
        # We fetch history from the DB to do temporal matching
        history = db.get_merchant_history()
        apply_recurring_tags(categorised, history)

        # ── Step 4c: Currency conversion ─────────────────────────
        from prism.fx import convert_currency
        for t in categorised:
            if t.currency.upper() != settings.base_currency:
                original_amt = t.amount
                original_cur = t.currency.upper()
                converted = convert_currency(original_amt, original_cur, settings.base_currency, t.date)
                
                t.original_amount = original_amt
                t.original_currency = original_cur
                t.amount = converted
                t.currency = settings.base_currency

        # ── Step 5: Write or print ───────────────────────────────
        if dry_run:
            from prism.reporter import generate_html_report
            logger.info("🧪 DRY RUN — writing to HTML report")
            generate_html_report(categorised)
            logger.info("✅ Report generated and opened in browser")
        else:
            sheets.append_transactions(categorised)
            # Save history (date, amount, clean_name) for future temporal recurring detection
            db.save_history(categorised)
            logger.info("✅ Done — %d rows written to Google Sheets", len(categorised))

            # Refresh the Dashboard tab with updated charts
            try:
                refresh_dashboard(sheets)
            except Exception:
                logger.warning("Dashboard update failed — continuing", exc_info=True)


def run_inbox(settings: Settings, inbox_dir: str, currency: str, dry_run: bool) -> None:
    """Process ALL csv/pdf files in a folder, then move them to processed/."""
    import shutil

    inbox = Path(inbox_dir)
    if not inbox.exists():
        logger.info("📂 Inbox folder %s does not exist — nothing to do", inbox)
        return

    files = sorted(
        list(inbox.glob("*.csv")) + list(inbox.glob("*.pdf"))
    )
    if not files:
        logger.info("📂 No CSV/PDF files in %s — nothing to do", inbox)
        return

    # Create processed/ as sibling of inbox/
    processed = inbox.parent / "processed"
    processed.mkdir(exist_ok=True)

    logger.info("📂 Found %d file(s) in %s", len(files), inbox)

    for bank_file in files:
        logger.info("─" * 40)
        logger.info("Processing: %s", bank_file.name)
        try:
            run(settings, file=str(bank_file), currency=currency, dry_run=dry_run)

            if not dry_run:
                dest = processed / bank_file.name
                if dest.exists():
                    from datetime import datetime, timezone
                    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                    dest = processed / f"{bank_file.stem}_{ts}{bank_file.suffix}"
                shutil.move(str(bank_file), str(dest))
                logger.info("📦 Moved to %s", dest)
        except Exception:
            logger.exception("❌ Failed to process %s", bank_file.name)

    logger.info("✅ Inbox processing complete")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="prism",
        description="Prism — Bank CSV → AI → Google Sheets",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Path to a bank CSV or PDF export")
    group.add_argument("--inbox", help="Path to folder with CSV/PDF files (processes all)")

    parser.add_argument("--currency", default=None, help="Currency code (default: from .env BASE_CURRENCY)")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing to Sheets")

    args = parser.parse_args()
    settings = load_settings()

    target_currency = args.currency or settings.base_currency

    try:
        if args.inbox:
            run_inbox(settings, inbox_dir=args.inbox, currency=target_currency, dry_run=args.dry_run)
        else:
            run(settings, file=args.file, currency=target_currency, dry_run=args.dry_run)
    except Exception:
        logger.exception("❌ Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
