# =============================================================
# FundSight — Data Explorer
# =============================================================

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

st.set_page_config(page_title="FundSight — Data Explorer",
                   page_icon="🔍", layout="wide",
                   initial_sidebar_state="expanded")

def load_css():
    p = os.path.join(os.path.dirname(__file__), "..", "style.css")
    with open(p, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

with st.sidebar:
    st.markdown("""
    <div style='padding:20px 18px 8px;'>
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
    st.markdown("---")
    st.markdown("<div style='font-size:0.6rem;text-transform:uppercase;"
                "letter-spacing:0.12em;color:rgba(232,232,240,0.25);"
                "font-weight:600;padding:0 18px 8px;'>Filters</div>",
                unsafe_allow_html=True)
    year_range  = st.slider("Year", 2010, 2025, (2010, 2025))
    all_sectors = sorted(
        df[df["sector"] != "Unknown"]["sector"].unique()
    )
    sectors = st.multiselect("Sector", all_sectors,
                             default=all_sectors)
    all_cities = sorted(df["city"].dropna().unique())
    cities = st.multiselect("City", all_cities,
                            default=all_cities)
    all_stages = sorted(df["funding_stage"].unique())
    stages = st.multiselect("Stage", all_stages,
                            default=all_stages)
    search = st.text_input("Search startup name",
                           placeholder="e.g. Flipkart, Zomato...")

f = df[
    df["year"].between(year_range[0], year_range[1]) &
    df["sector"].isin(sectors if sectors else all_sectors) &
    df["city"].isin(cities   if cities   else all_cities)  &
    df["funding_stage"].isin(stages if stages else all_stages)
]

if search:
    f = f[f["startup_name"].str.contains(
        search, case=False, na=False
    )]

st.markdown("""
<div style='padding:6px 0 20px 0;'>
    <div class='pg-title'>Data Explorer</div>
    <div class='pg-sub'>
        Browse and search all 3,000+ funding records
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
k1,k2,k3,k4 = st.columns(4)

def kpi(col, label, value, sub, cls):
    col.markdown(f"""
<div class="{cls}"><div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value {'text' if len(str(value))>7 else ''}">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div></div>""", unsafe_allow_html=True)

kpi(k1,"Matching Records", f"{len(f):,}",
    "after filters","kpi-v")
kpi(k2,"Total Funding",
    f"${f['amount_usd'].sum()/1e9:.1f}B",
    "filtered set","kpi-g")
kpi(k3,"Avg Deal Size",
    f"${f['amount_usd'].mean()/1e6:.1f}M",
    "mean value","kpi-o")
kpi(k4,"Unique Startups",
    f"{f['startup_name'].nunique():,}",
    "in results","kpi-c")

st.markdown("<br>", unsafe_allow_html=True)

# ── Sort options ──────────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Records</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

col_sort, col_order, _ = st.columns([2, 2, 6])
sort_by = col_sort.selectbox("Sort by",
    ["year","amount_usd","startup_name","sector","city"],
    index=0)
order = col_order.selectbox("Order",
    ["Descending","Ascending"], index=0)

ascending = order == "Ascending"
display = (f.sort_values(sort_by, ascending=ascending)
            .reset_index(drop=True))

# Format amount
display["amount_usd"] = display["amount_usd"].apply(
    lambda x: f"${x/1e6:.1f}M" if pd.notna(x) else "—"
)

# Rename for display
display = display.rename(columns={
    "startup_name":  "Startup",
    "sector":        "Sector",
    "city":          "City",
    "investors":     "Investors",
    "funding_stage": "Stage",
    "amount_usd":    "Amount (USD)",
    "year":          "Year"
})

st.markdown('<div class="chart-card" style="padding:0;overflow:hidden;">',
            unsafe_allow_html=True)
st.dataframe(
    display[["Startup","Sector","City","Stage",
             "Amount (USD)","Year","Investors"]],
    use_container_width=True,
    height=520,
    hide_index=True
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style='font-size:0.72rem;color:rgba(232,232,240,0.25);
            padding:8px 2px;text-align:right;'>
    Showing {len(display):,} records
</div>
""", unsafe_allow_html=True)

# ── Download ──────────────────────────────────────────────────
st.markdown('<div class="sec-head"><span class="sec-head-title">'
            'Export</span>'
            '<div class="sec-head-line"></div></div>',
            unsafe_allow_html=True)

csv = f.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="fundsight_filtered.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown('<div class="fs-footer">FundSight &nbsp;·&nbsp; '
            'Anuska Ghosh &nbsp;·&nbsp; Data Source: Kaggle</div>',
            unsafe_allow_html=True)