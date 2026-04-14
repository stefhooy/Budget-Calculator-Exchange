"""
components/setup.py — budget setup page shown after file load, before the dashboard.
"""
import streamlit as st

from config import CURRENCIES, CURRENCY_CODES


def render_setup(t: dict):
    n_exp = len(st.session_state.expenses)
    if n_exp > 0:
        st.success(f"✅ **{n_exp}** {t['setup_loaded_msg']}")

    _, card_col, _ = st.columns([1, 3, 1])
    with card_col:
        st.markdown(
            f"""<div style="background:rgba(255,255,255,0.05);
                 border:1px solid rgba(255,255,255,0.12);
                 border-radius:16px; padding:36px 40px; margin-top:12px;">
                <h2 style="margin-top:0;">{t['setup_header']}</h2>
            </div>""",
            unsafe_allow_html=True,
        )
        setup_bc = st.selectbox(
            t["budget_currency"], CURRENCY_CODES,
            format_func=lambda c: f"{c}  {CURRENCIES[c]['symbol']}  ({CURRENCIES[c]['name']})",
            key="setup_bc",
        )
        bc_sym = CURRENCIES[setup_bc]["symbol"]
        setup_amount = st.number_input(
            f"{t['total_budget']} ({bc_sym})",
            min_value=0.0, value=3000.0, step=100.0, key="setup_amount",
        )
        setup_dur = st.number_input(
            t["duration"], min_value=1, max_value=24, value=5, step=1,
            key="setup_dur",
        )
        st.caption(f"ℹ️ {t['rates_note']}")

        if st.button(t["setup_go_btn"], type="primary", use_container_width=True):
            st.session_state.initial_budget    = setup_amount
            st.session_state.budget_currency   = setup_bc
            st.session_state.display_currency  = setup_bc
            st.session_state.exchange_duration = setup_dur
            st.rerun()
