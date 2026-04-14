import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import json
import re
import os
import base64

# ── Image helper ──────────────────────────────────────────────────────────────
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")

def _image_b64(filename: str) -> str | None:
    path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            ext = filename.rsplit(".", 1)[-1].lower()
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    return None

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Budget Calculator | Calculateur Budget",
    page_icon="💶",
    layout="wide",
)

st.markdown("""
<script>
    window.addEventListener('beforeunload', function(e) {
        e.preventDefault(); e.returnValue = '';
    });
</script>
""", unsafe_allow_html=True)

# ── Currency data (approximate 2024 annual averages vs EUR) ───────────────────
CURRENCIES = {
    "EUR": {"name": "Euro",             "symbol": "€",   "rate_to_eur": 1.0},
    "USD": {"name": "US Dollar",        "symbol": "$",   "rate_to_eur": 1.08},
    "CAD": {"name": "Canadian Dollar",  "symbol": "CA$", "rate_to_eur": 1.47},
    "HUF": {"name": "Hungarian Forint", "symbol": "Ft",  "rate_to_eur": 394.0},
    "SEK": {"name": "Swedish Krona",    "symbol": "kr",  "rate_to_eur": 11.47},
    "TRY": {"name": "Turkish Lira",     "symbol": "₺",   "rate_to_eur": 35.26},
}
CURRENCY_CODES = list(CURRENCIES.keys())

# ── Category colours (semantic: same colour per category everywhere) ──────────
CATEGORY_COLORS = {
    "Restaurant":         "#e07b39",   # warm orange
    "Food":               "#f0a500",   # amber
    "Grocery":            "#27ae60",   # green
    "Transport":          "#3498db",   # blue
    "Hotel":              "#9b59b6",   # purple
    "Bar":                "#c0392b",   # dark red
    "Activity & Museums": "#1abc9c",   # teal
    "Activités & Musées": "#1abc9c",
    "Actividades & Museos": "#1abc9c",
    "Telephone":          "#7f8c8d",   # slate
    "Téléphone":          "#7f8c8d",
    "Teléfono":           "#7f8c8d",
    "Housing":            "#e74c3c",   # red
    "Logement":           "#e74c3c",
    "Alojamiento":        "#e74c3c",
    "Entertainment":      "#e91e8c",   # pink
    "Loisirs":            "#e91e8c",
    "Ocio":               "#e91e8c",
    "Health":             "#00bcd4",   # cyan
    "Santé":              "#00bcd4",
    "Salud":              "#00bcd4",
    "Shopping":           "#ff9800",   # deep orange
    "Compras":            "#ff9800",
    "Nourriture":         "#f0a500",
    "Comida":             "#f0a500",
}
_DEFAULT_CAT_COLORS = [
    "#3498db","#e07b39","#27ae60","#9b59b6","#1abc9c",
    "#e74c3c","#f39c12","#00bcd4","#e91e8c","#7f8c8d","#ff9800",
]

def cat_color(name: str, idx: int = 0) -> str:
    return CATEGORY_COLORS.get(name, _DEFAULT_CAT_COLORS[idx % len(_DEFAULT_CAT_COLORS)])

def convert_amount(amount: float, from_cur: str, to_cur: str) -> float:
    if from_cur == to_cur:
        return amount
    eur = amount / CURRENCIES.get(from_cur, CURRENCIES["EUR"])["rate_to_eur"]
    return eur * CURRENCIES.get(to_cur, CURRENCIES["EUR"])["rate_to_eur"]

def fmt(amount: float, currency: str = None) -> str:
    cur = currency or st.session_state.get("display_currency", "EUR")
    sym = CURRENCIES[cur]["symbol"]
    return f"{sym}{amount:,.2f}"

def to_display(amount: float, original_currency: str) -> float:
    dc = st.session_state.get("display_currency", "EUR")
    return convert_amount(amount, original_currency, dc)

def _detect_currency(raw: str) -> str:
    s = str(raw).strip()
    if "Ft" in s or "ft" in s:
        return "HUF"
    if "€" in s:
        return "EUR"
    if "₺" in s:
        return "TRY"
    if "kr" in s.lower():
        return "SEK"
    if "$" in s:
        return "CAD"
    return "EUR"

