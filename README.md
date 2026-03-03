<p align="center">
  <img src="assets/icon.png" alt="Spectra" width="180" />
</p>

<h1 align="center">Spectra</h1>
<p align="center">
  <strong>Bank CSV/PDF → AI categorization → Dashboard & Google Sheets</strong><br>
  Your personal finance dashboard, fully automated.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python" />
  <img src="https://img.shields.io/badge/license-AGPL--3.0-lightgrey" alt="License" />
  <img src="https://img.shields.io/badge/status-active-success" alt="Status" />
  <img src="https://img.shields.io/badge/AI-OpenAI%20%7C%20Gemini%20%7C%20Local-blueviolet" alt="AI Providers" />
</p>

<p align="center">
  <img src="assets/dashboard.png" alt="Spectra Dashboard" width="1000" />
</p>

---

## What is Spectra?

Spectra takes your raw bank exports (CSV or PDF), categorizes every transaction — via AI or fully offline — and visualizes your finances in a **self-hosted web dashboard** and optionally syncs to **Google Sheets**.

### Why Spectra exists

Most personal finance tools require direct access to your bank account or lock your data inside proprietary platforms. Spectra works directly from standard bank exports, keeps everything local, and gives you full control.

---

## ✨ Features

### 🌐 Self-Hosted Web Dashboard
A Notion-style local dashboard at `localhost:8080` with:
- **Summary cards** — Total Spent, Income, Subscriptions, Uncategorized count
- **Spending charts** — Category doughnut + monthly trend bar chart (Chart.js)
- **Transactions table** — Filterable, searchable, with inline click-to-edit
- **Drag & drop upload** — Upload CSV/PDF, preview AI categories, confirm & save
- **Settings** — Live config, DB stats, CSV export
- **Mobile responsive** — Works on phone/tablet with collapsible sidebar

### 🤖 Three AI Modes

Spectra supports three categorization modes, switchable via `AI_PROVIDER` in your `.env`:

- **`openai`** — Categorization via OpenAI API. Requires `OPENAI_API_KEY`.
- **`gemini`** — Categorization via Google Gemini API. Requires `GEMINI_API_KEY`. Free tier available.
- **`local`** — 100% offline, no API keys needed. Uses a 6-step deterministic cascade:

  1. **User Overrides** — Previously corrected categories
  2. **Merchant Memory** — Exact match against merchants seen before (SQLite)
  3. **Fuzzy Match** — Approximate matching (e.g., "STARBUCKS ROMA" → "Starbucks") via `rapidfuzz`
  4. **Keyword Rules** — 120+ built-in patterns covering subscriptions, transport, food, travel, entertainment, shopping, health, taxes, education, cash deposits, and more
  5. **ML Classifier** (optional) — Trained on *your* history. Install `scikit-learn` to enable
  6. **Fallback** — "Uncategorized" for manual correction (Spectra remembers next time)

> **Stress-tested**: 35/35 tricky Italian bank transactions categorized correctly on first pass with zero API calls.

### 📊 Google Sheets Dashboard
Spectra automatically creates and formats multiple tabs:
- **Dashboard** — Income vs Expenses, spending donuts, monthly breakdowns, recurring cash flow, and budget status
- **Budget** — Define monthly limits. Spectra shows 🟢/🟡/🔴 Budget Status on the Dashboard
- **Transactions YYYY** — Color-coded ledger for each year
- **Trends** — Year-over-Year comparison with Net Cash Flow, Savings Rate %, and multi-year charts

### 🔧 Other Features
- **Universal Import** — Auto-detects delimiters, bank layouts, Italian/European number formats, multi-line descriptions
- **Multi-Currency (FX)** — Automatic ECB historical rates via [Frankfurter API](https://www.frankfurter.app/) (no API key needed)
- **Hybrid Recurring Detection** — Pattern-matching + historical date analysis flags subscriptions/salaries automatically
- **Smart Overrides** — Correct AI mistakes in Sheets; Spectra learns and applies them locally next time
- **Idempotent** — SHA1 transaction hashes in SQLite prevent duplicate imports
- **GitHub Actions** — Nightly cron automation included

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/francescogabrieli/Spectra.git
cd Spectra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
# Required
BASE_CURRENCY=EUR

# AI Provider (choose one)
AI_PROVIDER=local          # Free, offline — no keys needed
# AI_PROVIDER=openai       # Needs OPENAI_API_KEY
# AI_PROVIDER=gemini       # Needs GEMINI_API_KEY

# Optional: Google Sheets sync
# SPREADSHEET_ID=1Do7APx...
# GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
```

### 3. Launch

```bash
python -m spectra --serve
```

Open **http://localhost:8080** — upload CSVs, review categories, and manage everything from the browser.

<details>
<summary><strong>CLI alternatives (advanced)</strong></summary>

```bash
# Process a folder of bank exports
python -m spectra --inbox inbox/

# Preview categorization without saving
python -m spectra --inbox inbox/ --dry-run

# Single file
python -m spectra -f export.csv

# Custom port for the dashboard
python -m spectra --serve --port 3000
```

| Flag | Description |
|------|-------------|
| `--serve` | Launch the web dashboard |
| `--port N` | Set dashboard port (default: 8080) |
| `--inbox DIR` | Process all CSV/PDF files in a directory |
| `-f FILE` | Process a single file |
| `--dry-run` | Preview only, no writes |
| `--currency USD` | Override base currency |

</details>


---


## 🔑 Getting the Keys

<details>
<summary><strong>Google Sheets API</strong> (optional — for Sheets sync)</summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a Project → Enable **Google Sheets API** and **Google Drive API**
3. **Credentials → Service Account** → Create → Download JSON key
4. Rename to `credentials.json` and place in project root
5. Create a Google Sheet → **Share** with the service account email (Editor)
6. Copy the **Spreadsheet ID** from the URL into `.env`

</details>

<details>
<summary><strong>OpenAI API Key</strong></summary>

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a key → set `OPENAI_API_KEY` in `.env`
3. Set `AI_PROVIDER=openai`

</details>

<details>
<summary><strong>Gemini API Key</strong> (free tier available)</summary>

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a key → set `GEMINI_API_KEY` in `.env`
3. Set `AI_PROVIDER=gemini`

</details>

---

## 🤖 GitHub Actions

Spectra includes `.github/workflows/spectra.yml` for nightly automation at 22:00 CET.

<details>
<summary><strong>Setup GitHub Secrets</strong></summary>

Add to **Settings → Secrets → Actions**:

| Secret | Value |
|--------|-------|
| `OPENAI_API_KEY` or `GEMINI_API_KEY` | Your AI key |
| `SPREADSHEET_ID` | Google Sheet ID |
| `GOOGLE_SHEETS_CREDENTIALS_B64` | `base64 -i credentials.json \| pbcopy` |

</details>

---

## 🔒 Privacy & Security

- **Local-first**: Parsing, cleaning, deduplication, and (optionally) categorization all run locally
- **Minimal AI payload**: Only date + cleaned description + amount are sent to the AI provider
- **No bank connections**: Spectra never connects to your bank — you export and upload manually
- **SQLite storage**: Transaction hashes + merchant categories stored locally in `data/prism.db`
- **Self-hosted dashboard**: Runs on `127.0.0.1` — your data never leaves your machine

---

## 📄 License

**GNU Affero General Public License v3.0 (AGPL-3.0)**

If you modify Spectra and run it as a network service, you must make your source code available.

### Commercial License

A separate commercial license is available for closed-source or proprietary use.

Contact: francesco.gabrieli.fg@gmail.com
