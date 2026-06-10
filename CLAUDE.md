# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```powershell
.venv\Scripts\streamlit.exe run main.py
```

Always use `.venv\Scripts\python.exe` for any direct Python invocations.

## Architecture

Single-file Streamlit app (`main.py`) with two core functions and an inline UI section:

**`extrair_dados_siclom(pdf_file)`** — parses a SICLOM-format PDF (Brazilian HIV medication dispensing system). Each page is split into blocks on the `Data:` field. From each block it extracts: withdrawal date (`Data:`), treatment days (`Dias Trat.:`), and weight (`Peso:`). Returns a list of records sorted by date.

**`analisar_gaps(registros)`** — simulates a running medication stock counter across all withdrawals in chronological order. For each withdrawal it computes whether the stock from the previous withdrawal lasted until this one. A gap is recorded when `stock_end < next_withdrawal_date` and the gap exceeds 10 days. After the loop, it also checks if stock ran out before today (to catch patients who stopped coming entirely). Returns a DataFrame with columns: `Inicio`, `Fim`, `Dias`, `Retirada`, `Qtd`, `Reserva`.

**Column semantics:**
- `Inicio` / `Fim` / `Dias` — when the gap started, ended, and how many days it lasted
- `Retirada` — date of the last withdrawal *before* the gap (not the one that ended it)
- `Qtd` — days of medication received at that withdrawal
- `Reserva` — days of stock remaining *when that withdrawal was made* (from a prior visit); combined with `Qtd` gives total stock that led to the gap

The UI displays results in reverse chronological order (most recent gap first).

## Language

All user-facing text — UI labels, messages, error strings, and column names — must be written in **Portuguese (Brazil)**.

## Deploying to Streamlit Community Cloud

1. Make sure `requirements.txt` is up to date
2. Push all changes to GitHub (`github.com/gianrocon/tarv`, branch `main`)
3. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
4. Click **New app** → select repo `gianrocon/tarv`, branch `main`, main file `main.py`
5. Click **Deploy**

## PDF format assumption

The parser assumes SICLOM PDFs where each dispensing record contains the literal strings `Data:`, `Dias Trat.:`, and optionally `Peso:`. If the PDF layout changes, update the regex patterns in `extrair_dados_siclom`.