# ── Language strings ──────────────────────────────────────────────────────────
LANG = {
    "EN": {
        "title": "Budget Calculator: Exchange Edition",
        "subtitle": "Track your spending abroad, stay in control.",
        "hero_image": "hero_en.jpg",
        "hero_tagline": "Exchange Edition · Remastered 2026",
        "landing_title": "Welcome",
        "landing_subtitle": "Your data never leaves your device. Upload a file to continue where you left off, or start from scratch.",
        "upload_section": "Upload your file",
        "upload_label": "Accepted: .json (app export), .csv or .xlsx (see structure below)",
        "fresh_btn": "Start fresh",
        "upload_error": "Could not read that file. Check the format matches the structure shown below.",
        "preview_title": "Expected file structure",
        "preview_caption_simple": "Simple format (exported by this app)",
        "preview_caption_legacy": "Legacy format (statswinter24.csv style, also supported)",
        "setup_header": "Budget Setup",
        "total_budget": "Total Budget",
        "budget_currency": "Budget Currency",
        "display_currency": "Display Currency",
        "rates_note": "Rates: approx. 2024 annual averages",
        "duration": "Exchange Duration (months)",
        "init_btn": "Set Total Budget",
        "add_header": "Add Expense",
        "amount": "Amount",
        "exp_currency": "Expense Currency",
        "description": "Description",
        "category": "Category",
        "add_btn": "Add Expense",
        "clear_btn": "Clear All Expenses",
        "reset_btn": "Reset (New Session)",
        "download_header": "Save your data",
        "download_caption": "Download before closing the tab!",
        "save_btn": "Download budget.json",
        "export_csv": "Export to CSV",
        "overview_header": "Budget Overview",
        "initial": "Total Budget",
        "spent": "Total Spent",
        "remaining": "Remaining",
        "monthly": "Monthly Budget",
        "weekly": "Weekly Budget",
        "expenses_header": "Expense Log",
        "no_expenses": "No expenses recorded yet.",
        "charts_header": "Spending Breakdown",
        "pie_title": "Spending by Category",
        "bar_title": "Spending by Entry",
        "cumulative_title": "Cumulative Spending",
        "cumulative_x": "# Entries",
        "currency_log_header": "Currency Log",
        "currency_log_caption": "All currencies detected in your expenses",
        "col_currency": "Currency",
        "col_transactions": "Transactions",
        "col_total_original": "Total (original)",
        "col_total_converted": "Converted",
        "status_good": "You're doing great! Keep it up.",
        "status_warning": "Careful, you're using up your budget.",
        "status_danger": "Alert! You're almost out of budget.",
        "status_over": "You have exceeded your budget!",
        "budget_used": "Budget used",
        "categories": ["Food", "Transport", "Housing", "Entertainment",
                       "Health", "Shopping", "Bar", "Activity & Museums",
                       "Hotel", "Telephone", "Other"],
        "try_it_title": "Try it out",
        "try_it_body": ("Want to see what this app can do? Download "
                        "<a href='https://github.com/stefhooy/Budget-Calculator-Exchange"
                        "/blob/main/data/statswinter24.csv' target='_blank' style='color:#5dade2;'>"
                        "<strong>statswinter24.csv</strong></a> from the GitHub repo and upload it here. "
                        "It contains real spending data across 5 months and 8 countries "
                        "with multiple currencies (HUF, EUR, CAD, SEK, TRY)."),
        "bar_country_title": "Spending by Country",
        "monthly_chart_title": "Monthly Spending vs Budget",
        "monthly_x": "Month",
        "monthly_budget_line": "Monthly Budget",
        "country_drill_header": "Country Deep Dive",
        "select_country": "Select a country to explore",
        "all_label": "All countries",
        "drill_total": "Total spent",
        "drill_pie_title": "Categories in",
        "drill_timeline_title": "Monthly spending in",
        "setup_loaded_msg": "expenses loaded from file. Now set your total budget to continue.",
        "setup_go_btn": "Let's go",
    },
    "FR": {
        "title": "Calculateur de Budget: Échange",
        "subtitle": "Suivez vos dépenses à l'étranger, gardez le contrôle.",
        "hero_image": "hero_fr.jpg",
        "hero_tagline": "Édition Échange · Remasterisé 2026",
        "landing_title": "Bienvenue",
        "landing_subtitle": "Vos données ne quittent jamais votre appareil. Importez un fichier pour continuer ou commencez à nouveau.",
        "upload_section": "Importer votre fichier",
        "upload_label": "Acceptés : .json, .csv ou .xlsx (voir structure ci-dessous)",
        "fresh_btn": "Nouveau départ",
        "upload_error": "Impossible de lire ce fichier. Vérifiez que la structure correspond.",
        "preview_title": "Structure attendue du fichier",
        "preview_caption_simple": "Format simple (exporté par cette app)",
        "preview_caption_legacy": "Format legacy (style statswinter24.csv, également supporté)",
        "setup_header": "Configuration du Budget",
        "total_budget": "Budget Total",
        "budget_currency": "Devise du Budget",
        "display_currency": "Devise d'Affichage",
        "rates_note": "Taux : moyennes annuelles approx. 2024",
        "duration": "Durée de l'échange (mois)",
        "init_btn": "Définir le Budget Total",
        "add_header": "Ajouter une Dépense",
        "amount": "Montant",
        "exp_currency": "Devise de la Dépense",
        "description": "Description",
        "category": "Catégorie",
        "add_btn": "Ajouter la Dépense",
        "clear_btn": "Effacer Toutes les Dépenses",
        "reset_btn": "Réinitialiser (Nouvelle Session)",
        "download_header": "Sauvegarder vos données",
        "download_caption": "Téléchargez avant de fermer l'onglet !",
        "save_btn": "Télécharger budget.json",
        "export_csv": "Exporter en CSV",
        "overview_header": "Vue d'Ensemble du Budget",
        "initial": "Budget Total",
        "spent": "Total Dépensé",
        "remaining": "Restant",
        "monthly": "Budget Mensuel",
        "weekly": "Budget Hebdomadaire",
        "expenses_header": "Journal des Dépenses",
        "no_expenses": "Aucune dépense enregistrée.",
        "charts_header": "Répartition des Dépenses",
        "pie_title": "Dépenses par Catégorie",
        "bar_title": "Dépenses par Entrée",
        "cumulative_title": "Dépenses Cumulées",
        "cumulative_x": "Entrées",
        "currency_log_header": "Journal des Devises",
        "currency_log_caption": "Toutes les devises détectées dans vos dépenses",
        "col_currency": "Devise",
        "col_transactions": "Transactions",
        "col_total_original": "Total (original)",
        "col_total_converted": "Converti",
        "status_good": "Vous gérez très bien votre budget !",
        "status_warning": "Attention, vous consommez votre budget.",
        "status_danger": "Alerte ! Vous êtes presque à court de budget.",
        "status_over": "Vous avez dépassé votre budget !",
        "budget_used": "Budget utilisé",
        "categories": ["Nourriture", "Transport", "Logement", "Loisirs",
                       "Santé", "Shopping", "Bar", "Activités & Musées",
                       "Hôtel", "Téléphone", "Autre"],
        "try_it_title": "Essayez !",
        "try_it_body": ("Vous voulez voir ce que cette app peut faire ? Téléchargez "
                        "<a href='https://github.com/stefhooy/Budget-Calculator-Exchange"
                        "/blob/main/data/statswinter24.csv' target='_blank' style='color:#5dade2;'>"
                        "<strong>statswinter24.csv</strong></a> depuis le dépôt GitHub et importez-le ici. "
                        "Il contient des données réelles sur 5 mois et 8 pays "
                        "avec plusieurs devises (HUF, EUR, CAD, SEK, TRY)."),
        "bar_country_title": "Dépenses par Pays",
        "monthly_chart_title": "Dépenses Mensuelles vs Budget",
        "monthly_x": "Mois",
        "monthly_budget_line": "Budget Mensuel",
        "country_drill_header": "Analyse par Pays",
        "select_country": "Sélectionner un pays",
        "all_label": "Tous les pays",
        "drill_total": "Total dépensé",
        "drill_pie_title": "Catégories en",
        "drill_timeline_title": "Dépenses mensuelles en",
        "setup_loaded_msg": "dépenses chargées. Définissez votre budget total pour continuer.",
        "setup_go_btn": "C'est parti",
    },
    "ES": {
        "title": "Calculadora de Presupuesto: Intercambio",
        "subtitle": "Controla tus gastos en el extranjero, mantén el control.",
        "hero_image": "hero_es.jpg",
        "hero_tagline": "Edición Intercambio · Remasterizado 2026",
        "landing_title": "Bienvenido",
        "landing_subtitle": "Tus datos nunca salen de tu dispositivo. Sube un archivo para continuar o empieza desde cero.",
        "upload_section": "Subir tu archivo",
        "upload_label": "Formatos: .json, .csv o .xlsx (ver estructura abajo)",
        "fresh_btn": "Empezar de cero",
        "upload_error": "No se pudo leer el archivo. Comprueba que la estructura coincide.",
        "preview_title": "Estructura esperada del archivo",
        "preview_caption_simple": "Formato simple (exportado por esta app)",
        "preview_caption_legacy": "Formato legacy (estilo statswinter24.csv, también soportado)",
        "setup_header": "Configuración del Presupuesto",
        "total_budget": "Presupuesto Total",
        "budget_currency": "Moneda del Presupuesto",
        "display_currency": "Moneda de Visualización",
        "rates_note": "Tasas: medias anuales aprox. 2024",
        "duration": "Duración del intercambio (meses)",
        "init_btn": "Establecer Presupuesto Total",
        "add_header": "Añadir Gasto",
        "amount": "Cantidad",
        "exp_currency": "Moneda del Gasto",
        "description": "Descripción",
        "category": "Categoría",
        "add_btn": "Añadir Gasto",
        "clear_btn": "Borrar Todos los Gastos",
        "reset_btn": "Reiniciar (Nueva Sesión)",
        "download_header": "Guardar tus datos",
        "download_caption": "¡Descarga antes de cerrar la pestaña!",
        "save_btn": "Descargar budget.json",
        "export_csv": "Exportar a CSV",
        "overview_header": "Resumen del Presupuesto",
        "initial": "Presupuesto Total",
        "spent": "Total Gastado",
        "remaining": "Restante",
        "monthly": "Presupuesto Mensual",
        "weekly": "Presupuesto Semanal",
        "expenses_header": "Registro de Gastos",
        "no_expenses": "Ningún gasto registrado todavía.",
        "charts_header": "Desglose de Gastos",
        "pie_title": "Gastos por Categoría",
        "bar_title": "Gastos por Entrada",
        "cumulative_title": "Gastos Acumulados",
        "cumulative_x": "Entradas",
        "currency_log_header": "Registro de Monedas",
        "currency_log_caption": "Todas las monedas detectadas en tus gastos",
        "col_currency": "Moneda",
        "col_transactions": "Transacciones",
        "col_total_original": "Total (original)",
        "col_total_converted": "Convertido",
        "status_good": "¡Lo estás haciendo genial! Sigue así.",
        "status_warning": "Cuidado, estás agotando tu presupuesto.",
        "status_danger": "¡Alerta! Estás casi sin presupuesto.",
        "status_over": "¡Has superado tu presupuesto!",
        "budget_used": "Presupuesto usado",
        "categories": ["Comida", "Transporte", "Alojamiento", "Ocio",
                       "Salud", "Compras", "Bar", "Actividades & Museos",
                       "Hotel", "Teléfono", "Otro"],
        "try_it_title": "Pruébalo",
        "try_it_body": ("¿Quieres ver lo que puede hacer esta app? Descarga "
                        "<a href='https://github.com/stefhooy/Budget-Calculator-Exchange"
                        "/blob/main/data/statswinter24.csv' target='_blank' style='color:#5dade2;'>"
                        "<strong>statswinter24.csv</strong></a> del repositorio de GitHub y súbelo aquí. "
                        "Contiene datos reales de gastos durante 5 meses y 8 países "
                        "con múltiples divisas (HUF, EUR, CAD, SEK, TRY)."),
        "bar_country_title": "Gastos por País",
        "monthly_chart_title": "Gastos Mensuales vs Presupuesto",
        "monthly_x": "Mes",
        "monthly_budget_line": "Presupuesto Mensual",
        "country_drill_header": "Análisis por País",
        "select_country": "Seleccionar un país",
        "all_label": "Todos los países",
        "drill_total": "Total gastado",
        "drill_pie_title": "Categorías en",
        "drill_timeline_title": "Gastos mensuales en",
        "setup_loaded_msg": "gastos cargados. Establece tu presupuesto total para continuar.",
        "setup_go_btn": "¡Vamos!",
    },
}

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

