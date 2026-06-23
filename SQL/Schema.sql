-- Active: 1782191376875@@127.0.0.1@5432@bluestock_mf
-- sql/schema.sql

-- 1. Fund Dimension Table (Master Metadata)
CREATE TABLE  dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT ,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    risk_category TEXT
);

-- 2. Historical NAV Fact Table (Time Series Tracks)
CREATE TABLE fact_nav (
    amfi_code TEXT,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, nav),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 3. Investor Transactions Fact Table
CREATE TABLE fact_transactions (
    investor_id  TEXT ,
    amfi_code TEXT,
    transaction_date DATE,
    transaction_type TEXT, -- SIP, Lumpsum, Redemption
    amount_inr REAL,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 4. Fund Performance Fact Table
CREATE TABLE fact_performance (
    amfi_code TEXT PRIMARY KEY,
    sharpe_ratio REAL,
    alpha REAL,
    beta REAL,
    expense_ratio_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);