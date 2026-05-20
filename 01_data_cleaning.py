# =============================================================
# FundSight — Step 1: Data Cleaning (v2)
# =============================================================
# Inputs : data/SRK_startup_funding.csv
#          data/2010-2025_startup_funding.csv
# Output : data/cleaned_startup_funding.csv
# =============================================================

import pandas as pd
import numpy as np
import re

# ─────────────────────────────────────────
# 1. LOAD BOTH DATASETS
# ─────────────────────────────────────────

srk = pd.read_csv("data/SRK_startup_funding.csv")
df2 = pd.read_csv("data/2010-2025_startup_funding.csv")

print(f"SRK loaded:        {srk.shape[0]} rows, {srk.shape[1]} cols")
print(f"2010-2025 loaded:  {df2.shape[0]} rows, {df2.shape[1]} cols")


# ─────────────────────────────────────────
# 2. CLEAN SRK DATASET
# ─────────────────────────────────────────

srk = srk.rename(columns={
    "Startup Name"      : "startup_name",
    "Industry Vertical" : "sector",
    "SubVertical"       : "sub_sector",
    "City  Location"    : "city",
    "Investors Name"    : "investors",
    "InvestmentnType"   : "funding_stage",
    "Amount in USD"     : "amount_usd",
    "Date dd/mm/yyyy"   : "date",
    "Remarks"           : "remarks",
    "Sr No"             : "sr_no"
})

# Extract year
srk["year"] = pd.to_datetime(
    srk["date"], dayfirst=True, errors="coerce"
).dt.year
srk["year"] = srk["year"].fillna(0).astype(int)

# Clean funding amount
def clean_amount(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace(",", "")
    val = re.sub(r"[^\d.]", "", val)
    if val in ("", "."):
        return np.nan
    try:
        return float(val)
    except:
        return np.nan

srk["amount_usd"] = srk["amount_usd"].apply(clean_amount)

# ── City standardisation ──────────────────
city_map = {
    "Bengaluru": "Bangalore", "bengaluru": "Bangalore",
    "bangalore": "Bangalore", "Banglore": "Bangalore",
    "Gurugram": "Gurgaon", "gurugram": "Gurgaon",
    "gurgaon": "Gurgaon",
    "New Delhi": "Delhi", "new delhi": "Delhi",
    "delhi": "Delhi",
    "NCR": "Delhi NCR", "Noida": "Delhi NCR",
    "noida": "Delhi NCR", "Faridabad": "Delhi NCR",
    "Ghaziabad": "Delhi NCR",
    "Mumbai": "Mumbai", "mumbai": "Mumbai",
    "Pune": "Pune", "pune": "Pune",
    "Hyderabad": "Hyderabad", "hyderabad": "Hyderabad",
    "Chennai": "Chennai", "chennai": "Chennai",
    "Ahmedabad": "Ahmedabad", "Ahmedabad ": "Ahmedabad",
    "Ahemdabad": "Ahmedabad", "Ahemadabad": "Ahmedabad",
    "Jaipur": "Jaipur", "jaipur": "Jaipur",
    "Kolkata": "Kolkata", "kolkata": "Kolkata",
    "Chandigarh": "Chandigarh",
    "Indore": "Indore",
    "Nagpur": "Nagpur",
    "Kochi": "Kochi", "Cochin": "Kochi",
    "Coimbatore": "Coimbatore",
    "Surat": "Surat",
    "Vadodara": "Vadodara",
    "Bhopal": "Bhopal",
    "Lucknow": "Lucknow",
}

KNOWN_CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Gurgaon", "Delhi NCR",
    "Pune", "Hyderabad", "Chennai", "Ahmedabad", "Jaipur",
    "Kolkata", "Chandigarh", "Indore", "Nagpur", "Kochi",
    "Coimbatore", "Surat", "Vadodara", "Bhopal", "Lucknow",
]

srk["city"] = srk["city"].str.strip()
srk["city"] = srk["city"].replace(city_map)
srk["city"] = srk["city"].apply(
    lambda x: x if pd.isna(x) else (x if x in KNOWN_CITIES else "Other City")
)

# ── Sector standardisation ────────────────
sector_map = {
    "eCommerce": "E-Commerce", "ECommerce": "E-Commerce",
    "E-commerce": "E-Commerce", "Ecommerce": "E-Commerce",
    "Consumer Internet": "Consumer Internet",
    "Technology": "Technology",
    "E-Tech": "EdTech",
    "FinTech": "Fintech", "Fin-Tech": "Fintech",
    "fin-tech": "Fintech", "fintech": "Fintech",
    "Finance": "Fintech",
    "Food & Beverage": "FoodTech", "Food and Beverage": "FoodTech",
    "Foodtech": "FoodTech", "food tech": "FoodTech",
    "HealthTech": "Healthcare", "Health Tech": "Healthcare",
    "healthcare": "Healthcare",
    "Logistics": "Logistics", "logistics": "Logistics",
    "Education": "EdTech", "education": "EdTech",
}

