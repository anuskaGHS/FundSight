# =============================================================
# FundSight — Overview
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

st.set_page_config(
    page_title="FundSight — Overview",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Helpers ───────────────────────────────────────────────────
def load_css():
    p = os.path.join(os.path.dirname(__file__), "style.css")
    with open(p, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

COLORS = {
    "violet": ["#1E1B4B","#3730A3","#6366F1","#818CF8","#A5B4FC","#C7D2FE"],
    "green":  ["#064E3B","#065F46","#059669","#10B981","#34D399","#6EE7B7"],
    "orange": ["#78350F","#92400E","#B45309","#D97706","#F59E0B","#FCD34D"],
    "multi":  ["#6366F1","#8B5CF6","#EC4899","#F59E0B","#10B981","#06B6D4",
               "#EF4444","#FB923C","#A3E635","#E879F9"],
}

def plotly_base(fig, height=300):
    fig.update_layout(
        plot_bgcolor="#13131A",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11,
                  color="rgba(232,232,240,0.6)"),
        margin=dict(t=40, b=8, l=8, r=8),
        height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, showline=False,
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, showline=False,
                   tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)",
                    font=dict(size=10)),
        hoverlabel=dict(
            bgcolor="#1E1B4B",
            bordercolor="#6366F1",
            font=dict(family="Inter", size=11, color="#E8E8F0")
        )
    )
    return fig

# ── Data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        load_dotenv()
        pw = quote_plus(os.getenv("DB_PASSWORD", ""))
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('DB_USER')}:{pw}"
            f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        )
        with engine.connect() as conn:
            return pd.read_sql("SELECT * FROM startup_funding", conn)
    except Exception:
        # Fallback to CSV for Streamlit Cloud deployment
        csv_path = os.path.join(
            os.path.dirname(__file__), "data",
            "cleaned_startup_funding.csv"
        )
        return pd.read_csv(csv_path)

