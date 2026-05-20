# =============================================================
# FundSight — City Analysis
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

st.set_page_config(page_title="FundSight — City Analysis",
                   page_icon="🏙️", layout="wide",
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

COLORS_O = ["#78350F","#92400E","#B45309","#D97706","#F59E0B","#FCD34D"]
COLORS_M = ["#6366F1","#8B5CF6","#EC4899","#F59E0B","#10B981",
            "#06B6D4","#EF4444","#FB923C"]

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
    df["funding_stage"].isin(stages if stages else all_stages)
]
fc = f.dropna(subset=["city"])

# ── Page header ───────────────────────────────────────────────
st.markdown("""
<div style='padding:6px 0 20px 0;'>
    <div class='pg-title'>City Analysis</div>
    <div class='pg-sub'>
        Geographic distribution of startup funding across Indian cities
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
top_c      = fc["city"].value_counts()
top_city   = top_c.index[0]     if len(top_c) else "—"
top_city_n = int(top_c.iloc[0]) if len(top_c) else 0
n_cities   = fc["city"].nunique()
blr        = len(fc[fc["city"] == "Bangalore"])
del_ncr    = len(fc[fc["city"].isin(["Delhi","Delhi NCR","Gurgaon"])])
blr_pct    = round(blr    * 100 / len(fc), 1) if len(fc) else 0
del_pct    = round(del_ncr * 100 / len(fc), 1) if len(fc) else 0

k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub, cls):
    col.markdown(f"""
<div class="{cls}"><div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {'text' if len(str(value)) > 7 else ''}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div></div>""", unsafe_allow_html=True)

kpi(k1, "Cities Covered",  str(n_cities),   "in dataset",        "kpi-v")
kpi(k2, "Top City",        top_city,         f"{top_city_n} deals","kpi-o")
kpi(k3, "Bangalore Share", f"{blr_pct}%",    f"{blr} deals",      "kpi-g")
kpi(k4, "Delhi NCR Share", f"{del_pct}%",    f"{del_ncr} deals",  "kpi-c")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Top cities bar + pie ───────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'City overview</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r1a, r1b = st.columns([3, 2])

with r1a:
    city_df = (fc[fc["city"] != "Other City"]
               .groupby("city").size()
               .reset_index(name="deals")
               .sort_values("deals", ascending=True).tail(12))
    fig = px.bar(city_df, x="deals", y="city", orientation="h",
                 color="deals", color_continuous_scale=COLORS_O,
                 labels={"deals": "Deals", "city": ""},
                 title="Deals by City · Top 12 by deal count")
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Deals: <b>%{x}</b><extra></extra>"
    )
    fig = plotly_base(fig, 400)
    fig.update_layout(
        coloraxis_showscale=False,
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper")
    )
    fig.update_yaxes(tickfont=dict(size=11,
                     color="rgba(232,232,240,0.7)"))
    st.plotly_chart(fig, use_container_width=True)

with r1b:
    pie_df = (fc[fc["city"] != "Other City"]
              .groupby("city").size()
              .reset_index(name="deals")
              .sort_values("deals", ascending=False).head(6))
    others = len(fc) - pie_df["deals"].sum()
    if others > 0:
        pie_df = pd.concat([pie_df,
            pd.DataFrame([{"city": "Others", "deals": others}])],
            ignore_index=True)
    fig2 = px.pie(pie_df, names="city", values="deals",
                  hole=0.5, color_discrete_sequence=COLORS_M,
                  title="City Share · % of total deals")
    fig2.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Deals: %{value}<br>"
                      "Share: %{percent}<extra></extra>",
        pull=[0.03] * len(pie_df)
    )
    fig2 = plotly_base(fig2, 400)
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

# ── Bangalore vs Delhi NCR ────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Bangalore vs Delhi NCR</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

r2a, r2b = st.columns([3, 2])

with r2a:
    bd = fc[fc["city"].isin(
        ["Bangalore","Delhi","Delhi NCR","Gurgaon"])].copy()
    bd["city_group"] = bd["city"].replace(
        {"Delhi": "Delhi NCR", "Gurgaon": "Delhi NCR"}
    )
    cy = (bd.groupby(["year","city_group"]).size()
            .reset_index(name="deals"))
    fig3 = px.line(cy, x="year", y="deals",
                   color="city_group", markers=True,
                   color_discrete_map={
                       "Bangalore": "#6366F1",
                       "Delhi NCR": "#F59E0B"
                   },
                   labels={"year": "Year", "deals": "Deals",
                           "city_group": "City"},
                   title="Year-wise Deal Volume · Bangalore vs Delhi NCR")
    fig3.update_traces(
        line_width=2.5, marker_size=6,
        hovertemplate="<b>%{fullData.name}</b><br>"
                      "Year: %{x}<br>"
                      "Deals: <b>%{y}</b><extra></extra>"
    )
    fig3 = plotly_base(fig3, 310)
    fig3.update_layout(
        title=dict(font=dict(size=13, color="#E8E8F0"),
                   x=0, xref="paper"),
        legend=dict(
            orientation="v",
            yanchor="top", y=1,
            xanchor="right", x=1,
            font=dict(size=10),
            bgcolor="rgba(19,19,26,0.8)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1
        )
    )
    fig3.update_xaxes(dtick=1, tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

with r2b:
    stats = (bd.groupby("city_group").agg(
        deals=("city_group", "count"),
        total_funding=("amount_usd", "sum"),
        avg_deal=("amount_usd", "mean")
    ).reset_index())
    stats["total_bn"] = stats["total_funding"] / 1e9
    stats["avg_m"]    = stats["avg_deal"] / 1e6

    for _, row in stats.iterrows():
        color = "#6366F1" if row["city_group"] == "Bangalore" \
                else "#F59E0B"
        st.markdown(f"""
<div class="insight-card" style="border-left-color:{color};">
    <div class="insight-tag" style="color:{color};">
        {row['city_group']}
    </div>
    <div class="insight-body">
        <b>{int(row['deals']):,} deals</b> &nbsp;·&nbsp;
        <b>${row['total_bn']:.1f}B</b> total<br>
        Avg deal size: <b>${row['avg_m']:.1f}M</b>
    </div>
</div>
""", unsafe_allow_html=True)

    blr_lead = blr - del_ncr
    st.markdown(f"""
<div class="insight-card r" style="margin-top:8px;">
    <div class="insight-tag">Key Finding</div>
    <div class="insight-body">
        Bangalore leads Delhi NCR by <b>{abs(blr_lead):,} deals</b>
        ({blr_pct}% vs {del_pct}% of total), confirming its dominance
        as India's startup capital.
    </div>
</div>
""", unsafe_allow_html=True)

# ── City × Sector heatmap ─────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'City × sector breakdown</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

top_cities  = (fc[fc["city"] != "Other City"]["city"]
               .value_counts().head(8).index.tolist())
top_sectors = (fc[~fc["sector"].isin(["Unknown","Other"])]["sector"]
               .value_counts().head(8).index.tolist())
heat = (fc[fc["city"].isin(top_cities) &
           fc["sector"].isin(top_sectors)]
        .groupby(["city","sector"]).size()
        .unstack(fill_value=0))

fig4 = px.imshow(heat, color_continuous_scale="Oranges",
                 aspect="auto", text_auto=True,
                 labels=dict(x="Sector", y="City", color="Deals"),
                 title="City × Sector Deal Matrix · Top 8 cities vs top 8 sectors")
fig4.update_traces(
    hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>"
                  "Deals: <b>%{z}</b><extra></extra>"
)
fig4 = plotly_base(fig4, 320)
fig4.update_layout(
    coloraxis_showscale=False,
    title=dict(font=dict(size=13, color="#E8E8F0"),
               x=0, xref="paper")
)
fig4.update_xaxes(tickangle=-35, tickfont=dict(size=10))
fig4.update_yaxes(tickfont=dict(size=11,
                  color="rgba(232,232,240,0.7)"))
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown('<div class="fs-footer">FundSight &nbsp;·&nbsp; '
            'Anuska Ghosh &nbsp;·&nbsp; Data Source: Kaggle</div>',
            unsafe_allow_html=True)