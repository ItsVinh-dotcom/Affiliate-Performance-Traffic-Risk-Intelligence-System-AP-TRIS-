"""
Big Data Generator: 1,000,000 Clicks & ~48,000 Conversions
Project: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)

Generates:
1. dim_publishers.csv (250 publishers across 6 traffic channels and 4 tiers)
2. dim_offers.csv (25 campaigns in Finance & Banking CPA/CPL, CPO, and E-commerce)
3. fact_clicks.parquet (or fact_clicks.csv.gz if pyarrow not yet installed) -> 1,000,000 rows
4. fact_conversions.parquet (or fact_conversions.csv.gz) -> ~48,000 rows
5. fact_conversions.csv (convenient for Excel & Power BI direct import)
"""

import os
import time
import gzip
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def run_big_data_generation():
    start_time = time.time()
    print("=" * 65)
    print(">> AP-TRIS BIG DATA GENERATOR (1,000,000 ROWS)")
    print("=" * 65)

    # Check for parquet engine
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

    raw_dir = os.path.dirname(os.path.abspath(__file__))
    # Handle if run from 01_data or root
    if not os.path.basename(raw_dir) == "raw":
        raw_dir = os.path.join(raw_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    np.random.seed(42)

    # 1. GENERATE DIM_PUBLISHERS (250 Publishers)
    print("\n[1/4] Generating dim_publishers.csv (250 rows)...")
    channels = ["TikTok Creator", "Facebook Media Buyer", "Google Ads Specialist", "SEO Content Hub", "Telegram/Zalo Community", "YouTube Reviewer"]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    tier_probs = [0.45, 0.30, 0.18, 0.07]
    pub_ids = [f"PUB_{i:03d}" for i in range(1, 251)]
    fraud_pubs = ["PUB_042", "PUB_077", "PUB_091", "PUB_142", "PUB_188"]

    publishers_data = []
    base_join_date = datetime(2026, 9, 30)
    for pid in pub_ids:
        channel = np.random.choice(channels)
        tier = np.random.choice(tiers, p=tier_probs)
        days_ago = np.random.randint(15, 365)
        join_date = (base_join_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        is_fraud = 1 if pid in fraud_pubs else 0
        status = "Flagged" if is_fraud else "Active"
        publishers_data.append({
            "publisher_id": pid,
            "publisher_name": f"Affiliate_Partner_{pid}",
            "traffic_channel": channel,
            "tier": tier,
            "status": status,
            "join_date": join_date,
            "is_fraud_suspect": is_fraud
        })
    df_publishers = pd.DataFrame(publishers_data)
    df_publishers.to_csv(os.path.join(raw_dir, "dim_publishers.csv"), index=False, encoding="utf-8")
    print(f"-> Saved dim_publishers.csv")

    # 2. GENERATE DIM_OFFERS (25 Offers)
    print("\n[2/4] Generating dim_offers.csv (25 rows)...")
    offers_raw = [
        ("OFF_FIN_01", "VPBank StepUp Credit Card", "Finance & Banking", "CPA", "VPBank", 420000, 310000, 0.58),
        ("OFF_FIN_02", "Techcombank eKYC Digital Account", "Finance & Banking", "CPA", "Techcombank", 130000, 95000, 0.75),
        ("OFF_FIN_03", "Cake by VPBank Digital Card", "Finance & Banking", "CPA", "Cake Digital", 145000, 105000, 0.72),
        ("OFF_FIN_04", "VIB Financial Super Card", "Finance & Banking", "CPA", "VIB Bank", 480000, 350000, 0.52),
        ("OFF_FIN_05", "MBBank App Open Account", "Finance & Banking", "CPA", "MBBank", 110000, 80000, 0.80),
        ("OFF_FIN_06", "Mirae Asset Easy Consumer Loan", "Finance & Banking", "CPL", "Mirae Asset", 290000, 210000, 0.45),
        ("OFF_FIN_07", "Shinhan Finance Personal Loan", "Finance & Banking", "CPL", "Shinhan Finance", 320000, 230000, 0.42),
        ("OFF_FIN_08", "TPBank EVO Credit Card", "Finance & Banking", "CPA", "TPBank", 400000, 290000, 0.55),
        ("OFF_FIN_09", "OCB OMNI Digital Banking", "Finance & Banking", "CPA", "OCB Bank", 125000, 90000, 0.73),
        ("OFF_FIN_10", "HD SAISON Fast Cash Loan", "Finance & Banking", "CPL", "HD SAISON", 270000, 195000, 0.48),
        ("OFF_CPO_01", "GlowUp Whitening Serum", "Beauty & Cosmetics", "CPO", "Aura Dermacare", 310000, 220000, 0.68),
        ("OFF_CPO_02", "SlimFit Herbal Detox Capsule", "Health & Wellness", "CPO", "VitaHealth VN", 280000, 195000, 0.65),
        ("OFF_CPO_03", "K-Collagen Youth Booster", "Beauty & Cosmetics", "CPO", "Seoul Miracle", 330000, 240000, 0.70),
        ("OFF_CPO_04", "Cordyceps Natural Tonic", "Health & Wellness", "CPO", "BioPharm VN", 350000, 250000, 0.62),
        ("OFF_CPO_05", "AcneClear Rapid Treatment", "Beauty & Cosmetics", "CPO", "DermaLab", 260000, 180000, 0.66),
        ("OFF_CPO_06", "NanoCurcumin Stomach Care", "Health & Wellness", "CPO", "DungPharma", 295000, 210000, 0.64),
        ("OFF_CPO_07", "Ginseng Gold Energy Booster", "Health & Wellness", "CPO", "Korea Ginseng", 380000, 275000, 0.60),
        ("OFF_CPS_01", "Shopee Mega Campaign Deals", "E-commerce", "CPS", "Shopee VN", 75000, 50000, 0.88),
        ("OFF_CPS_02", "TikTok Shop High Commission Picks", "E-commerce", "CPS", "TikTok Shop MCN", 90000, 65000, 0.85),
        ("OFF_CPS_03", "Lazada Super Brand Day", "E-commerce", "CPS", "Lazada VN", 80000, 55000, 0.86),
        ("OFF_CPS_04", "TikiNOW Fast Delivery Tech", "E-commerce", "CPS", "Tiki VN", 65000, 45000, 0.89),
        ("OFF_CPI_01", "FinGo Personal Budgeting App", "Mobile Apps", "CPI", "FinTech Lab", 45000, 30000, 0.90),
        ("OFF_CPI_02", "CryptoWallet SafePay App", "Mobile Apps", "CPI", "BlockTech", 85000, 60000, 0.78),
        ("OFF_CPI_03", "EnglishMaster AI Learning App", "Education", "CPI", "EdTech Global", 55000, 38000, 0.85),
        ("OFF_CPI_04", "FitPro Workout & Diet Coach", "Mobile Apps", "CPI", "FitTech VN", 50000, 35000, 0.88)
    ]
    df_offers = pd.DataFrame(offers_raw, columns=[
        "offer_id", "offer_name", "vertical", "payout_model", "advertiser_name", 
        "advertiser_revenue_vnd", "publisher_payout_vnd", "expected_approval_rate"
    ])
    df_offers.to_csv(os.path.join(raw_dir, "dim_offers.csv"), index=False, encoding="utf-8")
    print(f"-> Saved dim_offers.csv")

    # 3. VECTORIZED GENERATION OF 1,000,000 CLICKS
    N_CLICKS = 1_000_000
    print(f"\n[3/4] Vectorizing and generating {N_CLICKS:,} clicks...")
    t0 = time.time()

    top_pubs = [f"PUB_{i:03d}" for i in range(1, 11)]
    other_pubs = [p for p in pub_ids if p not in top_pubs and p not in fraud_pubs]

    probs = np.zeros(len(pub_ids))
    for i, pid in enumerate(pub_ids):
        if pid in top_pubs:
            probs[i] = 0.35 / len(top_pubs)
        elif pid in fraud_pubs:
            probs[i] = 0.12 / len(fraud_pubs)
        else:
            probs[i] = 0.53 / len(other_pubs)
    probs /= probs.sum()

    click_pubs = np.random.choice(pub_ids, size=N_CLICKS, p=probs)
    offer_ids = df_offers["offer_id"].values
    click_offers = np.random.choice(offer_ids, size=N_CLICKS)

    start_ts = int(datetime(2026, 8, 1, 0, 0, 0).timestamp())
    end_ts = int(datetime(2026, 9, 30, 23, 59, 59).timestamp())
    rand_timestamps = np.random.randint(start_ts, end_ts, size=N_CLICKS)

    devices = np.random.choice(["Mobile", "Desktop", "Tablet"], size=N_CLICKS, p=[0.78, 0.18, 0.04])
    ip_blocks = np.random.randint(14, 222, size=(N_CLICKS, 4))
    ips = [f"{b[0]}.{b[1]}.{b[2]}.{b[3]}" for b in ip_blocks]

    fraud_mask = np.isin(click_pubs, fraud_pubs)
    fraud_indices = np.where(fraud_mask)[0]
    for idx in fraud_indices:
        ips[idx] = f"113.161.44.{np.random.randint(10, 16)}"
        devices[idx] = "Desktop"

    click_times = pd.to_datetime(rand_timestamps, unit="s")

    df_clicks = pd.DataFrame({
        "click_id": [f"CLK_{10000000 + i}" for i in range(N_CLICKS)],
        "click_time": click_times,
        "publisher_id": click_pubs,
        "offer_id": click_offers,
        "device_type": devices,
        "user_ip": ips
    })
    df_clicks.sort_values(by="click_time", inplace=True)
    df_clicks.reset_index(drop=True, inplace=True)

    if has_parquet:
        parquet_clicks_path = os.path.join(raw_dir, "fact_clicks.parquet")
        print("Saving to fact_clicks.parquet...")
        df_clicks.to_parquet(parquet_clicks_path, compression="snappy", index=False)
        print(f"-> Saved fact_clicks.parquet ({os.path.getsize(parquet_clicks_path)/(1024*1024):.2f} MB)")
    else:
        # Save as compressed gzip CSV (industry standard alternative to Parquet)
        gz_clicks_path = os.path.join(raw_dir, "fact_clicks.csv.gz")
        print("Saving to compressed fact_clicks.csv.gz (gzip)...")
        df_clicks.to_csv(gz_clicks_path, index=False, compression="gzip", encoding="utf-8")
        print(f"-> Saved fact_clicks.csv.gz ({os.path.getsize(gz_clicks_path)/(1024*1024):.2f} MB)")

    print(f"Generation of 1M clicks finished in {time.time() - t0:.2f}s.")

    # 4. GENERATE ~48,000 CONVERSIONS
    print("\n[4/4] Generating ~48,000 conversions...")
    t1 = time.time()

    conv_prob = np.where(fraud_mask, 0.075, 0.045)
    is_converted = np.random.random(N_CLICKS) < conv_prob
    conv_indices = np.where(is_converted)[0]
    n_convs = len(conv_indices)

    df_conv_clicks = df_clicks.iloc[conv_indices].copy()
    offer_lookup = df_offers.set_index("offer_id").to_dict("index")

    ttc_seconds = np.zeros(n_convs, dtype=int)
    statuses = []
    reasons = []
    revenues = []
    payouts = []
    margins = []

    fraud_conv_mask = np.isin(df_conv_clicks["publisher_id"].values, fraud_pubs)
    rejection_reasons_normal = ["Bad Debt History (CIC)", "Customer Cancelled", "Invalid Lead Form", "Duplicate Phone", "Under Review"]
    rejection_reasons_fraud = ["Fake / Bot Traffic", "Duplicate Phone", "Invalid eKYC / OCR Failed"]

    for i in range(n_convs):
        is_fraud = fraud_conv_mask[i]
        off_id = df_conv_clicks["offer_id"].iloc[i]
        off_info = offer_lookup[off_id]
        exp_approval = off_info["expected_approval_rate"]

        if is_fraud:
            ttc = np.random.randint(1, 4)
            status = np.random.choice(["Rejected", "Fraud", "Approved"], p=[0.65, 0.30, 0.05])
            reason = np.random.choice(rejection_reasons_fraud)
        else:
            ttc = np.random.randint(25, 2700)
            if np.random.random() < exp_approval:
                status = "Approved"
                reason = "None"
            else:
                status = np.random.choice(["Rejected", "Pending"], p=[0.75, 0.25])
                reason = np.random.choice(rejection_reasons_normal)

        ttc_seconds[i] = ttc
        statuses.append(status)
        reasons.append(reason)

        rev = off_info["advertiser_revenue_vnd"] if status == "Approved" else 0.0
        payout = off_info["publisher_payout_vnd"] if status == "Approved" else 0.0
        revenues.append(rev)
        payouts.append(payout)
        margins.append(rev - payout)

    conv_times = df_conv_clicks["click_time"] + pd.to_timedelta(ttc_seconds, unit="s")

    df_conversions = pd.DataFrame({
        "conversion_id": [f"CONV_{5000000 + i}" for i in range(n_convs)],
        "click_id": df_conv_clicks["click_id"].values,
        "conversion_time": conv_times,
        "publisher_id": df_conv_clicks["publisher_id"].values,
        "offer_id": df_conv_clicks["offer_id"].values,
        "time_to_convert_seconds": ttc_seconds,
        "status": statuses,
        "rejection_reason": reasons,
        "advertiser_revenue_vnd": revenues,
        "publisher_payout_vnd": payouts,
        "gross_margin_vnd": margins
    })
    df_conversions.sort_values(by="conversion_time", inplace=True)
    df_conversions.reset_index(drop=True, inplace=True)

    # Save conversions in CSV (for Excel/Power BI direct usage)
    csv_conv_path = os.path.join(raw_dir, "fact_conversions.csv")
    df_conversions.to_csv(csv_conv_path, index=False, encoding="utf-8")
    print(f"-> Saved fact_conversions.csv ({len(df_conversions):,} rows, {os.path.getsize(csv_conv_path)/(1024*1024):.2f} MB)")

    if has_parquet:
        parquet_conv_path = os.path.join(raw_dir, "fact_conversions.parquet")
        df_conversions.to_parquet(parquet_conv_path, compression="snappy", index=False)
        print(f"-> Saved fact_conversions.parquet ({os.path.getsize(parquet_conv_path)/(1024*1024):.2f} MB)")

    print("\n" + "=" * 65)
    print(f">> 1,000,000 ROW BIG DATA GENERATION COMPLETED IN {time.time() - start_time:.2f}s!")
    print(f"Clicks File: {'fact_clicks.parquet' if has_parquet else 'fact_clicks.csv.gz'}")
    print(f"Conversions File: fact_conversions.csv & {'fact_conversions.parquet' if has_parquet else 'fact_conversions.csv'}")
    print("=" * 65)

if __name__ == "__main__":
    run_big_data_generation()