load_css()
df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:8px 4px 4px 4px;'>
        <div style='font-size:1.1rem;font-weight:700;
            background:linear-gradient(90deg,#818CF8,#C084FC);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;letter-spacing:-0.02em;margin-bottom:2px;'>
            📈 FundSight
        </div>
        <div style='font-size:0.62rem;color:rgba(232,232,240,0.25);
            text-transform:uppercase;letter-spacing:0.1em;'>
            Indian Startup Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.6rem;text-transform:uppercase;"
                "letter-spacing:0.1em;opacity:0.4;margin:8px 0 6px 4px;"
                "font-weight:600;'>Filters</div>",
                unsafe_allow_html=True)

    year_range = st.slider("Year", 2010, 2025, (2010, 2025), key="yr")

    all_sectors = sorted(df[df["sector"] != "Unknown"]["sector"].unique())
    sectors = st.multiselect("Sector", all_sectors, default=all_sectors)

    all_cities = sorted(df["city"].dropna().unique())
    cities = st.multiselect("City", all_cities, default=all_cities)

    all_stages = sorted(df["funding_stage"].unique())
    stages = st.multiselect("Stage", all_stages, default=all_stages)

    st.markdown("""
    <div style='margin-top:16px;padding-top:12px;
                border-top:1px solid rgba(99,102,241,0.1);
                font-size:0.72rem;color:rgba(232,232,240,0.25);
                line-height:1.7;'>
        Built by <b style='color:rgba(232,232,240,0.4);'>Anuska Ghosh</b>
    </div>
    """, unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────
f = df[
    df["year"].between(year_range[0], year_range[1]) &
    df["sector"].isin(sectors if sectors else all_sectors) &
    df["city"].isin(cities   if cities   else all_cities)  &
    df["funding_stage"].isin(stages if stages else all_stages)
]

n           = len(f)
funding     = f["amount_usd"].sum() / 1e9
avg         = f["amount_usd"].mean() / 1e6
top_s       = f[f["sector"] != "Unknown"]["sector"].value_counts()
top_c       = f["city"].dropna().value_counts()
top_sec     = top_s.index[0]      if len(top_s) else "—"
top_sec_n   = int(top_s.iloc[0])  if len(top_s) else 0
top_city    = top_c.index[0]      if len(top_c) else "—"
yearly      = f.groupby("year").size().reset_index(name="deals")
peak_yr     = int(yearly.loc[yearly["deals"].idxmax(), "year"]) \
              if len(yearly) else 2016
peak_n      = int(yearly["deals"].max()) if len(yearly) else 0
post2020    = len(f[f["year"] >= 2020])
blr_del     = len(f[f["city"].isin(
                ["Bangalore","Delhi","Delhi NCR","Gurgaon"])])
blr_pct     = round(blr_del * 100 / n, 1) if n else 0

# ── Title ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 6px 0 14px 0;">
    <div style="font-size:3.2rem; font-weight:800; letter-spacing:-0.04em;
                background:linear-gradient(90deg,#818CF8,#C084FC,#818CF8);
                background-size:200% 100%;
                animation: shimmerText 4s linear infinite;
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                background-clip:text; margin-bottom:8px; line-height:1.1;">
        FundSight
    </div>
    <div style="font-size:0.78rem; color:rgba(232,232,240,0.35);
                letter-spacing:0.1em; text-transform:uppercase;
                font-weight:500;">
        Decoding India's Startup Funding Landscape &nbsp;·&nbsp; 2010 – 2025
    </div>
</div>
<style>
@keyframes shimmerText {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
</style>
""", unsafe_allow_html=True)

# ── Ticker ────────────────────────────────────────────────────
def ti(lbl, val, cls="val-v"):
    return (f'<span class="t-item">'
            f'<span class="lbl">{lbl}</span>'
            f'<span class="{cls}">{val}</span>'
            f'</span><span class="t-sep">·</span>')

rows = (
    ti("DEALS",       f"{n:,}",            "val-v") +
    ti("FUNDING",     f"${funding:.1f}B",  "val-g") +
    ti("TOP SECTOR",  top_sec,             "val-v") +
    ti("TOP CITY",    top_city,            "val-o") +
    ti("AVG DEAL",    f"${avg:.1f}M",      "val-g") +
    ti("PEAK YEAR",   str(peak_yr),        "val-o") +
    ti("POST-2020",   f"{post2020} deals", "val-g") +
    ti("BLR+DEL NCR", f"{blr_pct}%",      "val-v")
)

st.markdown(f"""
<div class="fs-ticker-outer">
    <div class="fs-ticker-badge">LIVE DATA</div>
    <div class="fs-ticker-scroll">
        <div class="fs-ticker-inner">{rows * 2}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────
st.markdown(f"""
<div class="pg-header">
    <div class="pg-title">Overview</div>
    <div class="pg-sub">
        {year_range[0]} – {year_range[1]} &nbsp;·&nbsp;
        {n:,} records &nbsp;·&nbsp;
        Indian startup funding analysis
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def kpi(col, label, value, sub, badge, badge_cls, color_cls):
    col.markdown(f"""
<div class="{color_cls}">
<div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {'text' if len(str(value)) > 6 else ''}">{value}</div>
    <div class="kpi-sub">{sub}</div>
    <span class="kpi-badge {badge_cls}">{badge}</span>
</div>
</div>""", unsafe_allow_html=True)

kpi(c1, "Total Deals",   f"{n:,}",          "all years",
    f"↑ {year_range[0]}–{year_range[1]}", "badge-v", "kpi-v")
kpi(c2, "Total Funding", f"${funding:.1f}B", "combined rounds",
    "all sectors", "badge-g", "kpi-g")
kpi(c3, "Avg Deal Size", f"${avg:.1f}M",     "per deal",
    "mean value", "badge-v", "kpi-v")
kpi(c4, "Top Sector",    top_sec,            f"{top_sec_n} deals",
    "most active", "badge-o", "kpi-o")
kpi(c5, "Peak Year",     str(peak_yr),       f"{peak_n} deals",
    "highest volume", "badge-g", "kpi-g")

st.markdown("<br>", unsafe_allow_html=True)

# ── Trend + Insights ──────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Funding activity over time</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

ca, cb = st.columns([3, 1])

with ca:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["deals"],
        mode="lines+markers",
        line=dict(color="#6366F1", width=2.5),
        marker=dict(size=6, color="#6366F1",
                    line=dict(color="#A5B4FC", width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        hovertemplate="<b>%{x}</b><br>Deals: <b>%{y}</b><extra></extra>"
    ))
    if len(yearly):
        px_yr = yearly.loc[yearly["deals"].idxmax()]
        fig.add_annotation(
            x=px_yr["year"], y=px_yr["deals"],
            text=f" Peak: {int(px_yr['deals'])}",
            showarrow=True, arrowhead=2,
            arrowcolor="#6366F1", arrowsize=1,
            font=dict(size=10, color="#A5B4FC"),
            bgcolor="rgba(30,27,75,0.8)",
            bordercolor="#6366F1", borderwidth=1,
            borderpad=4, ay=-35
        )
    fig = plotly_base(fig, 300)
    fig.update_xaxes(dtick=1, tickangle=-45)
    fig.update_layout(
        title=dict(
            text="Year-wise Deal Count"
                 "<br><sup style='color:rgba(232,232,240,0.35);'>"
                 "Number of funding deals per year · 2010–2025</sup>",
            font=dict(size=13, color="#E8E8F0"),
            x=0, xref="paper", pad=dict(b=10)
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with cb:
    st.markdown(f"""
<div class="insight-card v">
    <div class="insight-tag">Peak Year</div>
    <div class="insight-body">
        <b>{peak_yr}</b> saw the highest deal activity
        with <b>{peak_n:,} deals</b>, driven by the
        global VC funding wave.
    </div>
</div>
<div class="insight-card g">
    <div class="insight-tag">Post-2020 Growth</div>
    <div class="insight-body">
        <b>{post2020:,} deals</b> recorded post-2020.
        Fintech emerged as the dominant sector
        after the pandemic.
    </div>
</div>
<div class="insight-card o">
    <div class="insight-tag">City Concentration</div>
    <div class="insight-body">
        Bangalore + Delhi NCR together account for
        <b>{blr_pct}%</b> of all filtered deals.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Snapshot ──────────────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Quick snapshot</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

cc, cd = st.columns(2)

with cc:
    sec_df = (f[~f["sector"].isin(["Unknown", "Other"])]
              .groupby("sector").size()
              .reset_index(name="deals")
              .sort_values("deals", ascending=True).tail(8))
    fig2 = px.bar(sec_df, x="deals", y="sector",
                  orientation="h", color="deals",
                  color_continuous_scale=COLORS["violet"],
                  labels={"deals": "Deals", "sector": ""},
                  title="Top Sectors · By number of deals")
    fig2.update_traces(
        hovertemplate="<b>%{y}</b><br>Deals: <b>%{x}</b><extra></extra>"
    )
    fig2 = plotly_base(fig2, 310)
    fig2.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig2.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig2, use_container_width=True)

with cd:
    city_df = (f[f["city"] != "Other City"].dropna(subset=["city"])
               .groupby("city").size()
               .reset_index(name="deals")
               .sort_values("deals", ascending=True).tail(8))
    fig3 = px.bar(city_df, x="deals", y="city",
                  orientation="h", color="deals",
                  color_continuous_scale=COLORS["orange"],
                  labels={"deals": "Deals", "city": ""},
                  title="Top Cities · By deal volume")
    fig3.update_traces(
        hovertemplate="<b>%{y}</b><br>Deals: <b>%{x}</b><extra></extra>"
    )
    fig3 = plotly_base(fig3, 310)
    fig3.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig3.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig3, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="fs-footer">
    FundSight &nbsp;·&nbsp; Anuska Ghosh &nbsp;·&nbsp;
    Data Source: Kaggle
</div>
""", unsafe_allow_html=True)