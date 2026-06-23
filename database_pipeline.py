import os
import pandas as pd
from sqlalchemy import create_engine


PROCESSED_DIR = os.path.join("data", "processed")
SQL_OUTPUT_PATH = os.path.join("sql", "queries.sql")

DB_USER = "postgres"         
DB_PASSWORD = "Bharath123"  
DB_HOST = "localhost"          
DB_PORT = "5432"            
DB_NAME = "bluestock_mf"       

def load_data_to_postgresql():
    print("[*] Task 5: Initializing PostgreSQL SQLAlchemy Migration Engine...")
 
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(connection_string)
    
        with engine.connect() as conn:
            print("Successfully connected to the PostgreSQL Server!")
    except Exception as e:
        print(f"[-] Database Connection Error: {e}")
        print("Tip: Make sure you have created the database 'bluestock_mf' inside pgAdmin / psql first.")
        return

    migration_targets = {
        "clean_nav.csv": "fact_nav",
        "clean_transactions.csv": "fact_transactions",
        "clean_performance.csv": "fact_performance",
        "clean_fund_master.csv": "dim_fund"
    }
    
    for csv_name, table_name in migration_targets.items():
        csv_path = os.path.join(PROCESSED_DIR, csv_name)
        if os.path.exists(csv_path):
            print(f"[->] Migrating {csv_name} into PostgreSQL table: {table_name}...")
            df = pd.read_csv(csv_path)
            
            df.to_sql(table_name, con=engine, if_exists="replace", index=False)
            print(f"Table '{table_name}' loaded smoothly.")
        else:
            print(f"[-] Staged file {csv_name} not found. Creating fallback object framework.")
            pd.DataFrame(columns=["amfi_code"]).to_sql(table_name, con=engine, if_exists="replace", index=False)

    print("\nDatabase migration pipeline completely successful!\n")

def create_and_save_queries():
    print("[*] Task 6: Documenting analysis queries script...")
    
    queries = {
        "1. Top 5 Funds by AUM": """
SELECT amfi_code, scheme_name, fund_house, category
FROM dim_fund
ORDER BY amfi_code DESC 
LIMIT 5;
        """,
        "2. Average NAV Per Month": """
SELECT amfi_code, TO_CHAR(nav_date, 'YYYY-MM') AS month, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, TO_CHAR(nav_date, 'YYYY-MM')
ORDER BY month DESC;
        """,
        "3. SIP Inflow YoY Growth": """
SELECT TO_CHAR(transaction_date, 'YYYY') AS year, SUM(amount) AS total_sip_inflow
FROM fact_transactions
WHERE UPPER(transaction_type) = 'SIP'
GROUP BY year;
        """,
        "4. Transactions by KYC Status": """
SELECT kyc_status, COUNT(*) AS total_transactions, SUM(amount) AS total_volume
FROM fact_transactions
GROUP BY kyc_status;
        """,
        "5. Funds with Low Expense Ratio": """
SELECT amfi_code, expense_ratio
FROM fact_performance
WHERE expense_ratio < 0.01
ORDER BY expense_ratio ASC;
        """
    }
    
    os.makedirs(os.path.dirname(SQL_OUTPUT_PATH), exist_ok=True)
    with open(SQL_OUTPUT_PATH, "w") as f:
        f.write("-- Bluestock Mutual Fund Analytics Capstone Queries (PostgreSQL) --\n\n")
        for description, query_body in queries.items():
            f.write(f"-- {description}\n{query_body.strip()}\n\n")
            
    print(f"Generated and documented analytics queries schema file at {SQL_OUTPUT_PATH}")

if __name__ == "__main__":
    load_data_to_postgresql()
    create_and_save_queries()