
import os
import glob

def verify_and_extract_summary():
    print("=== ETL Layer 1: Data Extraction & Environment Check ===")
    

    raw_dir = os.path.join("data", "raw")
    
    
    if not os.path.exists(raw_dir):
        print(f"[-] Critical Error: The directory '{raw_dir}' is missing.")
        print("[*] Action: Please run your folder creation commands or recreate the directory.")
        return
        
    print(f"[+] Active workspace verified at: {raw_dir}/")
    
    
    all_files = os.listdir(raw_dir)
    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    
    print(f"[+] Total individual tracking files found: {len(all_files)}")
    print(f"[+] Total validated CSV datasets: {len(csv_files)}")
    
    if len(csv_files) == 0:
        print(" Warning: No CSV data assets found. Ensure files are dragged into data/raw/")
    else:
        print(" Success: Extraction layer clear. Data is fully staged for ingestion.")
    print("=======================================================")

if __name__ == "__main__":
    verify_and_extract_summary()