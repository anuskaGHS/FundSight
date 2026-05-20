# =============================================================
# FundSight — Funding Stages
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

st.set_page_config(page_title="FundSight — Funding Stages",
                   page_icon="💰", layout="wide",
                   initial_sidebar_state="expanded")

def load_css():
    p = os.path.join(os.path.dirname(__file__), "..", "style.css")
    with open(p, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def plotly_base(fig, height=320):
    fig.update_layout(
        plot_bgcolor="#13131A", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11,
                  color="rgba(232,232,240,0.6)"),
        margin=dict(t=40, b=8, l=8, r=8), height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, showline=False,
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)",
                   zeroline=False, showline=False,
                   tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)",
                    font=dict(size=10)),
        hoverlabel=dict(bgcolor="#1E1B4B", bordercolor="#6366F1",
                        font=dict(family="Inter", size=11,
                                  color="#E8E8F0"))
    )
    return fig

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
            os.path.dirname(__file__), "..", "data",
            "cleaned_startup_funding.csv"
        )
        return pd.read_csv(csv_path)

load_css()
df = load_data()

COLORS_M = ["#6366F1","#8B5CF6","#EC4899","#F59E0B","#10B981",
            "#06B6D4","#EF4444","#FB923C","#A3E635","#E879F9"]
COLORS_G = ["#064E3B","#065F46","#059669","#10B981","#34D399"]

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
    year_range = st.slider("Year", 2010, 2025, (2010, 2025))
    all_sectors = sorted(df[df["sector"] != "Unknown"]["sector"].unique())
    sectors = st.multiselect("Sector", all_sectors, default=all_sectors)
    all_cities = sorted(df["city"].dropna().unique())
    cities = st.multiselect("City", all_cities, default=all_cities)
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
    df["city"].isin(cities   if cities   else all_cities)
]

