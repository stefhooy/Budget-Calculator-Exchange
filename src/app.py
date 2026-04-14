import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import json
import re
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Budget Calculator | Calculateur Budget",
    page_icon="💶",
    layout="wide",
)

# ── Inject beforeunload warning ───────────────────────────────────────────────
st.markdown("""
<script>
    window.addEventListener('beforeunload', function(e) {
        e.preventDefault();
        e.returnValue = '';
    });
</script>
""", unsafe_allow_html=True)

# ── Language strings ──────────────────────────────────────────────────────────
LANG = {
    "EN": {
        "title": "Budget Calculator — Exchange Edition",
        "subtitle": "Track your spending abroad, stay in control.",
        "landing_title": "Welcome — restore a session or start fresh",
        "landing_subtitle": "Your data never leaves your device. Upload a file to continue where you left off, or start from scratch.",
        "upload_section": "Upload your file",
        "upload_label": "Accepted formats: .json (app export), .csv or .xlsx (see structure below)",
        "upload_btn": "Load",
        "fresh_btn": "Start fresh",
        "upload_error": "Could not read that file. Check the format matches the structure shown below.",
        "preview_title": "Expected file structure",
        "preview_caption_simple": "Simple format (exported by this app)",
        "preview_caption_legacy": "Legacy format (statswinter24.csv style — also supported)",
        "setup_header": "Budget Setup",
        "initial_budget": "Total Budget ($)",
        "duration": "Exchange Duration (months)",
        "init_btn": "Set Total Budget",
        "add_header": "Add Expense",
        "amount": "Amount ($)",
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
        "initial": "Initial Budget",
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
        "status_good": "You're doing great! Keep it up.",
        "status_warning": "Careful — you're using up your budget.",
        "status_danger": "Alert! You're almost out of budget.",
        "status_over": "You have exceeded your budget!",
        "budget_used": "Budget used",
        "categories": ["Food", "Transport", "Housing", "Entertainment", "Health", "Shopping", "Bar", "Activity & Museums", "Hotel", "Telephone", "Other"],
    },
    "FR": {
        "title": "Calculateur de Budget — Échange",
        "subtitle": "Suivez vos dépenses à l'étranger, gardez le contrôle.",
        "landing_title": "Bienvenue — restaurez une session ou repartez de zéro",
        "landing_subtitle": "Vos données ne quittent jamais votre appareil. Importez un fichier pour continuer ou commencez à nouveau.",
        "upload_section": "Importer votre fichier",
        "upload_label": "Formats acceptés : .json (export app), .csv ou .xlsx (voir structure ci-dessous)",
        "upload_btn": "Charger",
        "fresh_btn": "Nouveau départ",
        "upload_error": "Impossible de lire ce fichier. Vérifiez que la structure correspond à celle indiquée.",
        "preview_title": "Structure attendue du fichier",
        "preview_caption_simple": "Format simple (exporté par cette app)",
        "preview_caption_legacy": "Format legacy (style statswinter24.csv — également supporté)",
        "setup_header": "Configuration du Budget",
        "initial_budget": "Budget Total ($)",
        "duration": "Durée de l'échange (mois)",
        "init_btn": "Définir le Budget Total",
        "add_header": "Ajouter une Dépense",
        "amount": "Montant ($)",
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
        "initial": "Budget Initial",
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
        "status_good": "Vous gérez très bien votre budget !",
        "status_warning": "Attention — vous consommez votre budget.",
        "status_danger": "Alerte ! Vous êtes presque à court de budget.",
        "status_over": "Vous avez dépassé votre budget !",
        "budget_used": "Budget utilisé",
        "categories": ["Nourriture", "Transport", "Logement", "Loisirs", "Santé", "Shopping", "Bar", "Activités & Musées", "Hôtel", "Téléphone", "Autre"],
    },
    "ES": {
        "title": "Calculadora de Presupuesto — Intercambio",
        "subtitle": "Controla tus gastos en el extranjero, mantén el control.",
        "landing_title": "Bienvenido — restaura una sesión o empieza de cero",
        "landing_subtitle": "Tus datos nunca salen de tu dispositivo. Sube un archivo para continuar donde lo dejaste, o empieza desde cero.",
        "upload_section": "Subir tu archivo",
        "upload_label": "Formatos aceptados: .json (exportado por la app), .csv o .xlsx (ver estructura abajo)",
        "upload_btn": "Cargar",
        "fresh_btn": "Empezar de cero",
        "upload_error": "No se pudo leer el archivo. Comprueba que la estructura coincide con la indicada abajo.",
        "preview_title": "Estructura esperada del archivo",
        "preview_caption_simple": "Formato simple (exportado por esta app)",
        "preview_caption_legacy": "Formato legacy (estilo statswinter24.csv — también soportado)",
        "setup_header": "Configuración del Presupuesto",
        "initial_budget": "Presupuesto Total ($)",
        "duration": "Duración del intercambio (meses)",
        "init_btn": "Establecer Presupuesto Total",
        "add_header": "Añadir Gasto",
        "amount": "Cantidad ($)",
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
        "initial": "Presupuesto Inicial",
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
        "status_good": "¡Lo estás haciendo genial! Sigue así.",
        "status_warning": "Cuidado — estás agotando tu presupuesto.",
        "status_danger": "¡Alerta! Estás casi sin presupuesto.",
        "status_over": "¡Has superado tu presupuesto!",
        "budget_used": "Presupuesto usado",
        "categories": ["Comida", "Transporte", "Alojamiento", "Ocio", "Salud", "Compras", "Bar", "Actividades & Museos", "Hotel", "Teléfono", "Otro"],
    },
}

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

