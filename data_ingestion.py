# data_ingestion.py
import os
import glob
import pandas as pd

def profile_provided_datasets():
    print("=========================================")
    # Look inside data/raw/ for any CSV files you pasted
    raw_dir = os.path.join("data", "raw")
    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    
    if not csv_files:
        print("[-] No CSV files found in data/raw/. Please ensure they are placed there.")
        return

    print(f"[+] Found {len(csv_files)} datasets to profile.\n")

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        print(f"--- Profiling Dataset: {filename} ---")
        
        # Load dataset
        df = pd.read_csv(file_path)
        
        # 1. Print Shape
        print(f"Shape (Rows, Columns): {df.shape}")
        
        # 2. Print Data Types
        print("\nData Types (.dtypes):")
        print(df.dtypes)
        
        # 3. Print Head
        print("\nFirst 5 Rows (.head()):")
        print(df.head(5))
        
        # 4. Note Anomalies / Quality Checks
        print("\n--- Data Quality & Anomalies Report ---")
        missing_values = df.isnull().sum()
        has_missing = missing_values.any()
        
        if has_missing:
            print("⚠️ Anomalies Detected: Found missing (null) values:")
            print(missing_values[missing_values > 0])
        else:
            print("✅ Clean Data: No missing values detected in this file.")
            
        # Check for duplicated primary keys if schemeCode column exists
        scheme_code_col = [col for col in df.columns if 'scheme' in col.lower() and 'code' in col.lower()]
        if scheme_code_col:
            dupes = df.duplicated(subset=[scheme_code_col[0]]).sum()
            if dupes > 0:
                print(f"⚠️ Duplicate Check: Found {dupes} duplicate codes in column '{scheme_code_col[0]}'")
        
        print("="*50 + "\n")

if __name__ == "__main__":
    profile_provided_datasets()