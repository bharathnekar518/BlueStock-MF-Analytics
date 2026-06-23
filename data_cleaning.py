import os
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

def clean_nav_history():
    print("[*] Standardizing columns for nav_history...")
    nav_files = [f for f in os.listdir(RAW_DIR) if f.startswith("nav_history_") and f.endswith(".csv")]
    if not nav_files: return
    
    df = pd.concat([pd.read_csv(os.path.join(RAW_DIR, f)) for f in nav_files], ignore_index=True)
    
    df.rename(columns={
        'date': 'nav_date', 
        'scheme_code': 'amfi_code',
        'nav': 'nav'
    }, inplace=True)
    
    df['nav_date'] = pd.to_datetime(df['nav_date'], errors='coerce')
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"), index=False)
    print("nav_history columns ready.")

def clean_investor_transactions():
    print("[*] Task 2: Cleaning investor transactions...")
    tx_file = os.path.join(RAW_DIR, "08_investor_transactions.csv") 
    
    if not os.path.exists(tx_file):
        print(f"[-] Missing target file at: {tx_file}")
        return
        
    df = pd.read_csv(tx_file)
    
    print(f"[+] Loaded raw transactions file. Headers found: {df.columns.tolist()}")
    
    df.rename(columns={
        'amfi_code': 'amfi_code',
        'transaction_date': 'transaction_date',
        'transaction_type': 'transaction_type',
        'amount': 'amount'
    }, inplace=True)
    
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    
    output_path = os.path.join(PROCESSED_DIR, "clean_transactions.csv")
    df.to_csv(output_path, index=False)
    print("Created clean_transactions.csv with real data contents!")
    
# Inside data_cleaning.py

def clean_scheme_performance():
    print("[*] Task: Cleaning fund performance metrics...")
    
    perf_file = os.path.join(RAW_DIR, "07_scheme_performance.csv") 
    
    if not os.path.exists(perf_file):
        print(f"[-] Performance file not found at: {perf_file}")
        return
        
    df = pd.read_csv(perf_file)
    print(f"[+] Loaded performance columns: {df.columns.tolist()}")
    
    df.rename(columns={
        'amfi_code': 'amfi_code',
        'expense_ratio': 'expense_ratio'
    }, inplace=True)
    
    output_path = os.path.join(PROCESSED_DIR, "clean_performance.csv")
    df.to_csv(output_path, index=False)
    print(" Created clean_performance.csv with filled datasets!")


def clean_fund_master():
    print("[*] Cleaning fund master...")
    
    master_file = os.path.join(RAW_DIR, "01_fund_master.csv") 
    
    if not os.path.exists(master_file):
        print(f"[-] Missing file: {master_file}")
        return
        
    df = pd.read_csv(master_file)
    
    df.rename(columns={
        'amfi_code': 'amfi_code',
        'fund_house': 'fund_house',
        'scheme_name': 'scheme_name',
        'category': 'category'
    }, inplace=True)
    df.rename(columns={'YOUR_RAW_CSV_HEADER_NAME': 'scheme_name'}, inplace=True)
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"), index=False)
    print(" Created clean_fund_master.csv with data!")
    
if __name__ == "__main__":
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_fund_master()
    