# ── File parsing helpers ──────────────────────────────────────────────────────
def _parse_amount(raw: str) -> float:
    """Strip currency symbols and parse a float from messy strings like '9,120.00 Ft' or '€ 7.80'."""
    cleaned = re.sub(r"[^\d.,]", "", str(raw).strip())
    # Remove thousand-separator commas (e.g. "9,120.00" → "9120.00")
    # Heuristic: if there's a comma followed by exactly 3 digits then a dot, it's a thousand sep
    cleaned = re.sub(r",(\d{3})(?=\.)", r"\1", cleaned)
    # Remove remaining commas (some locales use comma as decimal — handle edge case)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _df_to_expenses(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to the app's internal expense list format.
    Supports both the app's own export format and the legacy statswinter24.csv format.
    """
    cols = [c.strip() for c in df.columns]
    df.columns = cols

    # ── App export format: Amount, Description, Category, Date ───────────────
    if "Amount" in cols and "Description" in cols:
        expenses = []
        for _, row in df.iterrows():
            expenses.append({
                "Amount": float(row.get("Amount", 0)),
                "Description": str(row.get("Description", "")),
                "Category": str(row.get("Category", "Other")),
                "Date": str(row.get("Date", str(date.today()))),
            })
        return expenses

    # ── Legacy format: Spending, Type of Expense, Month, Country ─────────────
    if "Spending" in cols and "Type of Expense" in cols:
        expenses = []
        for _, row in df.iterrows():
            amount = _parse_amount(str(row.get("Spending", "0")))
            if amount == 0:
                continue
            month_str = str(row.get("Month", "")).strip().lower()
            month_num = MONTH_MAP.get(month_str, "01")
            year = str(row.get("Year", "2024")).strip()
            exp_date = f"{year}-{month_num}-01"
            country = str(row.get("Country", "")).strip()
            category = str(row.get("Type of Expense", "Other")).strip()
            expenses.append({
                "Amount": amount,
                "Description": country,
                "Category": category,
                "Date": exp_date,
            })
        return expenses

    return []


def parse_uploaded_file(uploaded_file) -> tuple[dict | None, str | None]:
    """Return (state_dict, error_message). state_dict is None on failure."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".json"):
            data = json.load(uploaded_file)
            # Validate minimal structure
            if "expenses" not in data:
                return None, "JSON must contain an 'expenses' key."
            return data, None

        elif name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            expenses = _df_to_expenses(df)
            total = round(sum(e["Amount"] for e in expenses), 2)
            return {"initial_budget": total, "exchange_duration": 5, "expenses": expenses}, None

        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            expenses = _df_to_expenses(df)
            total = round(sum(e["Amount"] for e in expenses), 2)
            return {"initial_budget": total, "exchange_duration": 5, "expenses": expenses}, None

        else:
            return None, "Unsupported file type."

    except Exception as e:
        return None, str(e)


