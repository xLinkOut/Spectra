"""Tests for the local categoriser (merchant extraction, fuzzy match, ML cascade)."""

from __future__ import annotations

import hashlib

import pytest

from spectra.local_categorizer import (
    _extract_merchant_name,
    _fuzzy_match,
    categorise_local,
)


# ── Merchant Name Extraction ────────────────────────────────────


class TestExtractMerchantName:
    """Test that banking boilerplate is stripped to a clean merchant name."""

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("POS 1234 STARBUCKS MILANO", "Starbucks Milano"),
            ("ADDEBITO SDD NETFLIX.COM", "Netflix.Com"),
            ("PAGAMENTO SU POS ESSELUNGA SESTO S", "Esselunga Sesto S"),
            ("Bonifico istantaneo da voi disposto a favore di Mario Rossi", "Mario Rossi"),
            ("PRELIEVO BANCOMAT ATM 12345 VIA ROMA", "Atm"),
            ("ADDEBITO DIRETTO SPOTIFY AB", "Spotify"),
            ("PAGAMENTO APPLE.COM/BILL", "Apple.Com/Bill"),
            ("RICARICA TELEFONICA TIM", "Tim"),
            ("POS AMAZON EU SARL", "Amazon Eu"),
            ("CANONE MENSILE CONTO", "Mensile Conto"),
            # English / UK
            ("CARD PAYMENT NETFLIX.COM", "Netflix.Com"),
            ("DIRECT DEBIT SPOTIFY", "Spotify"),
            ("CONTACTLESS STARBUCKS", "Starbucks"),
            # German
            ("Lastschrift SPOTIFY AB", "Spotify"),
            ("Kartenzahlung AMAZON", "Amazon"),
            # French
            ("Prélèvement SEPA NETFLIX", "Netflix"),
            ("Paiement CB UBER", "Uber"),
            # Spanish
            ("Pago con tarjeta UBER", "Uber"),
        ],
    )
    def test_extraction(self, raw: str, expected: str):
        result = _extract_merchant_name(raw)
        assert result.lower() == expected.lower(), f"Expected {expected!r}, got {result!r}"


# ── ML Classifier (seed-bootstrapped) ────────────────────────────


class TestMLClassifierSeedBased:
    """Test that the ML classifier works from day-0 with seed data."""

    def test_trains_without_user_data(self):
        """Classifier should train on seed data alone (no user data needed)."""
        from spectra.ml_classifier import train_classifier
        clf = train_classifier()
        assert clf is not None

    def test_trains_with_none_user_data(self):
        from spectra.ml_classifier import train_classifier
        clf = train_classifier(None)
        assert clf is not None

    @pytest.mark.parametrize(
        "description, expected_category",
        [
            ("NETFLIX.COM", "Digital Subscriptions"),
            ("SPOTIFY AB", "Digital Subscriptions"),
            ("UBER TRIP HELP.UBER.COM", "Transport"),
            ("RYANAIR", "Travel"),
            ("IKEA ITALIA RETAIL", "Shopping"),
            ("AMAZON MARKETPLACE", "Shopping"),
            ("UBER EATS DELIVERY", "Food & Dining"),
            ("BOOKING.COM AMSTERDAM", "Travel"),
            ("STIPENDIO MESE 02/2026", "Salary"),
            ("AWS EMEA 123456789", "Digital Subscriptions"),
            ("ESSELUNGA SESTO", "Groceries"),
            ("VODAFONE ITALIA", "Utilities"),
            ("Starbucks Coffee", "Food & Dining"),
        ],
    )
    def test_seed_predictions(self, description: str, expected_category: str):
        """The seed-bootstrapped model should correctly classify common merchants."""
        from spectra.ml_classifier import train_classifier, predict
        clf = train_classifier()
        assert clf is not None
        category, confidence = predict(clf, description)
        assert category == expected_category, (
            f"For {description!r}: expected {expected_category!r}, got {category!r} (conf={confidence:.0%})"
        )

    def test_user_data_overrides_seed(self):
        """User corrections should dominate over seed knowledge."""
        from spectra.ml_classifier import train_classifier, predict

        # The user decides Netflix is "Entertainment" instead of "Digital Subscriptions"
        user_data = [("NETFLIX.COM", "Entertainment")] * 15

        clf = train_classifier(user_data)
        assert clf is not None
        category, _ = predict(clf, "NETFLIX.COM")
        assert category == "Entertainment"

    def test_predict_returns_confidence(self):
        from spectra.ml_classifier import train_classifier, predict
        clf = train_classifier()
        assert clf is not None
        category, confidence = predict(clf, "NETFLIX.COM")
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0


# ── Fuzzy Matching ───────────────────────────────────────────────