# ── File parsing ──────────────────────────────────────────────────────────────
def _parse_amount(raw: str) -> float:
    cleaned = re.sub(r"[^\d.,]", "", str(raw).strip())
    cleaned = re.sub(r",(\d{3})(?=\.)", r"\1", cleaned)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _df_to_expenses(df: pd.DataFrame) -> list[dict]:
    cols = [c.strip() for c in df.columns]
    df.columns = cols

    # App export format
    if "Amount" in cols and "Description" in cols:
        expenses = []
        for _, row in df.iterrows():
            expenses.append({
                "Amount":      float(row.get("Amount", 0)),
                "Currency":    str(row.get("Currency", "EUR")),
                "Description": str(row.get("Description", "")),
                "Category":    str(row.get("Category", "Other")),
                "Date":        str(row.get("Date", str(date.today()))),
            })
        return expenses

    # Legacy format (statswinter24.csv)
    if "Spending" in cols and "Type of Expense" in cols:
        expenses = []
        for _, row in df.iterrows():
            raw_spending = str(row.get("Spending", "0"))
            amount = _parse_amount(raw_spending)
            if amount == 0:
                continue
            currency = _detect_currency(raw_spending)
            month_str = str(row.get("Month", "")).strip().lower()
            month_num = MONTH_MAP.get(month_str, "01")
            year = str(row.get("Year", "2024")).strip()
            expenses.append({
                "Amount":      amount,
                "Currency":    currency,
                "Description": str(row.get("Country", "")).strip(),
                "Category":    str(row.get("Type of Expense", "Other")).strip(),
                "Date":        f"{year}-{month_num}-01",
            })
        return expenses

    return []