# ── Session state defaults ────────────────────────────────────────────────────
def _default(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_default("language", "EN")
_default("data_loaded", False)
_default("initial_budget", None)
_default("exchange_duration", None)
_default("expenses", [])

# ── Helpers ───────────────────────────────────────────────────────────────────
def session_to_json() -> bytes:
    return json.dumps({
        "initial_budget": st.session_state.initial_budget,
        "exchange_duration": st.session_state.exchange_duration,
        "expenses": st.session_state.expenses,
    }, indent=2, ensure_ascii=False).encode("utf-8")

def load_from_dict(d: dict):
    st.session_state.initial_budget = d.get("initial_budget")
    st.session_state.exchange_duration = d.get("exchange_duration")
    st.session_state.expenses = d.get("expenses", [])
    st.session_state.data_loaded = True

# ── Language toggle ───────────────────────────────────────────────────────────
c1, c2, c3, c_space = st.columns([1, 1, 1, 7])
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
    st.title(f"💶 {t['landing_title']}")
    st.markdown(f"_{t['landing_subtitle']}_")
    st.markdown("")

    upload_col, sep_col, fresh_col = st.columns([5, 1, 3], gap="small")

    with upload_col:
        st.markdown(f"### {t['upload_section']}")
        uploaded = st.file_uploader(
            t["upload_label"],
            type=["json", "csv", "xlsx", "xls"],
            label_visibility="visible",
        )
        if uploaded is not None:
            result, err = parse_uploaded_file(uploaded)
            if err:
                st.error(f"{t['upload_error']} ({err})")
            else:
                load_from_dict(result)
                st.toast("✅ Loaded!", icon="✅")
                st.rerun()

        # ── Structure preview ─────────────────────────────────────────────────
        st.markdown("")
        with st.expander(f"📋 {t['preview_title']}", expanded=False):
            st.caption(t["preview_caption_simple"])
            simple_example = pd.DataFrame([
                {"Amount": 12.50, "Description": "Lunch at market", "Category": "Food", "Date": "2024-02-14"},
                {"Amount": 8.00,  "Description": "Metro",           "Category": "Transport", "Date": "2024-02-14"},
                {"Amount": 45.00, "Description": "Museum ticket",   "Category": "Activity & Museums", "Date": "2024-02-15"},
            ])
            st.dataframe(simple_example, hide_index=True, use_container_width=True)

            st.markdown("---")
            st.caption(t["preview_caption_legacy"])
            legacy_example = pd.DataFrame([
                {"Spending": "9,120.00 Ft", "Type of Expense": "Restaurant",          "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Hungary"},
                {"Spending": "€ 7.80",      "Type of Expense": "Restaurant",          "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Slovakia"},
                {"Spending": "$594.00",      "Type of Expense": "Activity & Museums", "Month": "April",    "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Croatia"},
            ])
            st.dataframe(legacy_example, hide_index=True, use_container_width=True)

    with sep_col:
        st.markdown("<div style='text-align:center;color:#aaa;padding-top:120px;font-size:1.3rem'>or</div>",
                    unsafe_allow_html=True)

    with fresh_col:
        st.markdown(f"### {t['fresh_btn']}")
        st.caption("Set up a new budget from scratch." if st.session_state.language == "EN"
                   else "Configurez un nouveau budget." if st.session_state.language == "FR"
                   else "Configura un nuevo presupuesto.")
        st.markdown("")
        if st.button(t["fresh_btn"], type="primary", use_container_width=True):
            st.session_state.initial_budget = None
            st.session_state.exchange_duration = None
            st.session_state.expenses = []
            st.session_state.data_loaded = True
            st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
st.title(f"💶 {t['title']}")
st.caption(t["subtitle"])
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header(t["setup_header"])
    initial_budget_input = st.number_input(
        t["initial_budget"], min_value=0.0,
        value=float(st.session_state.initial_budget or 3000.0), step=100.0)
    duration_input = st.number_input(
        t["duration"], min_value=1, max_value=24,
        value=int(st.session_state.exchange_duration or 5), step=1)

    if st.button(t["init_btn"], use_container_width=True, type="primary"):
        st.session_state.initial_budget = initial_budget_input
        st.session_state.exchange_duration = duration_input
        st.session_state.expenses = []
        st.rerun()

    st.divider()

    if st.session_state.initial_budget is not None:
        st.header(t["add_header"])
        with st.form("add_expense_form", clear_on_submit=True):
            exp_amount = st.number_input(t["amount"], min_value=0.01, value=10.0, step=0.5)
            exp_desc   = st.text_input(t["description"])
            exp_cat    = st.selectbox(t["category"], t["categories"])
            exp_date   = st.date_input("Date", value=date.today())
            if st.form_submit_button(t["add_btn"], use_container_width=True) and exp_desc.strip():
                st.session_state.expenses.append({
                    "Amount": exp_amount,
                    "Description": exp_desc,
                    "Category": exp_cat,
                    "Date": str(exp_date),
                })
                st.rerun()

        st.divider()
        if st.button(t["clear_btn"], use_container_width=True, type="secondary"):
            st.session_state.expenses = []
            st.rerun()
        if st.button(t["reset_btn"], use_container_width=True, type="secondary"):
            for k in ("initial_budget", "exchange_duration", "expenses"):
                st.session_state[k] = None if k != "expenses" else []
            st.session_state.data_loaded = False
            st.rerun()

    st.divider()

    # ── Always-visible download panel ────────────────────────────────────────
    st.markdown(
        f"""<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;
             padding:10px 14px;margin-bottom:8px;">
            <span style="font-size:1rem;font-weight:700;">💾 {t['download_header']}</span><br>
            <span style="font-size:0.82rem;color:#7a5c00;">{t['download_caption']}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.download_button(t["save_btn"], data=session_to_json(),
                       file_name="budget.json", mime="application/json",
                       use_container_width=True, type="primary")
    if st.session_state.expenses:
        csv_bytes = pd.DataFrame(st.session_state.expenses).to_csv(index=False).encode("utf-8")
        st.download_button(t["export_csv"], data=csv_bytes,
                           file_name="budget_export.csv", mime="text/csv",
                           use_container_width=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if st.session_state.initial_budget is None:
    st.info("👈 " + t["setup_header"])
    st.stop()

# ── Derived values ────────────────────────────────────────────────────────────
initial     = st.session_state.initial_budget
duration    = st.session_state.exchange_duration
total_spent = sum(e["Amount"] for e in st.session_state.expenses)
remaining   = initial - total_spent
monthly     = initial / duration
weekly      = monthly / 4
pct_used    = total_spent / initial if initial > 0 else 0

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
    </div>""",
    unsafe_allow_html=True,
)
st.markdown(f"**{t['budget_used']}: {pct_used*100:.1f}%**")
st.markdown(
    f"""<div style="background:#e0e0e0;border-radius:8px;height:18px;overflow:hidden;">
        <div style="width:{min(pct_used,1)*100:.1f}%;background:{sc};height:100%;border-radius:8px;"></div>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown("")

# ── Metrics ───────────────────────────────────────────────────────────────────
st.subheader(t["overview_header"])
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(t["initial"],  f"${initial:,.2f}")
m2.metric(t["spent"],    f"${total_spent:,.2f}")
m3.metric(t["remaining"], f"${remaining:,.2f}",
          delta=f"{remaining - initial:,.2f}" if total_spent > 0 else None, delta_color="inverse")
m4.metric(t["monthly"],  f"${monthly:,.2f}")
m5.metric(t["weekly"],   f"${weekly:,.2f}")
st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    st.subheader(t["charts_header"])
    col_pie, col_bar = st.columns(2)

    with col_pie:
        cat_totals = df.groupby("Category")["Amount"].sum().reset_index()
        cat_totals["pct"] = cat_totals["Amount"] / initial
        cat_totals["color"] = cat_totals["pct"].apply(
            lambda p: "#e74c3c" if p >= 0.3 else ("#f39c12" if p >= 0.15 else "#27ae60"))
        fig_pie = px.pie(cat_totals, values="Amount", names="Category", title=t["pie_title"],
                         color_discrete_sequence=cat_totals["color"].tolist(), hole=0.4)
        fig_pie.update_traces(textinfo="label+percent", hovertemplate="%{label}: $%{value:,.2f}")
        fig_pie.update_layout(showlegend=True, margin=dict(t=50, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        df_plot = df.copy()
        df_plot["pct_of_budget"] = df_plot["Amount"] / initial
        df_plot["bar_color"] = df_plot["pct_of_budget"].apply(
            lambda p: "#e74c3c" if p >= 0.1 else ("#f39c12" if p >= 0.05 else "#27ae60"))
        fig_bar = go.Figure(go.Bar(
            x=df_plot["Description"], y=df_plot["Amount"],
            marker_color=df_plot["bar_color"].tolist(),
            hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",
        ))
        fig_bar.update_layout(title=t["bar_title"], xaxis_tickangle=-30, yaxis_title="$",
                               margin=dict(t=50, b=60),
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Cumulative line
    df_line = df.copy()
    df_line["Cumulative"] = df_line["Amount"].cumsum()
    df_line.index = range(1, len(df_line) + 1)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=list(df_line.index), y=df_line["Cumulative"],
        mode="lines+markers", line=dict(color="#3498db", width=3),
        hovertemplate="Entry %{x}: $%{y:,.2f}<extra></extra>"))
    fig_line.add_hline(y=initial, line_dash="dash", line_color="#e74c3c",
                       annotation_text=t["initial"], annotation_position="top right")
    fig_line.add_hline(y=initial * 0.7, line_dash="dot", line_color="#f39c12",
                       annotation_text="70%", annotation_position="top right")
    fig_line.update_layout(title=t["cumulative_title"], xaxis_title=t["cumulative_x"],
                            yaxis_title="$", plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ── Expense table ─────────────────────────────────────────────────────────
    st.subheader(t["expenses_header"])
    for col_w, label in zip(st.columns([2, 3, 4, 2, 1]),
                            ["Date", "Category", "Description", "Amount", ""]):
        col_w.markdown(f"**{label}**")

    for i, exp in enumerate(st.session_state.expenses):
        pct = exp["Amount"] / initial
        bg = "#fdecea" if pct >= 0.1 else ("#fef9e7" if pct >= 0.05 else "#eafaf1")
        cols = st.columns([2, 3, 4, 2, 1])
        for cw, val in zip(cols[:4], [exp["Date"], exp["Category"],
                                       exp["Description"], f'${exp["Amount"]:,.2f}']):
            cw.markdown(f'<div style="background:{bg};padding:4px 8px;border-radius:4px">{val}</div>',
                        unsafe_allow_html=True)
        if cols[4].button("✕", key=f"del_{i}"):
            st.session_state.expenses.pop(i)
            st.rerun()

else:
    st.subheader(t["expenses_header"])
    st.info(t["no_expenses"])
