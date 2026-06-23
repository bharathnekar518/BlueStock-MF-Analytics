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
SELECT TO_CHAR(transaction_date, 'YYYY') AS year, SUM(amount) AS total_sip_inflow
FROM fact_transactions
WHERE UPPER(transaction_type) = 'SIP'
GROUP BY year;

-- 4. Transactions by KYC Status
SELECT kyc_status, COUNT(*) AS total_transactions, SUM(amount) AS total_volume
FROM fact_transactions
GROUP BY kyc_status;

-- 5. Funds with Low Expense Ratio
SELECT amfi_code, expense_ratio
FROM fact_performance
WHERE expense_ratio < 0.01
ORDER BY expense_ratio ASC;

