"""
components/sidebar.py — sidebar panel: currency pickers, budget input, add expense, download.
"""
import streamlit as st
import pandas as pd
from datetime import date

from config import CURRENCIES, CURRENCY_CODES
from session import session_to_json


def render_sidebar(t: dict):
    with st.sidebar:
        st.header(t["setup_header"])

        # Currency pickers
        cur_col1, cur_col2 = st.columns(2)
        with cur_col1:
            bc_idx = CURRENCY_CODES.index(st.session_state.budget_currency)
            new_bc = st.selectbox(
                t["budget_currency"], CURRENCY_CODES, index=bc_idx,
                format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}",
            )
            if new_bc != st.session_state.budget_currency:
                st.session_state.budget_currency = new_bc
                st.rerun()
        with cur_col2:
            dc_idx = CURRENCY_CODES.index(st.session_state.display_currency)
            new_dc = st.selectbox(
                t["display_currency"], CURRENCY_CODES, index=dc_idx,
                format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}",
            )
            if new_dc != st.session_state.display_currency:
                st.session_state.display_currency = new_dc
                st.rerun()

        st.caption(f"ℹ️ {t['rates_note']}")

        # Budget amount
        bc_sym = CURRENCIES[st.session_state.budget_currency]["symbol"]
        budget_in_bc = st.number_input(
            f"{t['total_budget']} ({bc_sym})",
            min_value=0.0,
            value=float(st.session_state.initial_budget or 3000.0),
            step=100.0,
        )
        duration_input = st.number_input(
            t["duration"], min_value=1, max_value=24,
            value=int(st.session_state.exchange_duration or 5), step=1,
        )
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
                    format_func=lambda c: f"{c} {CURRENCIES[c]['symbol']}",
                )
                exp_sym = CURRENCIES[exp_cur]["symbol"]
                exp_amount = st.number_input(
                    f"{t['amount']} ({exp_sym})", min_value=0.01, value=10.0, step=0.5,
                )
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
                    "expenses": [], "data_loaded": False,
                })
                st.rerun()

        st.divider()

        # Download panel
        st.markdown(
            f"""<div style="background:#fff3cd; border:1px solid #ffc107; border-radius:8px;
                 padding:10px 14px; margin-bottom:8px;">
                <span style="font-size:1rem; font-weight:700;">💾 {t['download_header']}</span><br>
                <span style="font-size:0.82rem; color:#7a5c00;">{t['download_caption']}</span>
            </div>""",
            unsafe_allow_html=True,
        )
        st.download_button(
            t["save_btn"], data=session_to_json(),
            file_name="budget.json", mime="application/json",
            use_container_width=True, type="primary",
        )
        if st.session_state.expenses:
            csv_bytes = pd.DataFrame(st.session_state.expenses).to_csv(index=False).encode("utf-8")
            st.download_button(
                t["export_csv"], data=csv_bytes,
                file_name="budget_export.csv", mime="text/csv",
                use_container_width=True,
            )
