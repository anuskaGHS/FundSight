-- =====================================================
-- FundSight — Business Insights SQL Queries
-- Database: fundsight | Table: startup_funding
-- =====================================================


-- ─────────────────────────────────────────
-- Q1. Total deals and funding by sector
-- (Sector-wise breakdown)
-- ─────────────────────────────────────────
SELECT 
    sector,
    COUNT(*) AS total_deals,
    ROUND(SUM(amount_usd) / 1000000, 2) AS total_funding_million_usd
FROM startup_funding
WHERE sector != 'Unknown'
GROUP BY sector
ORDER BY total_deals DESC;


-- ─────────────────────────────────────────
-- Q2. Year-wise funding trend (2010–2025)
-- ─────────────────────────────────────────
SELECT
    year,
    COUNT(*) AS total_deals,
    ROUND(SUM(amount_usd) / 1000000, 2) AS total_funding_million_usd
FROM startup_funding
GROUP BY year
ORDER BY year ASC;


-- ─────────────────────────────────────────
-- Q3. City-wise deal volume
-- (Bangalore vs Delhi NCR concentration)
-- ─────────────────────────────────────────
SELECT
    city,
    COUNT(*) AS total_deals,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM startup_funding), 2) AS deal_share_pct
FROM startup_funding
WHERE city IS NOT NULL
GROUP BY city
ORDER BY total_deals DESC
LIMIT 10;


-- ─────────────────────────────────────────
-- Q4. Funding stage distribution
-- ─────────────────────────────────────────
SELECT
    funding_stage,
    COUNT(*) AS total_deals,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM startup_funding), 2) AS pct_of_total
FROM startup_funding
GROUP BY funding_stage
ORDER BY total_deals DESC;


-- ─────────────────────────────────────────
-- Q5. Post-2020 Fintech dominance
-- Compare Fintech vs other sectors after 2020
-- ─────────────────────────────────────────
SELECT
    sector,
    COUNT(*) AS deals_post_2020,
    ROUND(SUM(amount_usd) / 1000000, 2) AS funding_million_usd
FROM startup_funding
WHERE year >= 2020
AND sector != 'Unknown'
GROUP BY sector
ORDER BY deals_post_2020 DESC;


-- ─────────────────────────────────────────
-- Q6. Year-over-year growth in deal count
-- ─────────────────────────────────────────
SELECT
    year,
    total_deals,
    LAG(total_deals) OVER (ORDER BY year) AS prev_year_deals,
    ROUND(
        (total_deals - LAG(total_deals) OVER (ORDER BY year)) * 100.0 /
        NULLIF(LAG(total_deals) OVER (ORDER BY year), 0),
    2) AS yoy_growth_pct
FROM (
    SELECT year, COUNT(*) AS total_deals
    FROM startup_funding
    GROUP BY year
) AS yearly
ORDER BY year ASC;


-- ─────────────────────────────────────────
-- Q7. Bangalore vs Delhi NCR — head to head
-- ─────────────────────────────────────────
SELECT
    city,
    COUNT(*) AS total_deals,
    ROUND(SUM(amount_usd) / 1000000, 2) AS total_funding_million_usd,
    ROUND(AVG(amount_usd) / 1000000, 2) AS avg_deal_size_million_usd
FROM startup_funding
WHERE city IN ('Bangalore', 'Delhi', 'Delhi NCR', 'Gurgaon')
GROUP BY city
ORDER BY total_deals DESC;


-- ─────────────────────────────────────────
-- Q8. Top funded startups overall
-- ─────────────────────────────────────────
SELECT
    startup_name,
    sector,
    city,
    year,
    ROUND(amount_usd / 1000000, 2) AS funding_million_usd
FROM startup_funding
WHERE amount_usd IS NOT NULL
ORDER BY amount_usd DESC
LIMIT 15;