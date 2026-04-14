"""
session.py — session state initialisation, serialisation, and loading.
"""
import json
import streamlit as st


def init_session_state():
    defaults = {
        "language":         "EN",
        "data_loaded":      False,
        "initial_budget":   None,
        "exchange_duration": None,
        "budget_currency":  "EUR",
        "display_currency": "EUR",
        "expenses":         [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


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
