
import os
import requests
import pandas as pd

def fetch_and_save_nav(scheme_code, fund_name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"[*] Fetching live NAV for {fund_name} (Code: {scheme_code})...")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[-] Failed to fetch code {scheme_code}. Status: {response.status_code}")
        return None
        
    response_json = response.json()
    
    if 'data' not in response_json or not response_json['data']:
        print(f"[-] No structural data found for code {scheme_code}.")
        return None
        
    nav_df = pd.DataFrame(response_json['data'])
    nav_df['scheme_code'] = scheme_code
    nav_df['fund_name'] = fund_name
    
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"nav_history_{scheme_code}.csv"
    output_path = os.path.join(output_dir, filename)
    nav_df.to_csv(output_path, index=False)
    print(f"✅ Saved raw history to: {output_path}")
    return nav_df

def run_live_pipeline():

    fetch_and_save_nav(125497, "HDFC Top 100 Direct")
    
    
    key_schemes = {
        119551: "SBI Bluechip",
        120503: "ICICI Bluechip",
        118632: "Nippon Large Cap",
        119092: "Axis Bluechip",
        120841: "Kotak Bluechip"
    }
    
    print("\n--- Starting Fetch for 5 Key Target Schemes ---")
    all_fetched_dfs = []
    for code, name in key_schemes.items():
        df = fetch_and_save_nav(code, name)
        if df is not None:
            all_fetched_dfs.append(df)

if __name__ == "__main__":
    run_live_pipeline()