KNOWN_SECTORS = [
    "Consumer Internet", "Technology", "E-Commerce", "Fintech",
    "Healthcare", "EdTech", "Logistics", "FoodTech", "Insurance",
    "Transportation", "SaaS", "Retail", "Real Estate", "Media",
    "Agriculture", "Manufacturing", "Fashion and Apparel",
    "Hospitality", "Aerospace", "Sports", "Services", "Unknown"
]

srk["sector"] = srk["sector"].str.strip()
srk["sector"] = srk["sector"].replace(sector_map)
srk["sector"] = srk["sector"].fillna("Unknown")
srk["sector"] = srk["sector"].apply(
    lambda x: x if x in KNOWN_SECTORS else "Other"
)

# ── Funding stage standardisation ─────────
def clean_stage(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).strip().lower()
    val = val.replace("\\n", " ").replace("\n", " ")
    if "seed" in val or "angel" in val:
        return "Seed"
    elif "pre-series" in val or "pre series" in val:
        return "Pre-Series A"
    elif "series a" in val:
        return "Series A"
    elif "series b" in val:
        return "Series B"
    elif "series c" in val:
        return "Series C"
    elif "series d" in val:
        return "Series D"
    elif "series e" in val or "series f" in val or \
         "series g" in val or "series h" in val or \
         "series j" in val:
        return "Series E+"
    elif "private equity" in val or "privateequity" in val:
        return "Private Equity"
    elif "debt" in val or "loan" in val or "term loan" in val or \
         "mezzanine" in val or "structured" in val:
        return "Debt Funding"
    elif "venture" in val:
        return "Venture"
    elif "crowd" in val:
        return "Crowdfunding"
    else:
        return "Other"

srk["funding_stage"] = srk["funding_stage"].apply(clean_stage)

srk_clean = srk[[
    "startup_name", "sector", "city",
    "investors", "funding_stage", "amount_usd", "year"
]].copy()


# ─────────────────────────────────────────
# 3. CLEAN 2010-2025 DATASET
# ─────────────────────────────────────────

df2 = df2.rename(columns={
    "Company"           : "startup_name",
    "Industry"          : "sector",
    "Funding_Amount_USD": "amount_usd",
    "Investor"          : "investors",
    "Year"              : "year",
    "City"              : "city"
})

df2["funding_stage"] = "Unknown"

df2["city"] = df2["city"].str.strip()
df2["city"] = df2["city"].replace(city_map)
df2["city"] = df2["city"].apply(
    lambda x: x if pd.isna(x) else (x if x in KNOWN_CITIES else "Other City")
)

df2["sector"] = df2["sector"].str.strip()
df2["sector"] = df2["sector"].replace(sector_map)
df2["sector"] = df2["sector"].fillna("Unknown")
df2["sector"] = df2["sector"].apply(
    lambda x: x if x in KNOWN_SECTORS else "Other"
)

df2_clean = df2[[
    "startup_name", "sector", "city",
    "investors", "funding_stage", "amount_usd", "year"
]].copy()


# ─────────────────────────────────────────
# 4. MERGE BOTH DATASETS
# ─────────────────────────────────────────

combined = pd.concat([srk_clean, df2_clean], ignore_index=True)
print(f"\nCombined before dedup: {combined.shape[0]} rows")

combined = combined.drop_duplicates(
    subset=["startup_name", "year", "amount_usd"]
)
print(f"Combined after dedup:  {combined.shape[0]} rows")


# ─────────────────────────────────────────
# 5. FINAL CLEANUP
# ─────────────────────────────────────────

combined = combined[combined["year"].between(2010, 2025)]
combined["startup_name"] = combined["startup_name"].str.strip().str.title()
combined["city"]         = combined["city"].str.strip()
combined["sector"]       = combined["sector"].str.strip()
combined["city"]         = combined["city"].replace({"Delhi Ncr": "Delhi NCR"})
combined                 = combined.reset_index(drop=True)

print(f"\nFinal dataset:         {combined.shape[0]} rows")
print(f"Year range:            {combined['year'].min()} – {combined['year'].max()}")
print(f"\nTop sectors:\n{combined['sector'].value_counts().head(15)}")
print(f"\nTop cities:\n{combined['city'].value_counts().head(15)}")
print(f"\nFunding stages:\n{combined['funding_stage'].value_counts()}")
print(f"\nMissing values:\n{combined.isnull().sum()}")


# ─────────────────────────────────────────
# 6. SAVE CLEANED FILE
# ─────────────────────────────────────────

combined.to_csv("data/cleaned_startup_funding.csv", index=False)
print("\n✅ Saved to data/cleaned_startup_funding.csv")