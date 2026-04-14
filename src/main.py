"""
main.py — entry point for the Budget Calculator: Exchange Edition.

Run with:
    python -m streamlit run src/main.py
"""
import streamlit as st

from config import LANG
from session import init_session_state
from components.landing import render_landing
from components.setup import render_setup
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Budget Calculator | Calculateur Budget",
    page_icon="💶",
    layout="wide",
)

# Warn user before closing tab with unsaved data
st.markdown("""
<script>
    window.addEventListener('beforeunload', function(e) {
        e.preventDefault(); e.returnValue = '';
    });
</script>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
init_session_state()

# ── Language toggle ───────────────────────────────────────────────────────────
c1, c2, c3, _ = st.columns([1, 1, 1, 7])
with c1:
    if st.button("🇬🇧 EN", use_container_width=True,
                 type="primary" if st.session_state.language == "EN" else "secondary"):
        st.session_state.language = "EN"
        st.rerun()
with c2:
    if st.button("🇫🇷 FR", use_container_width=True,
                 type="primary" if st.session_state.language == "FR" else "secondary"):
        st.session_state.language = "FR"
        st.rerun()
with c3:
    if st.button("🇪🇸 ES", use_container_width=True,
                 type="primary" if st.session_state.language == "ES" else "secondary"):
        st.session_state.language = "ES"
        st.rerun()

t = LANG[st.session_state.language]
st.divider()

# ── Routing ───────────────────────────────────────────────────────────────────
if not st.session_state.data_loaded:
    render_landing(t)
    st.stop()

render_sidebar(t)

if st.session_state.initial_budget is None:
    render_setup(t)
    st.stop()

render_dashboard(t)
