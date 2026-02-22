# 🔷 Prism

**Bank CSV → AI → Google Sheets** — il tuo estratto conto categorizzato automaticamente.

Esporta il CSV dalla tua banca, lancia un comando, e Prism categorizza ogni transazione con l'AI e la scrive su Google Sheets. Funziona con **qualsiasi banca** (Intesa, ISyBank, UniCredit, N26, Revolut, etc.).

```
📄 movimenti.csv  →  🤖 Gemini/OpenAI  →  📊 Google Sheets
```

---

## Caratteristiche

- **Universale** — legge CSV da qualsiasi banca (auto-detect colonne e formato)
- **AI-powered** — categorizza le transazioni con Gemini o OpenAI
- **Google Sheets** — scrive direttamente nel tuo foglio
- **Idempotente** — non importa mai la stessa transazione due volte
- **Privacy-first** — i tuoi dati restano tuoi, nessun intermediario
- **Zero dipendenze esterne** — nessun account bancario API richiesto

---

## Quick Start

### 1. Setup

```bash
git clone https://github.com/YOUR_USERNAME/Prism.git
cd Prism

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# → Compila GEMINI_API_KEY e SPREADSHEET_ID
```

### 2. Prendi una Gemini API Key (gratis)

1. Vai su [aistudio.google.com](https://aistudio.google.com/)
2. Clicca **Get API Key**
3. Incolla nel file `.env` → `GEMINI_API_KEY=...`

### 3. Configura Google Sheets

1. Crea un progetto su [Google Cloud Console](https://console.cloud.google.com/)
2. Abilita le API **Google Sheets** e **Google Drive**
3. Crea un **Service Account** e scarica il JSON
4. Rinomina il file in `credentials.json` e mettilo nella root del progetto
5. Crea un foglio Google Sheets e **condividilo** con l'email del service account
6. Copia l'ID del foglio dall'URL e mettilo in `.env` → `SPREADSHEET_ID=...`

### 4. Usa

```bash
# Esporta il CSV dalla tua banca e poi:
python -m prism --file ~/Downloads/movimenti.csv

# Dry-run (solo anteprima, non scrive nulla):
python -m prism --file ~/Downloads/movimenti.csv --dry-run
```

---

## Formato CSV supportati

Prism auto-detecta il formato. Funziona con:

| Banca | Formato | Testato |
|-------|---------|---------|
| ISyBank / Intesa | `;` separatore, importi italiani | ✅ |
| UniCredit | `;` separatore | ✅ |
| N26 | `,` separatore, ISO dates | ✅ |
| Revolut | `,` separatore, English | ✅ |
| Qualsiasi altra | Auto-detect | ✅ |

Colonne riconosciute automaticamente: `Data`, `Descrizione`, `Importo`, `Date`, `Description`, `Amount`, `Addebito`, `Accredito`, `Credit`, `Debit`, e molte altre varianti.

---

## Struttura

```
Prism/
├── src/prism/
│   ├── __init__.py
│   ├── __main__.py        # entry point
│   ├── config.py           # env vars (Pydantic)
│   ├── csv_parser.py       # universal CSV parser
│   ├── ai.py               # LLM categoriser (Gemini/OpenAI)
│   ├── sheets.py           # Google Sheets writer
│   ├── pipeline.py         # orchestrator
│   └── db.py               # SQLite dedup tracker
├── tests/
├── .env.example
├── .github/workflows/
└── pyproject.toml
```

---

## Variabili d'ambiente

| Variabile | Obbligatoria | Default | Descrizione |
|-----------|-------------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | Chiave API Gemini |
| `SPREADSHEET_ID` | ✅ | — | ID del Google Sheet |
| `GOOGLE_SHEETS_CREDENTIALS_B64` | ✅* | — | Credenziali service account (base64) |
| `GOOGLE_SHEETS_CREDENTIALS_FILE` | ✅* | `credentials.json` | Path al file JSON |
| `AI_PROVIDER` | ❌ | `gemini` | `gemini` o `openai` |
| `GEMINI_MODEL` | ❌ | `gemma-3-27b-it` | Modello Gemini |
| `OPENAI_API_KEY` | ❌ | — | Chiave API OpenAI |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | Modello OpenAI |
| `DB_PATH` | ❌ | `data/prism.db` | Path del database SQLite |
| `LOG_LEVEL` | ❌ | `INFO` | Livello di log |

*Una delle due è obbligatoria.

---

## Privacy & Sicurezza

- I dati bancari **non lasciano mai il tuo computer** (a parte la descrizione inviata all'AI)
- Nessun server terzo, nessun account bancario API
- Il database SQLite è locale e contiene solo gli hash delle transazioni già importate
- Le credenziali Google restano nel tuo `.env` (mai committate su Git)

---

## Fork & Personalizza

1. Forka il repo
2. Modifica `src/prism/ai.py` per cambiare le categorie o la lingua del prompt
3. Modifica `src/prism/sheets.py` per cambiare le colonne del foglio
4. Aggiungi il tuo CSV e lancia!

---

## License

MIT