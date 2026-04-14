import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Budget Calculator | Calculateur Budget",
    page_icon="💶",
    layout="wide",
)

# ── Language strings ──────────────────────────────────────────────────────────
LANG = {
    "EN": {
        "title": "Budget Calculator — Exchange Edition",
        "subtitle": "Track your spending abroad, stay in control.",
        "setup_header": "Budget Setup",
        "initial_budget": "Initial Budget ($)",
        "duration": "Exchange Duration (months)",
        "init_btn": "Initialize Budget",
        "add_header": "Add Expense",
        "amount": "Amount ($)",
        "description": "Description",
        "category": "Category",
        "add_btn": "Add Expense",
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
        "status_good": "You're doing great! Keep it up.",
        "status_warning": "Careful — you're using up your budget.",
        "status_danger": "Alert! You're almost out of budget.",
        "status_over": "You have exceeded your budget!",
        "budget_used": "Budget used",
        "clear_btn": "Clear All Expenses",
        "save_btn": "Export to CSV",
        "categories": ["Food", "Transport", "Housing", "Entertainment", "Health", "Shopping", "Other"],
    },
    "FR": {
        "title": "Calculateur de Budget — Échange",
        "subtitle": "Suivez vos dépenses à l'étranger, gardez le contrôle.",
        "setup_header": "Configuration du Budget",
        "initial_budget": "Budget Initial ($)",
        "duration": "Durée de l'échange (mois)",
        "init_btn": "Initialiser le Budget",
        "add_header": "Ajouter une Dépense",
        "amount": "Montant ($)",
        "description": "Description",
        "category": "Catégorie",
        "add_btn": "Ajouter la Dépense",
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
        "status_good": "Vous gérez très bien votre budget !",
        "status_warning": "Attention — vous consommez votre budget.",
        "status_danger": "Alerte ! Vous êtes presque à court de budget.",
        "status_over": "Vous avez dépassé votre budget !",
        "budget_used": "Budget utilisé",
        "clear_btn": "Effacer Toutes les Dépenses",
        "save_btn": "Exporter en CSV",
        "categories": ["Nourriture", "Transport", "Logement", "Loisirs", "Santé", "Shopping", "Autre"],
    },
}

# ── Session state defaults ────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state.language = "EN"
if "initial_budget" not in st.session_state:
    st.session_state.initial_budget = None
if "exchange_duration" not in st.session_state:
    st.session_state.exchange_duration = None
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ── Language toggle ───────────────────────────────────────────────────────────
col_lang1, col_lang2, col_spacer = st.columns([1, 1, 8])
with col_lang1:
    if st.button("🇬🇧 English", use_container_width=True,
                 type="primary" if st.session_state.language == "EN" else "secondary"):
        st.session_state.language = "EN"
        st.rerun()
with col_lang2:
    if st.button("🇫🇷 Français", use_container_width=True,
                 type="primary" if st.session_state.language == "FR" else "secondary"):
        st.session_state.language = "FR"
        st.rerun()

t = LANG[st.session_state.language]

st.divider()

# ── Title ─────────────────────────────────────────────────────────────────────
st.title(f"💶 {t['title']}")
st.caption(t["subtitle"])
st.divider()

# ── Sidebar: Budget Setup ─────────────────────────────────────────────────────
with st.sidebar:
    st.header(t["setup_header"])
    initial_budget_input = st.number_input(t["initial_budget"], min_value=0.0, value=3000.0, step=100.0)
    duration_input = st.number_input(t["duration"], min_value=1, max_value=24, value=5, step=1)

    if st.button(t["init_btn"], use_container_width=True, type="primary"):
        st.session_state.initial_budget = initial_budget_input
        st.session_state.exchange_duration = duration_input
        st.session_state.expenses = []
        st.success("✓")

    st.divider()

    # Add expense form
    if st.session_state.initial_budget is not None:
        st.header(t["add_header"])
        with st.form("add_expense_form", clear_on_submit=True):
            exp_amount = st.number_input(t["amount"], min_value=0.01, value=10.0, step=0.5)
            exp_desc = st.text_input(t["description"])
            exp_cat = st.selectbox(t["category"], t["categories"])
            exp_date = st.date_input("Date", value=date.today())
            submitted = st.form_submit_button(t["add_btn"], use_container_width=True)
            if submitted and exp_desc.strip():
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

# ── Main content ──────────────────────────────────────────────────────────────
if st.session_state.initial_budget is None:
    st.info("👈 " + t["setup_header"] + " →")
    st.stop()

initial = st.session_state.initial_budget
duration = st.session_state.exchange_duration
total_spent = sum(e["Amount"] for e in st.session_state.expenses)
remaining = initial - total_spent
monthly = initial / duration
weekly = monthly / 4
pct_used = total_spent / initial if initial > 0 else 0

# ── Color status ──────────────────────────────────────────────────────────────
if pct_used >= 1.0:
    status_color = "#e74c3c"
    status_bg = "#fdecea"
    status_emoji = "🔴"
    status_msg = t["status_over"]
