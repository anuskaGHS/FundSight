# =============================================================
# FundSight — Sector Analysis
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

st.set_page_config(page_title="FundSight — Sector Analysis",
                   page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

def load_css():
    p = os.path.join(os.path.dirname(__file__), "..", "style.css")
    with open(p, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def plotly_base(fig, height=320):
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
        hoverlabel=dict(bgcolor="#1E1B4B", bordercolor="#6366F1",
                        font=dict(family="Inter", size=11,
                                  color="#E8E8F0"))
    )
    return fig

@st.cache_data
def load_data():
    load_dotenv()
    pw = quote_plus(os.getenv("DB_PASSWORD"))
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{pw}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM startup_funding", conn)

load_css()
df = load_data()

COLORS_V = ["#1E1B4B","#3730A3","#6366F1","#818CF8","#A5B4FC","#C7D2FE"]
COLORS_G = ["#064E3B","#065F46","#059669","#10B981","#34D399","#6EE7B7"]
COLORS_M = ["#6366F1","#8B5CF6","#EC4899","#F59E0B","#10B981",
            "#06B6D4","#EF4444","#FB923C","#A3E635","#E879F9"]

EXCLUDE = ["Unknown", "Other"]

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
    all_cities = sorted(df["city"].dropna().unique())
    cities = st.multiselect("City", all_cities, default=all_cities)
    all_stages = sorted(df["funding_stage"].unique())
    stages = st.multiselect("Stage", all_stages, default=all_stages)

# ── Filter ────────────────────────────────────────────────────
f = df[
    df["year"].between(year_range[0], year_range[1]) &
    df["city"].isin(cities if cities else all_cities) &
    df["funding_stage"].isin(stages if stages else all_stages)
]
fc = f[~f["sector"].isin(EXCLUDE)]

# ── Page header ───────────────────────────────────────────────
st.markdown("""
<div style='padding:6px 0 20px 0;'>
    <div class='pg-title'>Sector Analysis</div>
    <div class='pg-sub'>
        Breakdown of funding deals and amounts across sectors
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
top_s     = fc["sector"].value_counts()
top_sec   = top_s.index[0]     if len(top_s) else "—"
top_n     = int(top_s.iloc[0]) if len(top_s) else 0
sectors   = fc["sector"].nunique()
post_top  = fc[fc["year"] >= 2020]["sector"].value_counts()
post_sec  = post_top.index[0] if len(post_top) else "—"
fintech_n = int(fc[fc["sector"] == "Fintech"].shape[0])

k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub, cls):
    col.markdown(f"""
<div class="{cls}"><div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {'text' if len(str(value)) > 7 else ''}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div></div>""", unsafe_allow_html=True)

kpi(k1, "Total Sectors",    str(sectors),   "unique sectors",  "kpi-v")
kpi(k2, "Top by Deals",     top_sec,        f"{top_n} deals",  "kpi-g")
kpi(k3, "Post-2020 Leader", post_sec,       "dominant sector", "kpi-o")
kpi(k4, "Fintech Deals",    str(fintech_n), "all years",       "kpi-c")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Bar + Pie ──────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Sector overview</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r1a, r1b = st.columns([3, 2])

with r1a:
    sec_df = (fc.groupby("sector").size()
                .reset_index(name="deals")
                .sort_values("deals", ascending=True).tail(10))
    fig = px.bar(sec_df, x="deals", y="sector", orientation="h",
                 color="deals", color_continuous_scale=COLORS_V,
                 labels={"deals": "Deals", "sector": ""},
                 title="Deals by Sector · Top 10 by deal count")
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Deals: <b>%{x}</b><extra></extra>"
    )
    fig = plotly_base(fig, 370)
    fig.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig.update_yaxes(tickfont=dict(size=11,
                     color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig, use_container_width=True)

with r1b:
    pie_df = (fc.groupby("sector").size()
                .reset_index(name="deals")
                .sort_values("deals", ascending=False).head(7))
    others = len(fc) - pie_df["deals"].sum()
    if others > 0:
        pie_df = pd.concat([pie_df,
            pd.DataFrame([{"sector": "Others", "deals": others}])],
            ignore_index=True)
    fig2 = px.pie(pie_df, names="sector", values="deals",
                  hole=0.5, color_discrete_sequence=COLORS_M,
                  title="Sector Share · % of total deals")
    fig2.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Deals: %{value}<br>"
                      "Share: %{percent}<extra></extra>",
        pull=[0.03] * len(pie_df)
    )
    fig2 = plotly_base(fig2, 370)
    fig2.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02,
            font=dict(size=10)
        ),
        margin=dict(t=40, b=20, l=20, r=100),
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Year trend by sector ───────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Sector trends over time</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

top8  = fc["sector"].value_counts().head(8).index.tolist()
trend = (fc[fc["sector"].isin(top8)]
         .groupby(["year", "sector"]).size()
         .reset_index(name="deals"))

fig3 = px.area(trend, x="year", y="deals", color="sector",
               color_discrete_sequence=COLORS_M,
               labels={"year": "Year", "deals": "Deals", "sector": "Sector"},
               title="Year-wise Deals by Sector · Top 8 sectors · stacked area")
fig3.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>"
                  "Year: %{x}<br>Deals: %{y}<extra></extra>"
)
fig3 = plotly_base(fig3, 380)
fig3.update_layout(
    title=dict(font=dict(size=13, color="#E8E8F0"), x=0, xref="paper"),
    margin=dict(t=40, b=8, l=8, r=8),
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
fig3.update_xaxes(dtick=1, tickangle=-45)
st.plotly_chart(fig3, use_container_width=True)

# ── Row 3: Post-2020 + Funding amount ─────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Post-2020 analysis</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r3a, r3b = st.columns(2)

with r3a:
    # Show Fintech growth year-wise to demonstrate dominance
    fintech_yr = (fc[fc["sector"] == "Fintech"]
                  .groupby("year").size()
                  .reset_index(name="deals"))

    top5_sectors = fc["sector"].value_counts().head(5).index.tolist()
    if "Fintech" not in top5_sectors:
        top5_sectors.append("Fintech")

    compare = (fc[fc["sector"].isin(top5_sectors)]
               .groupby(["year", "sector"]).size()
               .reset_index(name="deals"))

    colors_map = {s: ("#EF4444" if s == "Fintech" else "#6366F1")
                  for s in top5_sectors}

    fig4 = px.line(compare, x="year", y="deals",
                   color="sector",
                   color_discrete_map=colors_map,
                   markers=True,
                   labels={"year": "Year", "deals": "Deals",
                           "sector": "Sector"},
                   title="Fintech Growth vs Top Sectors")
    fig4.update_traces(
        line_width=2, marker_size=5,
        hovertemplate="<b>%{fullData.name}</b><br>"
                      "Year: %{x}<br>Deals: <b>%{y}</b><extra></extra>"
    )
    fig4 = plotly_base(fig4, 340)
    fig4.update_layout(
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper"),
        margin=dict(t=40, b=8, l=8, r=8),
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
    fig4.update_xaxes(dtick=1, tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

with r3b:
    fund_df = (fc.groupby("sector")["amount_usd"]
                 .sum().reset_index()
                 .rename(columns={"amount_usd": "total_usd"})
                 .sort_values("total_usd", ascending=True).tail(10))
    fund_df["total_bn"] = fund_df["total_usd"] / 1e9
    fig5 = px.bar(fund_df, x="total_bn", y="sector",
                  orientation="h", color="total_bn",
                  color_continuous_scale=COLORS_G,
                  labels={"total_bn": "Funding ($B)", "sector": ""},
                  title="Total Funding by Sector · In USD billions")
    fig5.update_traces(
        hovertemplate="<b>%{y}</b><br>"
                      "Funding: $<b>%{x:.2f}B</b><extra></extra>"
    )
    fig5 = plotly_base(fig5, 340)
    fig5.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig5.update_yaxes(tickfont=dict(size=11,
                      color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig5, use_container_width=True)

# ── Heatmap ───────────────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Sector heatmap</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

heat = (fc[fc["sector"].isin(top8)]
        .groupby(["year", "sector"]).size()
        .unstack(fill_value=0))

fig6 = px.imshow(heat.T, color_continuous_scale="Purples",
                 aspect="auto", text_auto=True,
                 labels=dict(x="Year", y="Sector", color="Deals"),
                 title="Sector × Year Deal Heatmap · Darker = more deals")
fig6.update_traces(
    hovertemplate="<b>%{y}</b> · %{x}<br>"
                  "Deals: <b>%{z}</b><extra></extra>"
)
fig6 = plotly_base(fig6, 310)
fig6.update_layout(
    coloraxis_showscale=False,
    title=dict(font=dict(size=13, color="#E8E8F0"),
               x=0, xref="paper")
)
fig6.update_xaxes(dtick=1, tickangle=-45, tickfont=dict(size=9))
fig6.update_yaxes(tickfont=dict(size=11,
                  color="rgba(232,232,240,0.7)"))
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.markdown('<div class="fs-footer">FundSight &nbsp;·&nbsp; '
            'Anuska Ghosh &nbsp;·&nbsp; Data Source: Kaggle</div>',
            unsafe_allow_html=True)