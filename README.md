# Budget Calculator: Exchange Edition [2026]

> Originally built in 2024, remastered in 2026 as a full Streamlit web app.

A multilingual personal finance tool for tracking spending across countries and currencies. Built during the Winter 2024 exchange at IE University, remastered in 2026 with a complete UI overhaul.

**Live app:** [budget-calculator-tracker.streamlit.app](https://budget-calculator-tracker.streamlit.app)

## Features

### Multi-language support

Switch between English, French, and Spanish at any time. All labels, charts, and messages update instantly.

### File import & export

- Upload your own `.json` (app export), `.csv`, or `.xlsx` file to restore a previous session
- Download your data as `budget.json` or export to CSV at any time
- Compatible with the legacy `statswinter24.csv` format (mixed currencies, country-tagged entries)

### Budget setup

After loading a file or starting fresh, set your total budget, currency, and exchange duration before viewing any charts. Your expenses are never wiped when you update the budget.

### Multi-currency tracking

Supports EUR, CAD, HUF, SEK, TRY with approximate 2024 annual average exchange rates. Each expense is recorded in its original currency and converted to your chosen display currency on the fly.

### Charts & visualizations

| Chart | What it shows |
| --- | --- |
| Spending by Category (pie) | Category breakdown with semantic colours, each category has a fixed, consistent colour |
| Spending by Country (bar) | Total per country, horizontal, green-to-red gradient by spend size |
| Geographic Spending Map | World map with visited countries highlighted in green-to-red gradient |
| Monthly Spending vs Budget | Bar chart per month with a dashed monthly budget line, red bars exceed the budget |
| Cumulative Spending | Running total line chart with budget and 70% warning thresholds |
| Country Deep Dive | Select any country to see its category breakdown and monthly timeline |

### Expense log

Colour-coded rows (green / amber / red) based on each expense as a share of the total budget. Includes a delete button per row.

### Currency log

Summary table of all currencies detected in the loaded data: transaction count, original total, and converted total.

## Project Structure

```
Budget-Calculator-Exchange/
├── src/
│   ├── main.py                 # Entry point (routing only)
│   ├── config.py               # Currencies, translations, category colours
│   ├── utils.py                # Currency conversion, formatting, image helpers
│   ├── file_parser.py          # CSV / JSON / Excel import
│   ├── session.py              # Session state init, load, export
│   ├── assets/                 # Banner images (hero + dashboard, per language)
│   └── components/
│       ├── landing.py          # Upload page
│       ├── setup.py            # Budget setup card
│       ├── sidebar.py          # Sidebar panel
│       └── dashboard.py        # Charts, metrics, expense log
├── data/
│   └── statswinter24.csv       # Sample data: Winter 2024 exchange
├── archive/                    # Original 2024 scripts (not part of the app)
├── .streamlit/
│   └── config.toml             # Dark theme + teal primary colour
├── requirements.txt
└── README.md
```

## Running locally

```bash
# 1. Clone the repo
git clone https://github.com/stefhooy/Budget-Calculator-Exchange.git
cd Budget-Calculator-Exchange

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python -m streamlit run src/main.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

Requirements: Python 3.10+

```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.0.0
```

## Deploying to Streamlit Cloud

1. Push the repo to GitHub, make sure `src/assets/` images are committed (do not gitignore them)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **Create app** and fill in:
   - Repository: `stefhooy/Budget-Calculator-Exchange`
   - Branch: `main`
   - Main file path: `src/main.py`
4. Click **Deploy**

No secrets or environment variables required.

## Try it out

Load `data/statswinter24.csv` from this repo to see the app in action. It contains real spending data across 5 months and 8 countries (Hungary, Croatia, France, Turkey, Malta, Austria, Bulgaria, Portugal, Sweden, Spain, Slovakia) with multiple currencies (HUF, EUR, CAD, SEK, TRY).

## Background

- **Original project:** Winter 2024, Python script + Jupyter notebook
- **Remastered:** 2026, full Streamlit web app with multilingual UI, interactive charts, geographic map, and file-based persistence

## Photography

All banner images were taken by me under the alias **HöY**, shot across Malta, Paris, Madrid, and Navacerrada.