# ── Page header ───────────────────────────────────────────────
st.markdown("""
<div style='padding:6px 0 20px 0;'>
    <div class='pg-title'>Funding Stages</div>
    <div class='pg-sub'>
        Distribution and trends across funding rounds
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
stage_vc    = f["funding_stage"].value_counts()
top_stage   = stage_vc.index[0]     if len(stage_vc) else "—"
top_stage_n = int(stage_vc.iloc[0]) if len(stage_vc) else 0
seed_n      = int(f[f["funding_stage"] == "Seed"].shape[0])
pe_n        = int(f[f["funding_stage"] == "Private Equity"].shape[0])
series_n    = int(f[f["funding_stage"].str.contains(
                  "Series", na=False)].shape[0])

k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub, cls):
    col.markdown(f"""
<div class="{cls}"><div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {'text' if len(str(value)) > 7 else ''}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div></div>""", unsafe_allow_html=True)

kpi(k1, "Top Stage",      top_stage,      f"{top_stage_n} deals", "kpi-v")
kpi(k2, "Seed Deals",     f"{seed_n:,}",  "early stage",          "kpi-g")
kpi(k3, "Private Equity", f"{pe_n:,}",    "growth stage",         "kpi-o")
kpi(k4, "Series Rounds",  f"{series_n:,}","A through E+",         "kpi-c")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Donut + Bar ────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Stage distribution</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r1a, r1b = st.columns([2, 3])

with r1a:
    stage_df = (f[~f["funding_stage"].isin(["Unknown","Other"])]
                ["funding_stage"].value_counts().reset_index())
    stage_df.columns = ["stage", "count"]

    fig = px.pie(stage_df, names="stage", values="count",
                 hole=0.55, color_discrete_sequence=COLORS_M,
                 title="Stage Breakdown · % share of all deals")
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Deals: %{value}<br>"
                      "Share: %{percent}<extra></extra>",
        pull=[0.03] * len(stage_df)
    )
    fig = plotly_base(fig, 360)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02,
            font=dict(size=10)
        ),
        margin=dict(t=40, b=20, l=20, r=120),
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    st.plotly_chart(fig, use_container_width=True)

with r1b:
    stage_bar = stage_df[~stage_df["stage"].isin(["Unknown","Other"])].sort_values("count", ascending=True)
    fig2 = px.bar(stage_bar, x="count", y="stage",
                  orientation="h", color="count",
                  color_continuous_scale=COLORS_M,
                  labels={"count": "Deals", "stage": ""},
                  title="Deals by Stage · Absolute deal counts per stage")
    fig2.update_traces(
        hovertemplate="<b>%{y}</b><br>Deals: <b>%{x}</b><extra></extra>"
    )
    fig2 = plotly_base(fig2, 360)
    fig2.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig2.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig2, use_container_width=True)

# ── Stage trend over years ────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Stage trends over time</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

top_stages = (f[~f["funding_stage"].isin(["Unknown","Other"])]["funding_stage"]
              .value_counts().head(6).index.tolist())
stage_yr   = (f[f["funding_stage"].isin(top_stages)]
              .groupby(["year","funding_stage"]).size()
              .reset_index(name="deals"))

fig3 = px.line(stage_yr, x="year", y="deals",
               color="funding_stage", markers=True,
               color_discrete_sequence=COLORS_M,
               labels={"year": "Year", "deals": "Deals",
                       "funding_stage": "Stage"},
               title="Funding Stage Trends by Year · Top 6 stages · Peak period 2015–2020")
fig3.update_traces(
    line_width=2, marker_size=5,
    hovertemplate="<b>%{fullData.name}</b><br>"
                  "Year: %{x}<br>"
                  "Deals: <b>%{y}</b><extra></extra>"
)
fig3 = plotly_base(fig3, 320)
fig3.update_layout(
    title=dict(font=dict(size=13, color="#E8E8F0"),
               x=0, xref="paper"),
    legend=dict(
        orientation="v",
        yanchor="top", y=1,
        xanchor="right", x=1,
        font=dict(size=9),
        bgcolor="rgba(19,19,26,0.8)",
        bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1
    )
)
fig3.update_xaxes(dtick=1, tickangle=-45,
                  range=[year_range[0]-0.5, year_range[1]+0.5])
st.plotly_chart(fig3, use_container_width=True)

# ── Funding amounts by stage ──────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Funding amounts by stage</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r3a, r3b = st.columns(2)

with r3a:
    avg_df = (f[~f["funding_stage"].isin(["Unknown","Other"])].groupby("funding_stage")["amount_usd"]
               .mean().reset_index()
               .rename(columns={"amount_usd": "avg_usd"})
               .sort_values("avg_usd", ascending=True))
    avg_df["avg_m"] = avg_df["avg_usd"] / 1e6
    fig4 = px.bar(avg_df, x="avg_m", y="funding_stage",
                  orientation="h", color="avg_m",
                  color_continuous_scale=COLORS_G,
                  labels={"avg_m": "Avg Deal ($M)", "funding_stage": ""},
                  title="Avg Deal Size by Stage · In USD millions")
    fig4.update_traces(
        hovertemplate="<b>%{y}</b><br>"
                      "Avg: $<b>%{x:.1f}M</b><extra></extra>"
    )
    fig4 = plotly_base(fig4, 320)
    fig4.update_layout(
        margin=dict(t=40, b=8, l=8, r=40),
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig4.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig4, use_container_width=True)

with r3b:
    total_df = (f[~f["funding_stage"].isin(["Unknown","Other"])].groupby("funding_stage")["amount_usd"]
                 .sum().reset_index()
                 .rename(columns={"amount_usd": "total"})
                 .sort_values("total", ascending=True))
    total_df["total_bn"] = total_df["total"] / 1e9
    fig5 = px.bar(total_df, x="total_bn", y="funding_stage",
                  orientation="h", color="total_bn",
                  color_continuous_scale=["#1E1B4B","#6366F1","#A5B4FC"],
                  labels={"total_bn": "Total ($B)", "funding_stage": ""},
                  title="Total Funding by Stage · In USD billions")
    fig5.update_traces(
        hovertemplate="<b>%{y}</b><br>"
                      "Total: $<b>%{x:.2f}B</b><extra></extra>"
    )
    fig5 = plotly_base(fig5, 320)
    fig5.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig5.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.markdown('<div class="fs-footer">FundSight &nbsp;·&nbsp; '
            'Anuska Ghosh &nbsp;·&nbsp; Data Source: Kaggle</div>',
            unsafe_allow_html=True)