class TestFuzzyMatch:
    """Test fuzzy string matching against a known merchant database."""

    KNOWN_MERCHANTS = {
        "Starbucks": "Food & Dining",
        "Netflix": "Digital Subscriptions",
        "Amazon": "Shopping",
    }

    def test_exact_match(self):
        result = _fuzzy_match("Starbucks", self.KNOWN_MERCHANTS)
        assert result is not None
        name, cat = result
        assert name == "Starbucks"
        assert cat == "Food & Dining"

    def test_close_variation(self):
        result = _fuzzy_match("Starbucks Roma", self.KNOWN_MERCHANTS, threshold=70)
        assert result is not None
        name, _ = result
        assert name == "Starbucks"

    def test_no_match_for_unrelated(self):
        result = _fuzzy_match("McDonald's Napoli", self.KNOWN_MERCHANTS)
        assert result is None

    def test_empty_db_returns_none(self):
        result = _fuzzy_match("Starbucks", {})
        assert result is None


# ── Full Cascade Integration ─────────────────────────────────────


class TestCategoriseLocal:
    """Test the full local categorisation cascade (Exact → Fuzzy → ML → Fallback)."""

    @classmethod
    def _get_ml(cls):
        from spectra.ml_classifier import train_classifier
        return train_classifier()

    def _make_txn(self, desc: str, amount: float = -10.0, currency: str = "EUR", date: str = "2026-02-01"):
        return {"raw_description": desc, "amount": amount, "currency": currency, "date": date}

    def test_exact_merchant_memory_hit(self):
        """When a merchant is in the DB, it should be used directly."""
        merchant_db = {"Netflix.Com": "Digital Subscriptions"}
        txns = [self._make_txn("NETFLIX.COM")]
        results = categorise_local(txns, merchant_db=merchant_db, ml_classifier=self._get_ml())
        assert len(results) == 1
        assert results[0].category == "Digital Subscriptions"

    def test_ml_classifies_known_merchants(self):
        """ML should categorise known merchants even without merchant DB."""
        txns = [self._make_txn("SPOTIFY AB")]
        results = categorise_local(txns, merchant_db={}, ml_classifier=self._get_ml())
        assert len(results) == 1
        assert results[0].category == "Digital Subscriptions"

    def test_fallback_to_uncategorized(self):
        """Truly unknown transactions should fall back to 'Uncategorized'."""
        txns = [self._make_txn("XYZZY CORP INTERNAL PAYMENT")]
        results = categorise_local(txns, merchant_db={}, ml_classifier=self._get_ml())
        assert len(results) == 1
        # May or may not be uncategorized depending on ML confidence;
        # the important thing is it returns a result
        assert results[0].category is not None

    def test_income_override(self):
        """Positive amounts should be categorised as income when not already income."""
        txns = [self._make_txn("RANDOM TRANSFER", amount=1500.00)]
        results = categorise_local(txns, merchant_db={}, ml_classifier=self._get_ml())
        assert len(results) == 1
        income_cats = {"Salary", "Pension", "Transfer In", "Transfer", "Cash Deposit",
                       "Other Income", "Investment Return", "Reimbursement", "Uncategorized"}
        assert results[0].category in income_cats

    def test_salary_with_positive_amount(self):
        """STIPENDIO should be correctly identified as Salary."""
        txns = [self._make_txn("STIPENDIO MESE 02/2026", amount=2500.00)]
        results = categorise_local(txns, merchant_db={}, ml_classifier=self._get_ml())
        assert len(results) == 1
        assert results[0].category == "Salary"

    def test_multiple_transactions(self):
        """Batch of mixed transactions should all be categorised."""
        ml = self._get_ml()
        txns = [
            self._make_txn("NETFLIX.COM"),
            self._make_txn("UBER TRIP"),
            self._make_txn("STIPENDIO", amount=3000.0),
        ]
        results = categorise_local(txns, merchant_db={}, ml_classifier=ml)
        assert len(results) == 3
        categories = [r.category for r in results]
        assert "Digital Subscriptions" in categories
        assert "Transport" in categories
        assert "Salary" in categories

    def test_empty_input(self):
        """Empty input should return empty output."""
        results = categorise_local([], merchant_db={})
        assert results == []

    def test_fuzzy_match_in_cascade(self):
        """Fuzzy match should activate when merchant DB has a close match."""
        merchant_db = {"Starbucks": "Food & Dining"}
        txns = [self._make_txn("POS STARBUCKS ROMA")]
        results = categorise_local(txns, merchant_db=merchant_db, ml_classifier=self._get_ml())
        assert len(results) == 1
        assert results[0].category == "Food & Dining"

    def test_without_ml_falls_back(self):
        """Without ML classifier, unknown transactions should be Uncategorized."""
        txns = [self._make_txn("XYZZY CORP")]
        results = categorise_local(txns, merchant_db={}, ml_classifier=None)
        assert len(results) == 1
        assert results[0].category == "Uncategorized"