def parse_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".json"):
            data = json.load(uploaded_file)
            if "expenses" not in data:
                return None, "JSON must contain an 'expenses' key."
            return data, None

        elif name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            expenses = _df_to_expenses(df)
            return {"initial_budget": None, "exchange_duration": None,
                    "budget_currency": "EUR", "expenses": expenses}, None

        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            expenses = _df_to_expenses(df)
            return {"initial_budget": None, "exchange_duration": None,
                    "budget_currency": "EUR", "expenses": expenses}, None

        return None, "Unsupported file type."
    except Exception as e:
        return None, str(e)


# ── Session state ─────────────────────────────────────────────────────────────
def _default(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_default("language",         "EN")
_default("data_loaded",      False)
_default("initial_budget",   None)
_default("exchange_duration",None)
_default("budget_currency",  "EUR")
_default("display_currency", "EUR")
_default("expenses",         [])

def session_to_json() -> bytes:
    return json.dumps({
        "initial_budget":    st.session_state.initial_budget,
        "exchange_duration": st.session_state.exchange_duration,
        "budget_currency":   st.session_state.budget_currency,
        "expenses":          st.session_state.expenses,
    }, indent=2, ensure_ascii=False).encode("utf-8")

def load_from_dict(d: dict):
    st.session_state.initial_budget    = d.get("initial_budget")
    st.session_state.exchange_duration = d.get("exchange_duration")
    st.session_state.budget_currency   = d.get("budget_currency", "EUR")
    st.session_state.display_currency  = d.get("budget_currency", "EUR")
    st.session_state.expenses          = d.get("expenses", [])
    st.session_state.data_loaded       = True

# ── Language toggle ───────────────────────────────────────────────────────────
c1, c2, c3, _ = st.columns([1, 1, 1, 7])
with c1:
    if st.button("🇬🇧 EN", use_container_width=True,
                 type="primary" if st.session_state.language == "EN" else "secondary"):
        st.session_state.language = "EN"; st.rerun()
with c2:
    if st.button("🇫🇷 FR", use_container_width=True,
                 type="primary" if st.session_state.language == "FR" else "secondary"):
        st.session_state.language = "FR"; st.rerun()
with c3:
    if st.button("🇪🇸 ES", use_container_width=True,
                 type="primary" if st.session_state.language == "ES" else "secondary"):
        st.session_state.language = "ES"; st.rerun()

t = LANG[st.session_state.language]
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.data_loaded:
    # ── Hero banner ───────────────────────────────────────────────────────────
    _hero_b64 = _image_b64(t["hero_image"])
    if _hero_b64:
        _bg = (f"background-image: url('{_hero_b64}');"
               "background-size: cover; background-position: center;")
        _inner_bg = "background: rgba(0,0,0,0.52);"
    else:
        _bg = ("background: linear-gradient("
               "135deg, #1a1a2e 0%, #16213e 40%, #0f3460 70%, #533483 100%);")
        _inner_bg = ""

    st.markdown(
        f"""
        <div style="{_bg} border-radius:16px; overflow:hidden; margin-bottom:28px;
                    aspect-ratio:3/1; width:100%;">
            <div style="{_inner_bg} height:100%; display:flex; flex-direction:column;
                        justify-content:center; align-items:center; text-align:center;
                        padding:0 48px;">
                <div style="font-size:3rem; margin-bottom:12px;
                            text-shadow:0 2px 8px rgba(0,0,0,0.6);">✈️ 🌍 💶</div>
                <h1 style="color:#ffffff; font-size:2.6rem; margin:0 0 10px 0;
                           font-weight:900; letter-spacing:-0.5px;
                           text-shadow:0 2px 12px rgba(0,0,0,0.8);">
                    Budget Calculator
                </h1>
                <p style="color:#f0f0f0; font-size:1.15rem; margin:0;
                          text-shadow:0 1px 6px rgba(0,0,0,0.7);">
                    {t['hero_tagline']}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title(f"👋 {t['landing_title']}")
    st.markdown(f"_{t['landing_subtitle']}_")
    st.markdown("")

    upload_col, sep_col, fresh_col = st.columns([5, 1, 3], gap="small")

    with upload_col:
        st.markdown(f"### {t['upload_section']}")
        uploaded = st.file_uploader(t["upload_label"], type=["json","csv","xlsx","xls"],
                                    label_visibility="visible")
        if uploaded is not None:
            result, err = parse_uploaded_file(uploaded)
            if err:
                st.error(f"{t['upload_error']} ({err})")
            else:
                load_from_dict(result)
                st.toast("✅ Loaded!", icon="✅")
                st.rerun()

        st.markdown("")
        st.markdown(
            f"""
            <div style="background:#1a2f45; border-left:4px solid #3498db;
                 padding:12px 16px; border-radius:6px; margin-bottom:12px;
                 color:#ffffff;">
                <span style="font-weight:700; color:#ffffff;">🎯 {t['try_it_title']}</span><br>
                {t['try_it_body']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"📋 {t['preview_title']}", expanded=False):
            st.caption(t["preview_caption_simple"])
            st.dataframe(pd.DataFrame([
                {"Amount": 12.50, "Currency": "EUR", "Description": "Lunch",         "Category": "Food",              "Date": "2024-02-14"},
                {"Amount": 8.00,  "Currency": "EUR", "Description": "Metro",          "Category": "Transport",         "Date": "2024-02-14"},
                {"Amount": 4500,  "Currency": "HUF", "Description": "Dinner Budapest","Category": "Restaurant",        "Date": "2024-03-02"},
                {"Amount": 45.00, "Currency": "EUR", "Description": "Museum ticket",  "Category": "Activity & Museums","Date": "2024-02-15"},
            ]), hide_index=True, use_container_width=True)

            st.markdown("---")
            st.caption(t["preview_caption_legacy"])
            st.dataframe(pd.DataFrame([
                {"Spending": "9,120.00 Ft", "Type of Expense": "Restaurant",         "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Hungary"},
                {"Spending": "€ 7.80",      "Type of Expense": "Restaurant",         "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Slovakia"},
                {"Spending": "$594.00",      "Type of Expense": "Activity & Museums","Month": "April",    "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Croatia"},
            ]), hide_index=True, use_container_width=True)

    with sep_col:
        st.markdown("<div style='text-align:center;color:#aaa;padding-top:120px;"
                    "font-size:1.3rem'>or</div>", unsafe_allow_html=True)

    with fresh_col:
        st.markdown(f"### {t['fresh_btn']}")
        if st.button(t["fresh_btn"], type="primary", use_container_width=True):
            st.session_state.data_loaded = True
            st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
_dash_b64 = _image_b64(t["hero_image"])
if _dash_b64:
    _dbg = (f"background-image: url('{_dash_b64}');"
            "background-size: cover; background-position: center 40%;")
    _dinner_bg = "background: rgba(0,0,0,0.50);"
else:
    _dbg = "background: linear-gradient(90deg, #0f3460 0%, #533483 100%);"
    _dinner_bg = ""

st.markdown(
    f"""
    <div style="{_dbg} border-radius:12px; overflow:hidden; margin-bottom:20px;">
        <div style="{_dinner_bg} padding:24px 32px; display:flex;
                    align-items:center; gap:16px;">
            <span style="font-size:2rem; text-shadow:0 2px 6px rgba(0,0,0,0.6);">💶</span>
            <div>
                <span style="color:#ffffff; font-size:1.4rem; font-weight:700;
                             text-shadow:0 2px 8px rgba(0,0,0,0.8);">{t['title']}</span><br>
                <span style="color:#f0f0f0; font-size:0.95rem;
                             text-shadow:0 1px 4px rgba(0,0,0,0.7);">{t['subtitle']}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()

dc = st.session_state.display_currency   # shorthand

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header(t["setup_header"])

    # Currency pickers
    cur_col1, cur_col2 = st.columns(2)
    with cur_col1:
        bc_idx = CURRENCY_CODES.index(st.session_state.budget_currency)
        new_bc = st.selectbox(t["budget_currency"], CURRENCY_CODES,
                              index=bc_idx,
                              format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}")
        if new_bc != st.session_state.budget_currency:
            st.session_state.budget_currency = new_bc
            st.rerun()
    with cur_col2:
        dc_idx = CURRENCY_CODES.index(st.session_state.display_currency)
        new_dc = st.selectbox(t["display_currency"], CURRENCY_CODES,
                              index=dc_idx,
                              format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}")
        if new_dc != st.session_state.display_currency:
            st.session_state.display_currency = new_dc
            dc = new_dc
            st.rerun()

    st.caption(f"ℹ️ {t['rates_note']}")

    # Budget amount (shown in budget_currency)
    bc_sym = CURRENCIES[st.session_state.budget_currency]["symbol"]
    budget_in_bc = st.number_input(
        f"{t['total_budget']} ({bc_sym})",
        min_value=0.0,
        value=float(st.session_state.initial_budget or 3000.0),
        step=100.0)
    duration_input = st.number_input(
        t["duration"], min_value=1, max_value=24,
        value=int(st.session_state.exchange_duration or 5), step=1)

    if st.button(t["init_btn"], use_container_width=True, type="primary"):
        st.session_state.initial_budget    = budget_in_bc
        st.session_state.exchange_duration = duration_input
        st.rerun()

    st.divider()

    # Add expense form
    if st.session_state.initial_budget is not None:
        st.header(t["add_header"])
        with st.form("add_expense_form", clear_on_submit=True):
            exp_cur = st.selectbox(
                t["exp_currency"], CURRENCY_CODES,
                index=CURRENCY_CODES.index(st.session_state.budget_currency),
                format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}")
            exp_sym = CURRENCIES[exp_cur]["symbol"]
            exp_amount = st.number_input(
                f"{t['amount']} ({exp_sym})", min_value=0.01, value=10.0, step=0.5)
            exp_desc = st.text_input(t["description"])
            exp_cat  = st.selectbox(t["category"], t["categories"])
            exp_date = st.date_input("Date", value=date.today())
            if st.form_submit_button(t["add_btn"], use_container_width=True) and exp_desc.strip():
                st.session_state.expenses.append({
                    "Amount":      exp_amount,
                    "Currency":    exp_cur,
                    "Description": exp_desc,
                    "Category":    exp_cat,
                    "Date":        str(exp_date),
                })
                st.rerun()

        st.divider()
        if st.button(t["clear_btn"], use_container_width=True, type="secondary"):
            st.session_state.expenses = []
            st.rerun()
        if st.button(t["reset_btn"], use_container_width=True, type="secondary"):
            st.session_state.update({
                "initial_budget": None, "exchange_duration": None,
                "expenses": [], "data_loaded": False})
            st.rerun()

    st.divider()

    # Download panel
    st.markdown(
        f"""<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;
             padding:10px 14px;margin-bottom:8px;">
            <span style="font-size:1rem;font-weight:700;">💾 {t['download_header']}</span><br>
            <span style="font-size:0.82rem;color:#7a5c00;">{t['download_caption']}</span>
        </div>""", unsafe_allow_html=True)
    st.download_button(t["save_btn"], data=session_to_json(),
                       file_name="budget.json", mime="application/json",
                       use_container_width=True, type="primary")
    if st.session_state.expenses:
        csv_bytes = pd.DataFrame(st.session_state.expenses).to_csv(index=False).encode("utf-8")
        st.download_button(t["export_csv"], data=csv_bytes,
                           file_name="budget_export.csv", mime="text/csv",
                           use_container_width=True)

# ── Budget setup page (shown after file load until user sets a budget) ────────
if st.session_state.initial_budget is None:
    n_exp = len(st.session_state.expenses)
    if n_exp > 0:
        st.success(f"✅ **{n_exp}** {t['setup_loaded_msg']}")

    _, card_col, _ = st.columns([1, 3, 1])
    with card_col:
        st.markdown(
            f"""<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);
                 border-radius:16px;padding:36px 40px;margin-top:12px;">
                <h2 style="margin-top:0;">{t['setup_header']}</h2>
            </div>""",
            unsafe_allow_html=True,
        )
        setup_bc = st.selectbox(
            t["budget_currency"], CURRENCY_CODES,
            format_func=lambda c: f"{c}  {CURRENCIES[c]['symbol']}  ({CURRENCIES[c]['name']})",
            key="setup_bc")
        bc_sym = CURRENCIES[setup_bc]["symbol"]
        setup_amount = st.number_input(
            f"{t['total_budget']} ({bc_sym})",
            min_value=0.0, value=3000.0, step=100.0, key="setup_amount")
        setup_dur = st.number_input(
            t["duration"], min_value=1, max_value=24, value=5, step=1,
            key="setup_dur")
        st.caption(f"ℹ️ {t['rates_note']}")
        if st.button(t["setup_go_btn"], type="primary", use_container_width=True):
            st.session_state.initial_budget    = setup_amount
            st.session_state.budget_currency   = setup_bc
            st.session_state.display_currency  = setup_bc
            st.session_state.exchange_duration = setup_dur
            st.rerun()
    st.stop()

# ── Derived values (everything converted to display currency) ─────────────────
bc          = st.session_state.budget_currency
initial_bc  = st.session_state.initial_budget          # in budget_currency
initial_dc  = convert_amount(initial_bc, bc, dc)       # in display_currency
duration    = st.session_state.exchange_duration
total_spent = sum(to_display(e["Amount"], e.get("Currency", bc))
                  for e in st.session_state.expenses)
remaining   = initial_dc - total_spent
monthly     = initial_dc / duration
weekly      = monthly / 4
pct_used    = total_spent / initial_dc if initial_dc > 0 else 0

# ── Color status ──────────────────────────────────────────────────────────────
if pct_used >= 1.0:
    sc, sb, se, sm = "#e74c3c", "#fdecea", "🔴", t["status_over"]
elif pct_used >= 0.9:
    sc, sb, se, sm = "#e74c3c", "#fdecea", "🔴", t["status_danger"]
elif pct_used >= 0.7:
    sc, sb, se, sm = "#f39c12", "#fef9e7", "🟡", t["status_warning"]
else:
    sc, sb, se, sm = "#27ae60", "#eafaf1", "🟢", t["status_good"]

st.markdown(
    f"""<div style="background:{sb};border-left:5px solid {sc};padding:14px 18px;
         border-radius:6px;margin-bottom:16px;">
        <span style="font-size:1.1rem;color:{sc};font-weight:600;">{se} {sm}</span>
    </div>""", unsafe_allow_html=True)

st.markdown(f"**{t['budget_used']}: {pct_used*100:.1f}%**")
st.markdown(
    f"""<div style="background:#e0e0e0;border-radius:8px;height:18px;overflow:hidden;">
        <div style="width:{min(pct_used,1)*100:.1f}%;background:{sc};height:100%;border-radius:8px;"></div>
    </div>""", unsafe_allow_html=True)
st.markdown("")

# ── Metrics ───────────────────────────────────────────────────────────────────
st.subheader(t["overview_header"])
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(t["initial"],   fmt(initial_dc))
m2.metric(t["spent"],     fmt(total_spent))
m3.metric(t["remaining"], fmt(remaining),
          delta=f"{remaining - initial_dc:,.2f}" if total_spent > 0 else None,
          delta_color="inverse")
m4.metric(t["monthly"],   fmt(monthly))
m5.metric(t["weekly"],    fmt(weekly))
st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df["Amount_display"] = df.apply(
        lambda r: to_display(r["Amount"], r.get("Currency", bc)), axis=1)

    st.subheader(t["charts_header"])
    col_pie, col_bar = st.columns(2)

    with col_pie:
        cat_totals = df.groupby("Category")["Amount_display"].sum().reset_index()
        cat_totals = cat_totals.sort_values("Amount_display", ascending=False)
        cat_colors = [cat_color(n, i) for i, n in enumerate(cat_totals["Category"])]
        fig_pie = px.pie(
            cat_totals, values="Amount_display", names="Category",
            title=t["pie_title"],
            color_discrete_sequence=cat_colors,
            hole=0.4,
        )
        fig_pie.update_traces(
            textinfo="label+percent",
            textfont_size=12,
            hovertemplate=f"%{{label}}<br>{CURRENCIES[dc]['symbol']}%{{value:,.2f}} (%{{percent}})<extra></extra>",
            pull=[0.03] * len(cat_totals),
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5),
            margin=dict(t=50, b=20, r=120),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        country_totals = (
            df.groupby("Description")["Amount_display"].sum()
              .reset_index()
              .rename(columns={"Description": "Country", "Amount_display": "Total"})
              .sort_values("Total", ascending=True)
        )
        fig_bar = go.Figure(go.Bar(
            y=country_totals["Country"],
            x=country_totals["Total"],
            orientation="h",
            marker=dict(
                color=country_totals["Total"],
                colorscale="RdYlGn_r",
                showscale=False,
            ),
            text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in country_totals["Total"]],
            textposition="outside",
            hovertemplate=(f"<b>%{{y}}</b><br>{CURRENCIES[dc]['symbol']}%{{x:,.2f}}"
                           "<extra></extra>"),
        ))
        fig_bar.update_layout(
            title=t["bar_country_title"],
            xaxis_title=dc,
            margin=dict(t=50, b=20, l=10, r=80),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=max(300, len(country_totals) * 38),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    df_line = df.copy()
    df_line["Cumulative"] = df_line["Amount_display"].cumsum()
    df_line.index = range(1, len(df_line) + 1)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=list(df_line.index), y=df_line["Cumulative"],
        mode="lines+markers", line=dict(color="#3498db", width=3),
        hovertemplate=f"Entry %{{x}}: {CURRENCIES[dc]['symbol']}%{{y:,.2f}}<extra></extra>"))
    fig_line.add_hline(y=initial_dc, line_dash="dash", line_color="#e74c3c",
                       annotation_text=t["initial"], annotation_position="top right")
    fig_line.add_hline(y=initial_dc * 0.7, line_dash="dot", line_color="#f39c12",
                       annotation_text="70%", annotation_position="top right")
    fig_line.update_layout(title=t["cumulative_title"], xaxis_title=t["cumulative_x"],
                            yaxis_title=dc, plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Monthly spending vs budget ────────────────────────────────────────────
    df_monthly = df.copy()
    df_monthly["YearMonth"] = pd.to_datetime(df_monthly["Date"], errors="coerce").dt.to_period("M").astype(str)
    monthly_totals = (
        df_monthly.groupby("YearMonth")["Amount_display"].sum()
        .reset_index()
        .sort_values("YearMonth")
    )
    monthly_totals["over"] = monthly_totals["Amount_display"] > monthly
    monthly_totals["color"] = monthly_totals["over"].map({True: "#e74c3c", False: "#27ae60"})

    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly_totals["YearMonth"],
        y=monthly_totals["Amount_display"],
        marker_color=monthly_totals["color"].tolist(),
        text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in monthly_totals["Amount_display"]],
        textposition="outside",
        name=dc,
        hovertemplate=(f"<b>%{{x}}</b><br>Spent: {CURRENCIES[dc]['symbol']}%{{y:,.2f}}"
                       "<extra></extra>"),
    ))
    fig_monthly.add_hline(
        y=monthly,
        line_dash="dash",
        line_color="#f39c12",
        line_width=2,
        annotation_text=f"{t['monthly_budget_line']}: {fmt(monthly)}",
        annotation_position="top left",
        annotation_font_color="#f39c12",
    )
    fig_monthly.update_layout(
        title=t["monthly_chart_title"],
        xaxis=dict(title=t["monthly_x"], type="category"),
        yaxis_title=dc,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=40),
        showlegend=False,
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # ── Country drill-down ────────────────────────────────────────────────────
    st.divider()
    st.subheader(f"🔍 {t['country_drill_header']}")

    countries_list = sorted(df["Description"].dropna().unique().tolist())
    selected_country = st.selectbox(
        t["select_country"],
        [t["all_label"]] + countries_list,
        key="country_drill_select",
    )

    if selected_country != t["all_label"]:
        df_c = df[df["Description"] == selected_country].copy()
        total_c = df_c["Amount_display"].sum()

        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric(t["drill_total"], fmt(total_c))
        m_c2.metric("% of budget", f"{total_c / initial_dc * 100:.1f}%")
        m_c3.metric("Transactions", len(df_c))

        drill_pie_col, drill_bar_col = st.columns(2)

        with drill_pie_col:
            cat_c = df_c.groupby("Category")["Amount_display"].sum().reset_index()
            cat_c = cat_c.sort_values("Amount_display", ascending=False)
            drill_colors = [cat_color(n, i) for i, n in enumerate(cat_c["Category"])]
            fig_drill_pie = px.pie(
                cat_c, values="Amount_display", names="Category",
                title=f"{t['drill_pie_title']} {selected_country}",
                color_discrete_sequence=drill_colors,
                hole=0.4,
            )
            fig_drill_pie.update_traces(
                textinfo="label+percent",
                textfont_size=12,
                hovertemplate=(f"%{{label}}<br>{CURRENCIES[dc]['symbol']}%{{value:,.2f}}"
                               " (%{{percent}})<extra></extra>"),
                pull=[0.03] * len(cat_c),
            )
            fig_drill_pie.update_layout(
                margin=dict(t=50, b=20, r=120),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_drill_pie, use_container_width=True)

        with drill_bar_col:
            df_c["YearMonth"] = pd.to_datetime(df_c["Date"], errors="coerce").dt.to_period("M").astype(str)
            timeline_c = df_c.groupby("YearMonth")["Amount_display"].sum().reset_index()
            timeline_c = timeline_c.sort_values("YearMonth")
            fig_drill_time = go.Figure(go.Bar(
                x=timeline_c["YearMonth"],
                y=timeline_c["Amount_display"],
                marker_color="#3498db",
                text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in timeline_c["Amount_display"]],
                textposition="outside",
                hovertemplate=f"<b>%{{x}}</b><br>{CURRENCIES[dc]['symbol']}%{{y:,.2f}}<extra></extra>",
            ))
            fig_drill_time.update_layout(
                title=f"{t['drill_timeline_title']} {selected_country}",
                xaxis=dict(title=t["monthly_x"], type="category"),
                yaxis_title=dc,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=40),
            )
            st.plotly_chart(fig_drill_time, use_container_width=True)

    st.divider()

    # ── Currency log ──────────────────────────────────────────────────────────
    st.subheader(t["currency_log_header"])
    st.caption(t["currency_log_caption"])

    cur_rows = []
    for cur_code, grp in df.groupby("Currency"):
        total_orig = grp["Amount"].sum()
        total_conv = grp["Amount_display"].sum()
        cur_rows.append({
            t["col_currency"]:    f"{cur_code}  {CURRENCIES.get(cur_code, {}).get('symbol', '')}  "
                                  f"({CURRENCIES.get(cur_code, {}).get('name', cur_code)})",
            t["col_transactions"]: len(grp),
            t["col_total_original"]: (f"{CURRENCIES.get(cur_code, {}).get('symbol', '')}"
                                      f"{total_orig:,.2f}"),
            t["col_total_converted"]: fmt(total_conv),
        })

    cur_df = pd.DataFrame(cur_rows)
    st.dataframe(cur_df, hide_index=True, use_container_width=True)

    st.divider()

    # ── Expense table ─────────────────────────────────────────────────────────
    st.subheader(t["expenses_header"])
    for cw, label in zip(st.columns([2, 2, 3, 3, 2, 2, 1]),
                         ["Date", "Category", "Description",
                          t["col_currency"], "Original", f"In {dc}", ""]):
        cw.markdown(f"**{label}**")

    for i, exp in enumerate(st.session_state.expenses):
        exp_dc_amount = to_display(exp["Amount"], exp.get("Currency", bc))
        pct = exp_dc_amount / initial_dc
        if pct >= 0.1:
            bg, txt = "rgba(220,50,50,0.30)", "#ffcccc"
        elif pct >= 0.05:
            bg, txt = "rgba(243,156,18,0.30)", "#ffe8a0"
        else:
            bg, txt = "rgba(39,174,96,0.22)", "#b0f0c8"
        cur_code = exp.get("Currency", bc)
        orig_fmt = f"{CURRENCIES.get(cur_code, {}).get('symbol', '')}{exp['Amount']:,.2f}"
        cols = st.columns([2, 2, 3, 3, 2, 2, 1])
        for cw, val in zip(cols[:6], [exp["Date"], exp["Category"], exp["Description"],
                                       f"{cur_code} {CURRENCIES.get(cur_code,{}).get('symbol','')}",
                                       orig_fmt, fmt(exp_dc_amount)]):
            cw.markdown(
                f'<div style="background:{bg};color:{txt};padding:4px 8px;'
                f'border-radius:4px;font-size:0.9rem">{val}</div>',
                unsafe_allow_html=True)
        if cols[6].button("✕", key=f"del_{i}"):
            st.session_state.expenses.pop(i)
            st.rerun()

else:
    st.subheader(t["expenses_header"])
    st.info(t["no_expenses"])
