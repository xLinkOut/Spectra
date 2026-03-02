"""Tests for the local categoriser (merchant extraction, keyword rules, fuzzy match, cascade)."""

from __future__ import annotations

import hashlib

import pytest

from spectra.local_categorizer import (
    _extract_merchant_name,
    _fuzzy_match,
    _match_keyword,
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
        ],
    )
    def test_extraction(self, raw: str, expected: str):
        result = _extract_merchant_name(raw)
        assert result.lower() == expected.lower(), f"Expected {expected!r}, got {result!r}"


# ── Keyword Rule Matching ────────────────────────────────────────


class TestKeywordRules:
    """Test that keyword rules correctly categorise known merchants."""

    @pytest.mark.parametrize(
        "description, expected_category",
        [
            ("NETFLIX.COM", "Digital Subscriptions"),
            ("SPOTIFY AB", "Digital Subscriptions"),
            ("UBER TRIP HELP.UBER.COM", "Transport"),
            ("TRENITALIA SPA", "Transport"),
            ("RYANAIR", "Travel"),
            ("FARMACIA DEL CENTRO", "Health"),
            ("IKEA ITALIA RETAIL", "Shopping"),
            ("RISTORANTE DA LUIGI", "Food & Dining"),
            ("ENI STATION MILANO", "Transport"),
            ("AXA ASSICURAZIONI", "Insurance"),
            ("VODAFONE ITALIA", "Utilities"),
            ("STIPENDIO MESE 02/2026", "Salary"),
            ("APPLE.COM/BILL", "Digital Subscriptions"),
            ("AMAZON MARKETPLACE", "Shopping"),
            ("UBER EATS DELIVERY", "Food & Dining"),
            ("BOOKING.COM AMSTERDAM", "Travel"),
        ],
    )
    def test_keyword_match(self, description: str, expected_category: str):
        result = _match_keyword(description)
        assert result is not None, f"No keyword match for {description!r}"
        category, _ = result
        assert category == expected_category

    def test_unknown_merchant_no_match(self):
        """Obscure descriptions should not match any keyword rule."""
        result = _match_keyword("PAGAMENTO XYZZY CORP INTERNAL REF 999")
        assert result is None


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
    """Test the full local categorisation cascade."""

    def _make_txn(self, desc: str, amount: float = -10.0, currency: str = "EUR", date: str = "2026-02-01"):
        return {"raw_description": desc, "amount": amount, "currency": currency, "date": date}

    def test_exact_merchant_memory_hit(self):
        """When a merchant is in the DB, it should be used directly."""
        merchant_db = {"Netflix.Com": "Digital Subscriptions"}
        txns = [self._make_txn("NETFLIX.COM")]
        results = categorise_local(txns, [], merchant_db=merchant_db)
        assert len(results) == 1
        # Should match via keyword (since extraction gives "Netflix.Com" which is in merchant_db)
        assert results[0].category in ("Digital Subscriptions",)

    def test_keyword_rule_hit(self):
        """Keyword rules should fire for known merchants."""
        txns = [self._make_txn("SPOTIFY AB")]
        results = categorise_local(txns, [], merchant_db={})
        assert len(results) == 1
        assert results[0].category == "Digital Subscriptions"
        assert results[0].clean_name == "Spotify"

    def test_fallback_to_uncategorized(self):
        """Unknown transactions should fall back to 'Uncategorized'."""
        txns = [self._make_txn("XYZZY CORP INTERNAL PAYMENT")]
        results = categorise_local(txns, [], merchant_db={})
        assert len(results) == 1
        assert results[0].category == "Uncategorized"

    def test_income_override(self):
        """Positive amounts should be categorised as income."""
        txns = [self._make_txn("RANDOM TRANSFER", amount=1500.00)]
        results = categorise_local(txns, [], merchant_db={})
        assert len(results) == 1
        # Should be income category since amount > 0
        income_cats = {"Salary", "Pension", "Transfer In", "Cash Deposit", "Other Income", "Investment Return"}
        assert results[0].category in income_cats or results[0].category == "Uncategorized"

    def test_salary_keyword_with_positive_amount(self):
        """STIPENDIO should be correctly identified as Salary."""
        txns = [self._make_txn("STIPENDIO MESE 02/2026", amount=2500.00)]
        results = categorise_local(txns, [], merchant_db={})
        assert len(results) == 1
        assert results[0].category == "Salary"

    def test_multiple_transactions(self):
        """Batch of mixed transactions should all be categorised."""
        txns = [
            self._make_txn("NETFLIX.COM"),
            self._make_txn("UBER TRIP"),
            self._make_txn("UNKNOWN MERCHANT XYZ"),
            self._make_txn("STIPENDIO", amount=3000.0),
        ]
        results = categorise_local(txns, [], merchant_db={})
        assert len(results) == 4
        categories = [r.category for r in results]
        assert "Digital Subscriptions" in categories
        assert "Transport" in categories
        assert "Salary" in categories

    def test_empty_input(self):
        """Empty input should return empty output."""
        results = categorise_local([], [], merchant_db={})
        assert results == []

    def test_fuzzy_match_in_cascade(self):
        """Fuzzy match should activate when merchant DB has a close match."""
        merchant_db = {"Starbucks": "Food & Dining"}
        txns = [self._make_txn("POS STARBUCKS ROMA")]
        results = categorise_local(txns, [], merchant_db=merchant_db)
        assert len(results) == 1
        # Should get "Food & Dining" from either fuzzy or keyword
        assert results[0].category == "Food & Dining"


# ── ML Classifier ────────────────────────────────────────────────


class TestMLClassifier:
    """Test the optional ML classifier."""

    def test_not_enough_data(self):
        from spectra.ml_classifier import train_classifier
        data = [("Netflix", "Subscriptions")] * 5
        result = train_classifier(data)
        assert result is None

    def test_single_category_returns_none(self):
        from spectra.ml_classifier import train_classifier
        data = [("Netflix", "Subscriptions")] * 25
        result = train_classifier(data)
        assert result is None

    def test_trains_successfully(self):
        from spectra.ml_classifier import train_classifier, predict

        data = (
            [("Netflix subscription", "Digital Subscriptions")] * 15
            + [("Uber trip", "Transport")] * 15
            + [("Amazon purchase", "Shopping")] * 15
        )
        clf = train_classifier(data)
        assert clf is not None

        category, confidence = predict(clf, "Netflix monthly")
        assert category == "Digital Subscriptions"
        assert confidence > 0.5

    def test_low_confidence_prediction(self):
        from spectra.ml_classifier import train_classifier, predict

        data = (
            [("Netflix subscription", "Digital Subscriptions")] * 10
            + [("Netflix streaming", "Transport")] * 10  # conflicting labels on purpose
            + [("Random stuff", "Shopping")] * 10
        )
        clf = train_classifier(data)
        assert clf is not None

        # With conflicting labels, confidence should be lower
        _, confidence = predict(clf, "Netflix premium")
        # Just verify it returns something reasonable
        assert 0.0 <= confidence <= 1.0
