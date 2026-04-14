"""
components/dashboard.py — main dashboard: header, status, metrics, charts, expense log.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import CURRENCIES, cat_color
from utils import _image_b64, convert_amount, fmt, to_display


def render_dashboard(t: dict):
    dc = st.session_state.display_currency
    bc = st.session_state.budget_currency

    # ── Dashboard header banner ───────────────────────────────────────────────
    b64 = _image_b64(t["dashboard_image"])
    if b64:
        dbg      = f"background-image: url('{b64}'); background-size: cover; background-position: center 40%;"
        inner_bg = "background: rgba(0,0,0,0.50);"
    else:
        dbg      = "background: linear-gradient(90deg, #0f3460 0%, #533483 100%);"
        inner_bg = ""

    st.markdown(
        f"""
        <div style="{dbg} border-radius:12px; overflow:hidden; margin-bottom:20px;">
            <div style="{inner_bg} padding:24px 32px; display:flex; align-items:center; gap:16px;">
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

    # ── Derived values ────────────────────────────────────────────────────────
    initial_bc  = st.session_state.initial_budget
    initial_dc  = convert_amount(initial_bc, bc, dc)
    duration    = st.session_state.exchange_duration
    total_spent = sum(to_display(e["Amount"], e.get("Currency", bc)) for e in st.session_state.expenses)
    remaining   = initial_dc - total_spent
    monthly     = initial_dc / duration
    weekly      = monthly / 4
    pct_used    = total_spent / initial_dc if initial_dc > 0 else 0

    # ── Status bar ────────────────────────────────────────────────────────────
    if pct_used >= 1.0:
        sc, sb, se, sm = "#e74c3c", "#fdecea", "🔴", t["status_over"]
    elif pct_used >= 0.9:
        sc, sb, se, sm = "#e74c3c", "#fdecea", "🔴", t["status_danger"]
    elif pct_used >= 0.7:
        sc, sb, se, sm = "#f39c12", "#fef9e7", "🟡", t["status_warning"]
    else:
        sc, sb, se, sm = "#27ae60", "#eafaf1", "🟢", t["status_good"]

    st.markdown(
        f"""<div style="background:{sb}; border-left:5px solid {sc}; padding:14px 18px;
             border-radius:6px; margin-bottom:16px;">
            <span style="font-size:1.1rem; color:{sc}; font-weight:600;">{se} {sm}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f"**{t['budget_used']}: {pct_used * 100:.1f}%**")
    st.markdown(
        f"""<div style="background:#e0e0e0; border-radius:8px; height:18px; overflow:hidden;">
            <div style="width:{min(pct_used, 1) * 100:.1f}%; background:{sc}; height:100%; border-radius:8px;"></div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # ── Metrics ───────────────────────────────────────────────────────────────
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

    if not st.session_state.expenses:
        st.subheader(t["expenses_header"])
        st.info(t["no_expenses"])
        return

    df = pd.DataFrame(st.session_state.expenses)
    df["Amount_display"] = df.apply(lambda r: to_display(r["Amount"], r.get("Currency", bc)), axis=1)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.subheader(t["charts_header"])
    _render_pie_and_country_bar(df, dc, t)
    _render_map(df, dc, t)
    _render_cumulative(df, dc, t, initial_dc)
    _render_monthly(df, dc, t, monthly)
    _render_country_drill(df, dc, t, initial_dc)

    st.divider()
    _render_currency_log(df, dc, t)
    st.divider()
    _render_expense_log(df, dc, t, bc, initial_dc)


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _render_pie_and_country_bar(df, dc, t):
    col_pie, col_bar = st.columns(2)

    with col_pie:
        cat_totals = (df.groupby("Category")["Amount_display"].sum()
                        .reset_index()
                        .sort_values("Amount_display", ascending=False))
        colors = [cat_color(n, i) for i, n in enumerate(cat_totals["Category"])]
        fig = px.pie(cat_totals, values="Amount_display", names="Category",
                     title=t["pie_title"], color_discrete_sequence=colors, hole=0.4)
        fig.update_traces(
            textinfo="label+percent", textfont_size=12,
            hovertemplate=f"%{{label}}<br>{CURRENCIES[dc]['symbol']}%{{value:,.2f}} (%{{percent}})<extra></extra>",
            pull=[0.03] * len(cat_totals),
        )
        fig.update_layout(showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5),
                          margin=dict(t=50, b=20, r=120))
        st.plotly_chart(fig, use_container_width=True)

    with col_bar:
        ct = (df.groupby("Description")["Amount_display"].sum()
                .reset_index()
                .rename(columns={"Description": "Country", "Amount_display": "Total"})
                .sort_values("Total", ascending=True))
        fig = go.Figure(go.Bar(
            y=ct["Country"], x=ct["Total"], orientation="h",
            marker=dict(color=ct["Total"], colorscale="RdYlGn_r", showscale=False),
            text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in ct["Total"]],
            textposition="outside",
            hovertemplate=f"<b>%{{y}}</b><br>{CURRENCIES[dc]['symbol']}%{{x:,.2f}}<extra></extra>",
        ))
        fig.update_layout(
            title=t["bar_country_title"], xaxis_title=dc,
            margin=dict(t=50, b=20, l=10, r=80),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=max(300, len(ct) * 38),
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_map(df, dc, t):
    cm = (df.groupby("Description")["Amount_display"].sum()
            .reset_index()
            .rename(columns={"Description": "Country", "Amount_display": "Total"}))
    fig = px.choropleth(
        cm, locations="Country", locationmode="country names",
        color="Total", color_continuous_scale="RdYlGn_r",
        title=t["map_title"], hover_name="Country",
        hover_data={"Total": ":.2f", "Country": False}, labels={"Total": dc},
    )
    fig.update_traces(
        hovertemplate=f"<b>%{{hovertext}}</b><br>{CURRENCIES[dc]['symbol']}%{{z:,.2f}}<extra></extra>"
    )
    fig.update_geos(
        projection_type="natural earth", bgcolor="rgba(0,0,0,0)",
        showframe=False, showcoastlines=True, coastlinecolor="rgba(255,255,255,0.25)",
        showland=True, landcolor="#1e2a3a", showocean=True, oceancolor="#0d1821",
        showcountries=True, countrycolor="rgba(255,255,255,0.18)",
        showlakes=False, fitbounds=False, visible=True,
        lataxis_range=[-60, 85], lonaxis_range=[-180, 180],
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title=dc, tickprefix=CURRENCIES[dc]["symbol"],
                                bgcolor="rgba(0,0,0,0.4)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=0, l=0, r=0), height=500,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_cumulative(df, dc, t, initial_dc):
    dfl = df.copy()
    dfl["Cumulative"] = dfl["Amount_display"].cumsum()
    dfl.index = range(1, len(dfl) + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(dfl.index), y=dfl["Cumulative"],
        mode="lines+markers", line=dict(color="#3498db", width=3),
        hovertemplate=f"Entry %{{x}}: {CURRENCIES[dc]['symbol']}%{{y:,.2f}}<extra></extra>",
    ))
    fig.add_hline(y=initial_dc, line_dash="dash", line_color="#e74c3c",
                  annotation_text=t["initial"], annotation_position="top right")
    fig.add_hline(y=initial_dc * 0.7, line_dash="dot", line_color="#f39c12",
                  annotation_text="70%", annotation_position="top right")
    fig.update_layout(title=t["cumulative_title"], xaxis_title=t["cumulative_x"],
                      yaxis_title=dc, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def _render_monthly(df, dc, t, monthly):
    dfm = df.copy()
    dfm["YearMonth"] = pd.to_datetime(dfm["Date"], errors="coerce").dt.to_period("M").astype(str)
    mt = dfm.groupby("YearMonth")["Amount_display"].sum().reset_index().sort_values("YearMonth")
    mt["color"] = mt["Amount_display"].apply(lambda v: "#e74c3c" if v > monthly else "#27ae60")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mt["YearMonth"], y=mt["Amount_display"],
        marker_color=mt["color"].tolist(),
        text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in mt["Amount_display"]],
        textposition="outside",
        hovertemplate=f"<b>%{{x}}</b><br>Spent: {CURRENCIES[dc]['symbol']}%{{y:,.2f}}<extra></extra>",
    ))
    fig.add_hline(y=monthly, line_dash="dash", line_color="#f39c12", line_width=2,
                  annotation_text=f"{t['monthly_budget_line']}: {fmt(monthly)}",
                  annotation_position="top left", annotation_font_color="#f39c12")
    fig.update_layout(
        title=t["monthly_chart_title"],
        xaxis=dict(title=t["monthly_x"], type="category"),
        yaxis_title=dc, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_country_drill(df, dc, t, initial_dc):
    st.divider()
    st.subheader(f"🔍 {t['country_drill_header']}")
    countries = sorted(df["Description"].dropna().unique().tolist())
    selected = st.selectbox(t["select_country"], [t["all_label"]] + countries, key="country_drill_select")

    if selected == t["all_label"]:
        return

    dfc = df[df["Description"] == selected].copy()
    total_c = dfc["Amount_display"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric(t["drill_total"], fmt(total_c))
    c2.metric("% of budget", f"{total_c / initial_dc * 100:.1f}%")
    c3.metric("Transactions", len(dfc))

    pie_col, bar_col = st.columns(2)

    with pie_col:
        cat_c = dfc.groupby("Category")["Amount_display"].sum().reset_index().sort_values("Amount_display", ascending=False)
        colors = [cat_color(n, i) for i, n in enumerate(cat_c["Category"])]
        fig = px.pie(cat_c, values="Amount_display", names="Category",
                     title=f"{t['drill_pie_title']} {selected}",
                     color_discrete_sequence=colors, hole=0.4)
        fig.update_traces(
            textinfo="label+percent", textfont_size=12,
            hovertemplate=f"%{{label}}<br>{CURRENCIES[dc]['symbol']}%{{value:,.2f}} (%{{percent}})<extra></extra>",
            pull=[0.03] * len(cat_c),
        )
        fig.update_layout(margin=dict(t=50, b=20, r=120),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with bar_col:
        dfc["YearMonth"] = pd.to_datetime(dfc["Date"], errors="coerce").dt.to_period("M").astype(str)
        tl = dfc.groupby("YearMonth")["Amount_display"].sum().reset_index().sort_values("YearMonth")
        fig = go.Figure(go.Bar(
            x=tl["YearMonth"], y=tl["Amount_display"], marker_color="#3498db",
            text=[f"{CURRENCIES[dc]['symbol']}{v:,.0f}" for v in tl["Amount_display"]],
            textposition="outside",
            hovertemplate=f"<b>%{{x}}</b><br>{CURRENCIES[dc]['symbol']}%{{y:,.2f}}<extra></extra>",
        ))
        fig.update_layout(
            title=f"{t['drill_timeline_title']} {selected}",
            xaxis=dict(title=t["monthly_x"], type="category"),
            yaxis_title=dc, plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_currency_log(df, dc, t):
    st.subheader(t["currency_log_header"])
    st.caption(t["currency_log_caption"])
    rows = []
    for cur_code, grp in df.groupby("Currency"):
        sym = CURRENCIES.get(cur_code, {}).get("symbol", "")
        name = CURRENCIES.get(cur_code, {}).get("name", cur_code)
        rows.append({
            t["col_currency"]:       f"{cur_code}  {sym}  ({name})",
            t["col_transactions"]:   len(grp),
            t["col_total_original"]: f"{sym}{grp['Amount'].sum():,.2f}",
            t["col_total_converted"]: fmt(grp["Amount_display"].sum()),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def _render_expense_log(df, dc, t, bc, initial_dc):
    st.subheader(t["expenses_header"])
    for cw, label in zip(
        st.columns([2, 2, 3, 3, 2, 2, 1]),
        ["Date", "Category", "Description", t["col_currency"], "Original", f"In {dc}", ""],
    ):
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
        sym      = CURRENCIES.get(cur_code, {}).get("symbol", "")
        orig_fmt = f"{sym}{exp['Amount']:,.2f}"
        cols = st.columns([2, 2, 3, 3, 2, 2, 1])
        for cw, val in zip(cols[:6], [
            exp["Date"], exp["Category"], exp["Description"],
            f"{cur_code} {sym}", orig_fmt, fmt(exp_dc_amount),
        ]):
            cw.markdown(
                f'<div style="background:{bg}; color:{txt}; padding:4px 8px; '
                f'border-radius:4px; font-size:0.9rem">{val}</div>',
                unsafe_allow_html=True,
            )
        if cols[6].button("✕", key=f"del_{i}"):
            st.session_state.expenses.pop(i)
            st.rerun()