elif pct_used >= 0.9:
    status_color = "#e74c3c"
    status_bg = "#fdecea"
    status_emoji = "🔴"
    status_msg = t["status_danger"]
elif pct_used >= 0.7:
    status_color = "#f39c12"
    status_bg = "#fef9e7"
    status_emoji = "🟡"
    status_msg = t["status_warning"]
else:
    status_color = "#27ae60"
    status_bg = "#eafaf1"
    status_emoji = "🟢"
    status_msg = t["status_good"]

# ── Status banner ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="background:{status_bg}; border-left: 5px solid {status_color};
         padding: 14px 18px; border-radius: 6px; margin-bottom: 16px;">
        <span style="font-size:1.1rem; color:{status_color}; font-weight:600;">
            {status_emoji} {status_msg}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Progress bar ──────────────────────────────────────────────────────────────
st.markdown(f"**{t['budget_used']}: {pct_used*100:.1f}%**")
progress_val = min(pct_used, 1.0)
bar_color = status_color

st.markdown(
    f"""
    <div style="background:#e0e0e0; border-radius:8px; height:18px; overflow:hidden;">
        <div style="width:{progress_val*100:.1f}%; background:{bar_color};
             height:100%; border-radius:8px; transition: width 0.4s;"></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("")

# ── Overview metrics ──────────────────────────────────────────────────────────
st.subheader(t["overview_header"])
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(t["initial"], f"${initial:,.2f}")
c2.metric(t["spent"], f"${total_spent:,.2f}")
c3.metric(t["remaining"], f"${remaining:,.2f}", delta=f"{remaining - initial:,.2f}" if total_spent > 0 else None,
          delta_color="inverse")
c4.metric(t["monthly"], f"${monthly:,.2f}")
c5.metric(t["weekly"], f"${weekly:,.2f}")

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    st.subheader(t["charts_header"])
    chart_col1, chart_col2 = st.columns(2)

    # Pie chart by category
    with chart_col1:
        cat_totals = df.groupby("Category")["Amount"].sum().reset_index()
        # Assign colors per row based on % of budget
        cat_totals["pct"] = cat_totals["Amount"] / initial
        cat_totals["color"] = cat_totals["pct"].apply(
            lambda p: "#e74c3c" if p >= 0.3 else ("#f39c12" if p >= 0.15 else "#27ae60")
        )
        fig_pie = px.pie(
            cat_totals,
            values="Amount",
            names="Category",
            title=t["pie_title"],
            color_discrete_sequence=cat_totals["color"].tolist(),
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="label+percent", hovertemplate="%{label}: $%{value:,.2f}")
        fig_pie.update_layout(showlegend=True, margin=dict(t=50, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar chart per entry with color coding
    with chart_col2:
        df_plot = df.copy()
        df_plot["pct_of_budget"] = df_plot["Amount"] / initial
        df_plot["bar_color"] = df_plot["pct_of_budget"].apply(
            lambda p: "#e74c3c" if p >= 0.1 else ("#f39c12" if p >= 0.05 else "#27ae60")
        )
        fig_bar = go.Figure(go.Bar(
            x=df_plot["Description"],
            y=df_plot["Amount"],
            marker_color=df_plot["bar_color"].tolist(),
            hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",
        ))
        fig_bar.update_layout(
            title=t["bar_title"],
            xaxis_tickangle=-30,
            yaxis_title="$",
            margin=dict(t=50, b=60),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Cumulative spending line chart
    df["Cumulative"] = df["Amount"].cumsum()
    df.index = range(1, len(df) + 1)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=list(df.index),
        y=df["Cumulative"],
        mode="lines+markers",
        line=dict(color="#3498db", width=3),
        name="Cumulative Spending",
        hovertemplate="Entry %{x}: $%{y:,.2f}<extra></extra>",
    ))
    fig_line.add_hline(y=initial, line_dash="dash", line_color="#e74c3c",
                       annotation_text=t["initial"], annotation_position="top right")
    fig_line.add_hline(y=initial * 0.7, line_dash="dot", line_color="#f39c12",
                       annotation_text="70%", annotation_position="top right")
    fig_line.update_layout(
        title="Cumulative Spending" if st.session_state.language == "EN" else "Dépenses Cumulées",
        xaxis_title="# Entries" if st.session_state.language == "EN" else "Entrées",
        yaxis_title="$",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ── Expense table ─────────────────────────────────────────────────────────
    st.subheader(t["expenses_header"])

    def row_color(amount):
        pct = amount / initial
        if pct >= 0.1:
            return "background-color: #fdecea"
        elif pct >= 0.05:
            return "background-color: #fef9e7"
        return "background-color: #eafaf1"

    display_df = df[["Date", "Category", "Description", "Amount"]].copy()
    display_df["Amount"] = display_df["Amount"].apply(lambda x: f"${x:,.2f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Export button
    csv = pd.DataFrame(st.session_state.expenses).to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t["save_btn"],
        data=csv,
        file_name="budget_export.csv",
        mime="text/csv",
    )

else:
    st.subheader(t["expenses_header"])
    st.info(t["no_expenses"])
