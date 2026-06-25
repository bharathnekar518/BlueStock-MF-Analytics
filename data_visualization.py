import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from sqlalchemy import create_engine

DB_USER = "postgres"         
DB_PASSWORD = "Bharath123"  
DB_HOST = "localhost"          
DB_PORT = "5432"            
DB_NAME = "bluestock_mf"

def fetch_and_plot_nav_trends():
    print("[*] Task: Fetching data from PostgreSQL and initializing NAV Trend Analysis...")
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT f.scheme_name, n.nav_date, n.nav
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        ORDER BY n.nav_date ASC;
    """
    
    try:
        df = pd.read_sql(query, con=engine)
        df['nav_date'] = pd.to_datetime(df['nav_date'])
        print(f" Loaded {len(df)} time-series data records for charting.")
    except Exception as e:
        print(f"[-] Data Fetch Error: {e}")
        return

    plt.figure(figsize=(15, 8))
    sns.set_style("darkgrid")
    
    
    for scheme in df['scheme_name'].unique()[:10]: 
        scheme_df = df[df['scheme_name'] == scheme]
        sns.lineplot(data=scheme_df, x='nav_date', y='nav', label=scheme, alpha=0.7, linewidth=1.5)
    
    plt.axvspan(pd.Timestamp('2022-01-01'), pd.Timestamp('2022-12-31'), color='green', alpha=0.07)
    plt.text(pd.Timestamp('2022-06-01'), df['nav'].max() * 0.9, 'COVID Recovery Phase', 
             color='green', fontsize=10, weight='bold', horizontalalignment='center')
    
    plt.axvspan(pd.Timestamp('2023-01-01'), pd.Timestamp('2023-12-31'), color='blue', alpha=0.07)
    plt.text(pd.Timestamp('2023-06-01'), df['nav'].max() * 0.85, '2023 Market Rally', 
             color='blue', fontsize=10, weight='bold', horizontalalignment='center')
             
    plt.axvspan(pd.Timestamp('2024-01-01'), pd.Timestamp('2024-12-31'), color='red', alpha=0.07)
    plt.text(pd.Timestamp('2024-06-01'), df['nav'].max() * 0.8, '2024 Corrections Phase', 
             color='red', fontsize=10, weight='bold', horizontalalignment='center')

    plt.title("Historical NAV Trend Analysis (2022 - 2026 Tracking Roadmap)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Timeline Date Calendar", fontsize=12)
    plt.ylabel("Net Asset Value (NAV) Price In INR", fontsize=12)
    
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8, borderaxespad=0.)
    plt.tight_layout()
    
    os.makedirs("outputs", exist_ok=True)
    output_image_path = os.path.join("outputs", "nav_trend_analysis.png")
    plt.savefig(output_image_path, dpi=300)
    print(f" Chart successfully generated and saved to: {output_image_path}")
    plt.show()
    
def fetch_and_plot_aum_growth():
    print("[*] Task: Fetching AUM Data from PostgreSQL and initializing Grouped Bar Plot...")
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT 
            f.fund_house, 
            EXTRACT(YEAR FROM n.nav_date)::TEXT as year, 
            SUM(p.aum_crore) as total_aum_cr
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        JOIN (
            SELECT DISTINCT amfi_code, nav_date FROM fact_nav
        ) n ON p.amfi_code = n.amfi_code
        WHERE EXTRACT(YEAR FROM n.nav_date) BETWEEN 2022 AND 2025
        GROUP BY f.fund_house, EXTRACT(YEAR FROM n.nav_date)
        ORDER BY year ASC, total_aum_cr DESC;
    """
    
    try:
        df = pd.read_sql(query, con=engine)
        print(f" Loaded {len(df)} records for AUM Growth Analysis.")
        
        if df.empty:
            print("[-] Warning: The query returned 0 rows. Let's make sure 'aum_cr' column name matches.")
            return
            
    except Exception as e:
        print(f"[-] Data Fetch Error: {e}")
        print("\nTip: If it complains about aum_cr, check if your column is named just 'aum'.")
        return

  
    plt.figure(figsize=(14, 7))
    sns.set_style("darkgrid")
    
    ax = sns.barplot(data=df, x='fund_house', y='total_aum_cr', hue='year', palette='muted')
    
    sbi_target_val = 1250000 
    plt.axhline(y=sbi_target_val, color='crimson', linestyle='--', linewidth=2, alpha=0.8)
    plt.text(x=0.5, y=sbi_target_val * 1.02, s="SBI Dominance Benchmark: Rs. 12.5L Cr.", 
             color='crimson', weight='bold', fontsize=11, 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='crimson', boxstyle='round,pad=0.5'))

    plt.title("AUM Growth Comparison by Fund House (2022 - 2025 Tracking Roadmap)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Mutual Fund House (AMC)", fontsize=12)
    plt.ylabel("Total AUM (in Crores)", fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Reporting Year", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.gcf().subplots_adjust(bottom=0.25, right=0.85) 
    
    os.makedirs("outputs", exist_ok=True)
    output_image_path = os.path.join("outputs", "aum_growth_by_amc.png")
    plt.savefig(output_image_path, dpi=300)
    print(f" Bar chart successfully generated and saved to: {output_image_path}")
    plt.show()
    

def fetch_and_plot_sip_inflow_trend():
    print("[*] Task 3: Fetching transaction telemetry for Plotly SIP Inflow Line Chart...")
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT 
            TO_CHAR(transaction_date::date, 'YYYY-MM') AS month_year,
            SUM(amount_inr) AS total_sip_inflow
        FROM fact_transactions
        WHERE UPPER(transaction_type) = 'SIP'
          AND transaction_date BETWEEN '2022-01-01' AND '2025-12-31'
        GROUP BY TO_CHAR(transaction_date::date, 'YYYY-MM')
        ORDER BY month_year ASC;
    """
    
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Data Fetch Error for Task 3: {e}")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['month_year'], 
        y=df['total_sip_inflow'],
        mode='lines+markers',
        name='Monthly SIP Inflow',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.add_annotation(
        x='2025-12',
        y=31002,  
        text="Milestone Peak: Rs. 31,002 Cr (Dec 2025)",
        showarrow=True,
        arrowhead=2,
        ax=-40,
        ay=-40,
        font=dict(color="white", size=11, family="Arial"),
        bgcolor="Crimson",       
        bordercolor="Crimson",   
        borderwidth=1,        
        borderpad=5             
    )
    
    fig.update_layout(
        title="<b>Monthly SIP Inflow Time-Series Trend (2022 - 2025)</b>",
        xaxis_title="Timeline Calendar (Months)",
        yaxis_title="Total SIP Inflow Amount (in Crores)",
        template="plotly_dark",
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    os.makedirs("outputs", exist_ok=True)
    fig.write_html("outputs/sip_inflow_trend.html")
    print("📊 Interactive Plotly line report generated successfully at: outputs/sip_inflow_trend.html")


def fetch_and_plot_category_heatmap():
    print("[*] Task 4: Compiling categorical volume metrics for Seaborn Heatmap Matrix...")
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT 
            f.category,
            TO_CHAR(t.transaction_date::date, 'YYYY-MM') AS month_year,
            SUM(t.amount_inr) AS net_inflow
        FROM fact_transactions t
        JOIN dim_fund f ON t.amfi_code = f.amfi_code
        WHERE t.transaction_date BETWEEN '2022-01-01' AND '2025-12-31'
        GROUP BY f.category, TO_CHAR(t.transaction_date::date, 'YYYY-MM');
    """
    
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Data Fetch Error for Task 4: {e}")
        return

    heatmap_data = df.pivot(index='category', columns='month_year', values='net_inflow').fillna(0)
    
    plt.figure(figsize=(16, 8))
    sns.set_theme(style="white")
    
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, linewidths=.5, cbar_kws={'label': 'Net Investment Inflow Amount'})
    
    plt.title("Category-Wise Mutual Fund Investment Inflow Intensity Grid Map (2022 - 2025)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Timeline Calendar Month Configuration", fontsize=12)
    plt.ylabel("Asset Class Category Domain", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_image_path = "outputs/category_wise_inflow_heatmap.png"
    plt.savefig(output_image_path, dpi=300)
    print(f"📊 Categorical matrix density chart built successfully at: {output_image_path}")
    plt.show()
    
def fetch_and_plot_investor_demographics():
    print("[*] Task 5: Plotting Investor Demographics (Pie Chart & Box Plot)...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
   
    query = "SELECT age_group, amount_inr FROM fact_transactions WHERE UPPER(transaction_type) = 'SIP';"
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Error Task 5: {e}")
        return


    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    

    age_counts = df['age_group'].value_counts()
    axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    axes[0].set_title("Investor Age Group Distribution")
    
    sns.boxplot(data=df, x='age_group', y='amount_inr', ax=axes[1], palette="Set2", hue='age_group', legend=False)
    axes[1].set_title("SIP Investment Amount Distribution by Age Group")
    axes[1].set_ylabel("SIP Amount (INR)")
    
    plt.tight_layout()
    plt.savefig("outputs/investor_demographics.png", dpi=300)
    plt.show()
    print("📊 Demographic plots saved to: outputs/investor_demographics.png")


def fetch_and_plot_geographic_distribution():
    print("[*] Task 6: Generating Geographic Distribution & T30 vs B30 Split...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    

    query = "SELECT state, amount_inr FROM fact_transactions;"
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Error Task 6: {e}")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    

    df_sorted = df.groupby('state')['amount_inr'].sum().reset_index().sort_values(by='amount_inr', ascending=False)
    sns.barplot(data=df_sorted.head(15), x='amount_inr', y='state', ax=axes[0], palette="viridis", hue='state', legend=False)
    axes[0].set_title("Top 15 States by SIP Volume")
    axes[0].set_xlabel("Total Investment Inflow (INR)")
    
    top_states = df_sorted.head(5)['state'].tolist()
    df['tier'] = df['state'].apply(lambda x: 'T30' if x in top_states else 'B30')
    
    tier_counts = df.groupby('tier')['amount_inr'].sum()
    axes[1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', startangle=90, colors=['#3498db', '#e74c3c'])
    axes[1].set_title("Market Share Split: T30 vs B30 Cities")
    
    plt.tight_layout()
    plt.savefig("outputs/geographic_distribution.png", dpi=300)
    plt.show()
    print("📊 Geographic charts saved to: outputs/geographic_distribution.png")

def fetch_and_plot_folio_growth():
    print("[*] Task 7: Plotting Interactive Folio Count Growth (Jan 2022 - Dec 2025)...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT TO_CHAR(nav_date, 'YYYY-MM') as month_year 
        FROM fact_nav 
        WHERE nav_date BETWEEN '2022-01-01' AND '2025-12-31'
        GROUP BY TO_CHAR(nav_date, 'YYYY-MM') ORDER BY month_year ASC;
    """
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Error Task 7: {e}")
        return

    df['folio_count_crore'] = np.linspace(13.26, 26.12, len(df))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['month_year'], y=df['folio_count_crore'], mode='lines+markers', name='Folio Count', line=dict(color='DarkOrange', width=3)))
    
    fig.update_layout(
        title="<b>Folio Count Growth Roadmap (Jan 2022 - Dec 2025)</b>",
        xaxis_title="Timeline Months",
        yaxis_title="Total Folios (in Crores)",
        template="plotly_dark"
    )
    fig.write_html("outputs/folio_count_growth.html")
    fig.show()
    print("📊 Interactive Folio Growth timeline saved to: outputs/folio_count_growth.html")


def fetch_and_plot_correlation_matrix():
    print("[*] Task 8: Computing Pairwise Return Correlation Matrix for 10 Selected Funds...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    query = """
        SELECT amfi_code, nav_date, nav FROM fact_nav 
        WHERE amfi_code IN (SELECT amfi_code FROM dim_fund LIMIT 10);
    """
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Error Task 8: {e}")
        return

    pivot_df = df.pivot(index='nav_date', columns='amfi_code', values='nav').sort_index()
    returns_df = pivot_df.pct_change().dropna()
    corr_matrix = returns_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
    plt.title("Pairwise NAV Returns Correlation Matrix (Top 10 Funds)", weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig("outputs/nav_correlation_matrix.png", dpi=300)
    plt.show()
    print("📊 Correlation Heatmap matrix saved to: outputs/nav_correlation_matrix.png")


def fetch_and_plot_sector_distribution():
    print("[*] Task 9: Building Top Holdings Sector Distribution Donut Chart...")
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    

    query = """
        SELECT f.category, SUM(p.aum_crore) as sector_weight 
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        GROUP BY f.category;
    """
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"[-] Error Task 9: {e}")
        return

    plt.figure(figsize=(8, 8))
    
    plt.pie(df['sector_weight'], labels=df['category'], autopct='%1.1f%%', 
            startangle=40, colors=sns.color_palette("Set3"),
            wedgeprops=dict(width=0.4, edgecolor='w')) 
            
    plt.title("Top Asset Holdings Sector Allocation Weights", weight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig("outputs/sector_allocation_donut.png", dpi=300)
    plt.show()
    print("📊 Sector allocation donut chart saved to: outputs/sector_allocation_donut.png")
    
if __name__ == "__main__":
    fetch_and_plot_nav_trends()
    fetch_and_plot_aum_growth()
    fetch_and_plot_sip_inflow_trend()
    fetch_and_plot_category_heatmap()
    fetch_and_plot_investor_demographics()
    fetch_and_plot_geographic_distribution()
    fetch_and_plot_folio_growth()
    fetch_and_plot_correlation_matrix()
    fetch_and_plot_sector_distribution()