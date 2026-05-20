# =============================================================
# FundSight — Step 3: Exploratory Data Analysis (EDA)
# =============================================================
# Reads : data/cleaned_startup_funding.csv
# Output: notebooks/charts/ (saves all plots as PNG)
# =============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────

df = pd.read_csv("data/cleaned_startup_funding.csv")

# Create output folder for charts
os.makedirs("notebooks/charts", exist_ok=True)

# Global style
sns.set_theme(style="darkgrid")
COLORS = sns.color_palette("muted", 12)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.family"] = "sans-serif"

print(f"Loaded {len(df)} rows for EDA\n")


# ─────────────────────────────────────────
# CHART 1: Year-wise Deal Count (2010–2025)
# ─────────────────────────────────────────

yearly = df.groupby("year").size().reset_index(name="deals")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(yearly["year"], yearly["deals"], marker="o",
        color=COLORS[0], linewidth=2.5, markersize=6)
ax.fill_between(yearly["year"], yearly["deals"],
                alpha=0.15, color=COLORS[0])

ax.set_title("Year-wise Startup Funding Deals in India (2010–2025)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Number of Deals", fontsize=11)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("notebooks/charts/01_yearly_deal_trend.png")
plt.close()
print("✅ Chart 1 saved: yearly deal trend")


# ─────────────────────────────────────────
# CHART 2: Top 10 Sectors by Deal Count
# ─────────────────────────────────────────

sector_deals = (df[df["sector"] != "Unknown"]
                .groupby("sector").size()
                .reset_index(name="deals")
                .sort_values("deals", ascending=False)
                .head(10))

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(sector_deals["sector"][::-1],
               sector_deals["deals"][::-1],
               color=COLORS)
ax.bar_label(bars, padding=4, fontsize=9)
ax.set_title("Top 10 Sectors by Number of Deals",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Number of Deals", fontsize=11)
ax.set_ylabel("Sector", fontsize=11)
plt.tight_layout()
plt.savefig("notebooks/charts/02_top_sectors.png")
plt.close()
print("✅ Chart 2 saved: top sectors")


# ─────────────────────────────────────────
# CHART 3: Top 10 Cities by Deal Volume
# ─────────────────────────────────────────

city_deals = (df.dropna(subset=["city"])
              .groupby("city").size()
              .reset_index(name="deals")
              .sort_values("deals", ascending=False)
              .head(10))

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(city_deals["city"], city_deals["deals"],
              color=COLORS)
ax.bar_label(bars, padding=4, fontsize=9)
ax.set_title("Top 10 Cities by Number of Deals",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("City", fontsize=11)
ax.set_ylabel("Number of Deals", fontsize=11)
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("notebooks/charts/03_top_cities.png")
plt.close()
print("✅ Chart 3 saved: top cities")


# ─────────────────────────────────────────
# CHART 4: Funding Stage Distribution (Pie)
# ─────────────────────────────────────────

stage_counts = df["funding_stage"].value_counts()

fig, ax = plt.subplots(figsize=(9, 9))
wedges, texts, autotexts = ax.pie(
    stage_counts.values,
    labels=stage_counts.index,
    autopct="%1.1f%%",
    colors=sns.color_palette("pastel", len(stage_counts)),
    startangle=140,
    pctdistance=0.82
)
for text in autotexts:
    text.set_fontsize(8)
ax.set_title("Funding Stage Distribution",
             fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("notebooks/charts/04_funding_stage_pie.png")
plt.close()
print("✅ Chart 4 saved: funding stage distribution")


# ─────────────────────────────────────────
# CHART 5: Post-2020 Fintech Dominance
# Top sectors AFTER 2020
# ─────────────────────────────────────────

post2020 = (df[(df["year"] >= 2020) & (df["sector"] != "Unknown")]
            .groupby("sector").size()
            .reset_index(name="deals")
            .sort_values("deals", ascending=False)
            .head(10))

fig, ax = plt.subplots(figsize=(12, 6))
bar_colors = ["#e74c3c" if s == "Fintech" else COLORS[2]
              for s in post2020["sector"]]
bars = ax.barh(post2020["sector"][::-1],
               post2020["deals"][::-1],
               color=bar_colors[::-1])
ax.bar_label(bars, padding=4, fontsize=9)
ax.set_title("Top Sectors Post-2020 (Fintech highlighted)",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Number of Deals", fontsize=11)
ax.set_ylabel("Sector", fontsize=11)
plt.tight_layout()
plt.savefig("notebooks/charts/05_post2020_fintech.png")
plt.close()
print("✅ Chart 5 saved: post-2020 fintech dominance")


# ─────────────────────────────────────────
# CHART 6: Bangalore vs Delhi NCR
# Year-wise deal comparison
# ─────────────────────────────────────────

blr_del = df[df["city"].isin(["Bangalore", "Delhi", "Delhi NCR", "Gurgaon"])]
blr_del = blr_del.copy()
blr_del["city_group"] = blr_del["city"].replace({
    "Delhi": "Delhi NCR",
    "Gurgaon": "Delhi NCR"
})

city_year = (blr_del.groupby(["year", "city_group"])
             .size().reset_index(name="deals"))

fig, ax = plt.subplots(figsize=(12, 5))
for city, grp in city_year.groupby("city_group"):
    ax.plot(grp["year"], grp["deals"], marker="o",
            linewidth=2.5, markersize=6, label=city)

ax.set_title("Bangalore vs Delhi NCR — Year-wise Deal Volume",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Number of Deals", fontsize=11)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.legend(fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("notebooks/charts/06_blr_vs_delhi.png")
plt.close()
print("✅ Chart 6 saved: Bangalore vs Delhi NCR")


# ─────────────────────────────────────────
# CHART 7: Sector Trend Over Years (Heatmap)
# ─────────────────────────────────────────

top_sectors = (df[df["sector"] != "Unknown"]
               ["sector"].value_counts()
               .head(8).index.tolist())

heat_data = (df[df["sector"].isin(top_sectors)]
             .groupby(["year", "sector"])
             .size().unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(heat_data.T, annot=True, fmt="d",
            cmap="YlOrRd", linewidths=0.5,
            ax=ax, cbar_kws={"label": "Number of Deals"})
ax.set_title("Sector-wise Deal Heatmap by Year",
             fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Sector", fontsize=11)
plt.tight_layout()
plt.savefig("notebooks/charts/07_sector_heatmap.png")
plt.close()
print("✅ Chart 7 saved: sector heatmap")


print("\n🎉 All 7 charts saved to notebooks/charts/")
print("Open the charts folder in VS Code to preview them.")