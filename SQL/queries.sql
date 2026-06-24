-- Active: 1782191376875@@127.0.0.1@5432@bluestock_mf
-- Bluestock Mutual Fund Analytics Capstone Queries (PostgreSQL) --

-- 1. Top 5 Funds by AUM
SELECT amfi_code, scheme_name, fund_house, category
FROM dim_fund
ORDER BY amfi_code DESC 
LIMIT 5;

-- 2. Average NAV Per Month
SELECT amfi_code, TO_CHAR(nav_date, 'YYYY-MM') AS month, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, TO_CHAR(nav_date, 'YYYY-MM')
ORDER BY month DESC;

-- 3. SIP Inflow YoY Growth
SELECT 
    TO_CHAR(transaction_date::date, 'YYYY') AS year, 
    SUM(amount_inr) AS total_sip_inflow
FROM fact_transactions
WHERE transaction_type ILIKE '%SIP%'
GROUP BY TO_CHAR(transaction_date::date, 'YYYY')
ORDER BY year ASC;

-- 4. Transactions by KYC Status
SELECT kyc_status, COUNT(*) AS total_transactions, SUM(amount_inr) AS total_volume
FROM fact_transactions
GROUP BY kyc_status;

-- 5. Funds with Low Expense Ratio
SELECT amfi_code, expense_ratio_pct
FROM fact_performance
WHERE expense_ratio_pct < 0.01
ORDER BY expense_ratio_pct ASC;

--6 In fact_transcations show the columns in the table
SELECT  amfi_code, amount_inr, transaction_type 
FROM fact_transactionss;

--7 Using Inner Join with dim_fund show me the Sheme_name
SELECT 
    f.scheme_name,        
    n.amfi_code, 
    n.nav_date::date AS execution_date, 
    n.nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code   
ORDER BY n.nav_date DESC
LIMIT 10;

--8 Show me the morningstar_rating is more than 3 in fact_performance
SELECT * FROM fact_performance
WHERE morningstar_rating > 3;

--9 Show me How many Males are making transactions from table fact_transactions
SELECT age_group, COUNT(*) AS total_transactions
FROM fact_transactions
WHERE gender = 'Male'
GROUP BY age_group;

--10 Dense Ranking of Funds by Sharpe Ratio within each Category
SELECT 
    f.category,
    f.scheme_name,
    p.amfi_code,
    p.sharpe_ratio,
    DENSE_RANK() OVER (
        PARTITION BY f.category 
        ORDER BY p.sharpe_ratio DESC
    ) AS rank_in_category
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code;