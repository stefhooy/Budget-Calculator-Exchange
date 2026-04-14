"""
components/landing.py — landing page: hero banner, file upload, and fresh-start button.
"""
import streamlit as st
import pandas as pd

from utils import _image_b64
from file_parser import parse_uploaded_file
from session import load_from_dict


def render_landing(t: dict):
    # Hero banner
    b64 = _image_b64(t["hero_image"])
    if b64:
        bg = f"background-image: url('{b64}'); background-size: cover; background-position: center;"
        inner_bg = "background: rgba(0,0,0,0.52);"
    else:
        bg = "background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 70%, #533483 100%);"
        inner_bg = ""

    st.markdown(
        f"""
        <div style="{bg} border-radius:16px; overflow:hidden; margin-bottom:28px;
                    aspect-ratio:3/1; width:100%;">
            <div style="{inner_bg} height:100%; display:flex; flex-direction:column;
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
        uploaded = st.file_uploader(
            t["upload_label"], type=["json", "csv", "xlsx", "xls"],
            label_visibility="visible",
        )
        if uploaded is not None:
            result, err = parse_uploaded_file(uploaded)
            if err:
                st.error(f"{t['upload_error']} ({err})")
            else:
                load_from_dict(result)
                st.toast("Loaded!", icon="✅")
                st.rerun()

        st.markdown("")
        st.markdown(
            f"""
            <div style="background:#1a2f45; border-left:4px solid #3498db;
                 padding:12px 16px; border-radius:6px; margin-bottom:12px; color:#ffffff;">
                <span style="font-weight:700; color:#ffffff;">🎯 {t['try_it_title']}</span><br>
                {t['try_it_body']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"📋 {t['preview_title']}", expanded=False):
            st.caption(t["preview_caption_simple"])
            st.dataframe(pd.DataFrame([
                {"Amount": 12.50, "Currency": "EUR", "Description": "Lunch",          "Category": "Food",               "Date": "2024-02-14"},
                {"Amount": 8.00,  "Currency": "EUR", "Description": "Metro",           "Category": "Transport",          "Date": "2024-02-14"},
                {"Amount": 4500,  "Currency": "HUF", "Description": "Dinner Budapest", "Category": "Restaurant",         "Date": "2024-03-02"},
                {"Amount": 45.00, "Currency": "EUR", "Description": "Museum ticket",   "Category": "Activity & Museums", "Date": "2024-02-15"},
            ]), hide_index=True, use_container_width=True)

            st.markdown("---")
            st.caption(t["preview_caption_legacy"])
            st.dataframe(pd.DataFrame([
                {"Spending": "9,120.00 Ft", "Type of Expense": "Restaurant",          "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Hungary"},
                {"Spending": "€ 7.80",      "Type of Expense": "Restaurant",          "Month": "February", "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Slovakia"},
                {"Spending": "$594.00",     "Type of Expense": "Activity & Museums",  "Month": "April",    "Year": 2024, "in HUF": "", "in CAD": "", "in EURO": "", "Country": "Croatia"},
            ]), hide_index=True, use_container_width=True)

    with sep_col:
        st.markdown(
            "<div style='text-align:center; color:#aaa; padding-top:120px; font-size:1.3rem'>or</div>",
            unsafe_allow_html=True,
        )

    with fresh_col:
        st.markdown(f"### {t['fresh_btn']}")
        if st.button(t["fresh_btn"], type="primary", use_container_width=True):
            st.session_state.data_loaded = True
            st.rerun()
