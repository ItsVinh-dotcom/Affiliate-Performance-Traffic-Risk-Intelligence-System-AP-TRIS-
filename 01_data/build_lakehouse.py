"""
Medallion Lakehouse Architecture Builder (Bronze -> Silver -> Gold + Exports)
Project: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)

Strict Architecture Rules:
- Core Storage (lakehouse/): 100% Columnar Format (Parquet)
- Business Delivery (exports/): CSV only for Accounting & Advertiser Reconciliation
"""

import os
import time
import gzip
import csv
import pandas as pd
import numpy as np

def build_lakehouse():
    start_time = time.time()
    print("=" * 70)
    print(">> BUILDING MEDALLION DATA LAKEHOUSE (BRONZE - SILVER - GOLD)")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "01_data")
    
    bronze_dir = os.path.join(data_dir, "lakehouse", "bronze")
    silver_dir = os.path.join(data_dir, "lakehouse", "silver")
    gold_dir = os.path.join(data_dir, "lakehouse", "gold")
    exports_dir = os.path.join(data_dir, "exports")

    for d in [bronze_dir, silver_dir, gold_dir, exports_dir]:
        os.makedirs(d, exist_ok=True)

    raw_dir = os.path.join(data_dir, "raw")

    # Check parquet capability
    has_parquet = False
    try:
        import pyarrow
        has_parquet = True
    except ImportError:
        try:
            import fastparquet
            has_parquet = True
        except ImportError:
            has_parquet = False

    print(f"Parquet Engine Detected: {'YES (pyarrow/fastparquet)' if has_parquet else 'NO (falling back to compressed storage until pyarrow installs)'}")

    # -------------------------------------------------------------
    # 1. BRONZE LAYER: Raw Ingestion of 1M Clicks & 49K Conversions
    # -------------------------------------------------------------
    print("\n[Layer 1: BRONZE] Organizing Raw Ingestion...")
    clicks_src = os.path.join(raw_dir, "fact_clicks.csv.gz")
    convs_src = os.path.join(raw_dir, "fact_conversions.csv")

    if os.path.exists(clicks_src):
        # Read clicks and write to bronze
        print("-> Ingesting 1,000,000 clicks into Bronze...")
        df_clicks = pd.read_csv(clicks_src, compression="gzip")
        if has_parquet:
            bronze_clicks = os.path.join(bronze_dir, "fact_clicks.parquet")
            df_clicks.to_parquet(bronze_clicks, compression="snappy", index=False)
            print(f"   [OK] fact_clicks.parquet ({len(df_clicks):,} rows, {os.path.getsize(bronze_clicks)/(1024*1024):.2f} MB)")
        else:
            bronze_clicks = os.path.join(bronze_dir, "fact_clicks.csv.gz")
            df_clicks.to_csv(bronze_clicks, compression="gzip", index=False)
            print(f"   [OK] fact_clicks.csv.gz ({len(df_clicks):,} rows, {os.path.getsize(bronze_clicks)/(1024*1024):.2f} MB)")

    if os.path.exists(convs_src):
        print("-> Ingesting 49,006 conversions into Bronze...")
        df_convs = pd.read_csv(convs_src)
        if has_parquet:
            bronze_convs = os.path.join(bronze_dir, "fact_conversions.parquet")
            df_convs.to_parquet(bronze_convs, compression="snappy", index=False)
            print(f"   [OK] fact_conversions.parquet ({len(df_convs):,} rows, {os.path.getsize(bronze_convs)/(1024*1024):.2f} MB)")
        else:
            bronze_convs = os.path.join(bronze_dir, "fact_conversions.csv.gz")
            df_convs.to_csv(bronze_convs, compression="gzip", index=False)
            print(f"   [OK] fact_conversions.csv.gz ({len(df_convs):,} rows, {os.path.getsize(bronze_convs)/(1024*1024):.2f} MB)")

    # -------------------------------------------------------------
    # 2. SILVER LAYER: Cleansed Dimensions & Enriched Facts
    # -------------------------------------------------------------
    print("\n[Layer 2: SILVER] Transforming Cleansed Dimensions & Facts...")
    pubs_src = os.path.join(raw_dir, "dim_publishers.csv")
    offers_src = os.path.join(raw_dir, "dim_offers.csv")

    df_pubs = pd.read_csv(pubs_src)
    df_offers = pd.read_csv(offers_src)

    # Silver enrichment: Join offer metadata onto conversions for faster analytical querying
    df_silver_convs = df_convs.merge(
        df_offers[["offer_id", "offer_name", "vertical", "payout_model", "advertiser_name"]], 
        on="offer_id", 
        how="left"
    )

    if has_parquet:
        df_pubs.to_parquet(os.path.join(silver_dir, "dim_publishers.parquet"), compression="snappy", index=False)
        df_offers.to_parquet(os.path.join(silver_dir, "dim_offers.parquet"), compression="snappy", index=False)
        df_silver_convs.to_parquet(os.path.join(silver_dir, "fact_conversions_cleansed.parquet"), compression="snappy", index=False)
        print("   [OK] dim_publishers.parquet")
        print("   [OK] dim_offers.parquet")
        print("   [OK] fact_conversions_cleansed.parquet (Enriched with Advertiser metadata)")
    else:
        df_pubs.to_csv(os.path.join(silver_dir, "dim_publishers.csv.gz"), compression="gzip", index=False)
        df_offers.to_csv(os.path.join(silver_dir, "dim_offers.csv.gz"), compression="gzip", index=False)
        df_silver_convs.to_csv(os.path.join(silver_dir, "fact_conversions_cleansed.csv.gz"), compression="gzip", index=False)
        print("   [OK] Silver tables compressed and stored.")

    # -------------------------------------------------------------
    # 3. GOLD LAYER: Curated Analytics Marts for Power BI & BI Tools
    # -------------------------------------------------------------
    print("\n[Layer 3: GOLD] Aggregating Analytical Data Marts...")
    
    # Mart 1: Daily Campaign KPI Mart
    df_convs["date"] = pd.to_datetime(df_convs["conversion_time"]).dt.strftime("%Y-%m-%d")
    gold_daily = df_convs.groupby(["date", "offer_id"]).agg(
        total_conversions=("conversion_id", "count"),
        approved_conversions=("status", lambda x: (x == "Approved").sum()),
        rejected_conversions=("status", lambda x: x.isin(["Rejected", "Fraud"]).sum()),
        bot_leads=("time_to_convert_seconds", lambda x: (x < 5).sum()),
        gross_revenue_vnd=("advertiser_revenue_vnd", "sum"),
        publisher_payout_vnd=("publisher_payout_vnd", "sum"),
        gross_margin_vnd=("gross_margin_vnd", "sum")
    ).reset_index()
    gold_daily["approval_rate_pct"] = np.round(gold_daily["approved_conversions"] / gold_daily["total_conversions"] * 100, 2)

    # Mart 2: Publisher Fraud Risk Intelligence Mart
    gold_risk = df_convs.groupby("publisher_id").agg(
        total_leads=("conversion_id", "count"),
        approved_leads=("status", lambda x: (x == "Approved").sum()),
        bot_leads_under_5s=("time_to_convert_seconds", lambda x: (x < 5).sum()),
        total_margin_vnd=("gross_margin_vnd", "sum")
    ).reset_index()
    gold_risk["approval_rate_pct"] = np.round(gold_risk["approved_leads"] / gold_risk["total_leads"] * 100, 2)
    gold_risk["risk_tier"] = np.where(
        gold_risk["bot_leads_under_5s"] >= 100, "CRITICAL: BOT ATTACK",
        np.where((gold_risk["total_leads"] >= 50) & (gold_risk["approval_rate_pct"] < 15), "WARNING: LOW QUALITY SPAM", "NORMAL")
    )

    if has_parquet:
        gold_daily.to_parquet(os.path.join(gold_dir, "daily_campaign_kpi.parquet"), compression="snappy", index=False)
        gold_risk.to_parquet(os.path.join(gold_dir, "publisher_risk_scoring.parquet"), compression="snappy", index=False)
        print("   [OK] daily_campaign_kpi.parquet (Direct ingestion source for Power BI)")
        print("   [OK] publisher_risk_scoring.parquet (Risk Intelligence Mart)")
    else:
        gold_daily.to_csv(os.path.join(gold_dir, "daily_campaign_kpi.csv.gz"), compression="gzip", index=False)
        gold_risk.to_csv(os.path.join(gold_dir, "publisher_risk_scoring.csv.gz"), compression="gzip", index=False)
        print("   [OK] Gold Marts compressed and stored.")

    # -------------------------------------------------------------
    # 4. EXPORTS LAYER: The ONLY place for Business CSVs
    # -------------------------------------------------------------
    print("\n[Layer 4: EXPORTS] Generating Business-Facing CSV Deliverables...")
    
    # Export 1: Accounting Monthly Payout Report (Thanh toán hoa hồng cho kế toán)
    pub_payouts = df_convs[df_convs["status"] == "Approved"].groupby("publisher_id")["publisher_payout_vnd"].sum().reset_index()
    df_accounting = df_pubs.merge(pub_payouts, on="publisher_id", how="left").fillna(0)
    df_accounting["gross_payout_vnd"] = df_accounting["publisher_payout_vnd"]
    df_accounting["pit_tax_withholding_10pct_vnd"] = np.where(df_accounting["gross_payout_vnd"] >= 2000000, df_accounting["gross_payout_vnd"] * 0.10, 0)
    df_accounting["net_payable_vnd"] = df_accounting["gross_payout_vnd"] - df_accounting["pit_tax_withholding_10pct_vnd"]
    df_accounting["payment_status"] = np.where(df_accounting["status"] == "Flagged", "HOLD (FRAUD AUDIT)", "READY TO PAY")
    
    accounting_file = os.path.join(exports_dir, "accounting_monthly_payout.csv")
    df_accounting[["publisher_id", "publisher_name", "tier", "traffic_channel", "gross_payout_vnd", "pit_tax_withholding_10pct_vnd", "net_payable_vnd", "payment_status"]].to_csv(accounting_file, index=False, encoding="utf-8")
    print(f"   [OK] accounting_monthly_payout.csv ({len(df_accounting)} rows) -> For Finance & Accounting")

    # Export 2: Advertiser Reconciliation Sample (Đối soát ngân hàng)
    recon_sample = df_silver_convs[df_silver_convs["vertical"] == "Finance & Banking"][
        ["conversion_id", "conversion_time", "offer_name", "advertiser_name", "status", "rejection_reason", "advertiser_revenue_vnd"]
    ].head(500)
    recon_file = os.path.join(exports_dir, "advertiser_reconciliation_sample.csv")
    recon_sample.to_csv(recon_file, index=False, encoding="utf-8")
    print(f"   [OK] advertiser_reconciliation_sample.csv ({len(recon_sample)} rows) -> For Bank Reconciliation")

    print("\n" + "=" * 70)
    print(f">> MEDALLION LAKEHOUSE COMPLETED IN {time.time() - start_time:.2f}s!")
    print("Core Data Lakehouse (100% Parquet/Compressed): 01_data/lakehouse/ (Bronze, Silver, Gold)")
    print("Business CSV Exports (Finance & Partners)   : 01_data/exports/")
    print("=" * 70)

if __name__ == "__main__":
    build_lakehouse()
