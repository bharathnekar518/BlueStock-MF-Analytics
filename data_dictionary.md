# Mutual Fund Analytics - Platform Data Dictionary

### 1. dim_fund (Dimension Table)
* **amfi_code (TEXT, PK):** Unique indexing identifier key assigned to the fund scheme.
* **fund_house (TEXT):** Name of the Asset Management Company (AMC).
* **scheme_name (TEXT):** Full commercial title of the investment vehicle.
* **category (TEXT):** High-level asset class allocation grouping (Equity, Debt, Hybrid).

### 2. fact_nav (Fact Table)
* **amfi_code (TEXT, FK):** Direct reference code tracking back to fund dimension.
* **nav_date (DATE):** The market session execution tracking date timestamp.
* **nav (REAL):** Net Asset Value value price points.

### 3. fact_transactions (Fact Table)
* **transaction_id (TEXT, PK):** Unique system identifier string for the record entry.
* **amfi_code (TEXT, FK):** Target investment scheme relational reference code.
* **transaction_type (TEXT):** Action categorization tags (SIP, Lumpsum, Redemption).
* **amount (REAL):** Fiat scale volume transacted.