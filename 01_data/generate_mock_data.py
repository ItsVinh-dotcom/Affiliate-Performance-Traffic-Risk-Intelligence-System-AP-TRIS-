"""
Mock Data Generator for Affiliate Performance & Risk Intelligence System (AP-TRIS)
Generates realistic, domain-specific datasets for:
- dim_publishers.csv
- dim_offers.csv
- fact_clicks.csv
- fact_conversions.csv
"""

import os
import csv
import random
from datetime import datetime, timedelta

# Set fixed seed for reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. GENERATE DIM_PUBLISHERS
# ---------------------------------------------------------
channels = ["TikTok Creator", "Facebook Media Buyer", "Google Ads Specialist", "SEO Content Hub", "Telegram/Zalo Community", "YouTube Reviewer"]
tiers = ["Bronze", "Silver", "Gold", "Platinum"]
tier_weights = [0.45, 0.30, 0.18, 0.07]

publishers = []
for i in range(1, 101):
    pub_id = f"PUB_{i:03d}"
    name = f"Affiliate_Partner_{i:03d}"
    channel = random.choice(channels)
    tier = random.choices(tiers, weights=tier_weights)[0]
    
    # Join date within last 12 months
    join_days_ago = random.randint(15, 365)
    join_date = (datetime(2026, 9, 30) - timedelta(days=join_days_ago)).strftime("%Y-%m-%d")
    
    # Quality status
    is_fraud_suspect = 1 if pub_id in ["PUB_042", "PUB_077", "PUB_091"] else 0
    status = "Flagged" if is_fraud_suspect else "Active"
    
    publishers.append({
        "publisher_id": pub_id,
        "publisher_name": name,
        "traffic_channel": channel,
        "tier": tier,
        "status": status,
        "join_date": join_date,
        "is_fraud_suspect": is_fraud_suspect
    })

with open(os.path.join(RAW_DIR, "dim_publishers.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(publishers[0].keys()))
    writer.writeheader()
    writer.writerows(publishers)

print(f"Generated {len(publishers)} publishers.")

# ---------------------------------------------------------
# 2. GENERATE DIM_OFFERS
# ---------------------------------------------------------
offers_data = [
    # Finance - Credit Cards & Banking (High payout, strict approval)
    ("OFF_FIN_01", "VPBank StepUp Credit Card", "Finance & Banking", "CPA", "VPBank", 420000, 310000, 0.58),
    ("OFF_FIN_02", "Techcombank eKYC Digital Account", "Finance & Banking", "CPA", "Techcombank", 130000, 95000, 0.75),
    ("OFF_FIN_03", "Cake by VPBank Digital Card", "Finance & Banking", "CPA", "Cake Digital", 145000, 105000, 0.72),
    ("OFF_FIN_04", "VIB Financial Super Card", "Finance & Banking", "CPA", "VIB Bank", 480000, 350000, 0.52),
    ("OFF_FIN_05", "MBBank App Open Account", "Finance & Banking", "CPA", "MBBank", 110000, 80000, 0.80),
    ("OFF_FIN_06", "Mirae Asset Easy Consumer Loan", "Finance & Banking", "CPL", "Mirae Asset", 290000, 210000, 0.45),
    ("OFF_FIN_07", "Shinhan Finance Personal Loan", "Finance & Banking", "CPL", "Shinhan Finance", 320000, 230000, 0.42),
    ("OFF_FIN_08", "TPBank EVO Credit Card", "Finance & Banking", "CPA", "TPBank", 400000, 290000, 0.55),
    
    # CPO - Beauty & Health (Medium payout, telesale confirmation)
    ("OFF_CPO_01", "GlowUp Whitening Serum", "Beauty & Cosmetics", "CPO", "Aura Dermacare", 310000, 220000, 0.68),
    ("OFF_CPO_02", "SlimFit Herbal Detox Capsule", "Health & Wellness", "CPO", "VitaHealth VN", 280000, 195000, 0.65),
    ("OFF_CPO_03", "K-Collagen Youth Booster", "Beauty & Cosmetics", "CPO", "Seoul Miracle", 330000, 240000, 0.70),
    ("OFF_CPO_04", "Cordyceps Natural Tonic", "Health & Wellness", "CPO", "BioPharm VN", 350000, 250000, 0.62),
    ("OFF_CPO_05", "AcneClear Rapid Treatment", "Beauty & Cosmetics", "CPO", "DermaLab", 260000, 180000, 0.66),

    # E-commerce & Others (CPS / CPI)
    ("OFF_CPS_01", "Shopee Mega Campaign Deals", "E-commerce", "CPS", "Shopee VN", 75000, 50000, 0.88),
    ("OFF_CPS_02", "TikTok Shop High Commission Picks", "E-commerce", "CPS", "TikTok Shop MCN", 90000, 65000, 0.85),
    ("OFF_CPI_01", "FinGo Personal Budgeting App", "Mobile Apps", "CPI", "FinTech Lab", 45000, 30000, 0.90)
]

offers = []
for item in offers_data:
    offers.append({
        "offer_id": item[0],
        "offer_name": item[1],
        "vertical": item[2],
        "payout_model": item[3],
        "advertiser_name": item[4],
        "advertiser_revenue_vnd": item[5],
        "publisher_payout_vnd": item[6],
        "expected_approval_rate": item[7]
    })

with open(os.path.join(RAW_DIR, "dim_offers.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(offers[0].keys()))
    writer.writeheader()
    writer.writerows(offers)

print(f"Generated {len(offers)} offers.")

# ---------------------------------------------------------
# 3. GENERATE FACT_CLICKS & FACT_CONVERSIONS
# ---------------------------------------------------------
start_date = datetime(2026, 8, 1, 0, 0, 0)
end_date = datetime(2026, 9, 30, 23, 59, 59)
total_seconds = int((end_date - start_date).total_seconds())

devices = ["Mobile", "Desktop", "Tablet"]
device_weights = [0.78, 0.18, 0.04]

clicks = []
conversions = []

click_counter = 100000
conv_counter = 50000

# High volume publishers
top_pubs = ["PUB_005", "PUB_012", "PUB_018", "PUB_024", "PUB_035"]
fraud_pubs = ["PUB_042", "PUB_077", "PUB_091"]
other_pubs = [p["publisher_id"] for p in publishers if p["publisher_id"] not in top_pubs and p["publisher_id"] not in fraud_pubs]

NUM_CLICKS = 22000

for _ in range(NUM_CLICKS):
    click_counter += 1
    click_id = f"CLK_{click_counter}"
    
    # Biased publisher distribution
    roll = random.random()
    if roll < 0.40:
        pub_id = random.choice(top_pubs)
    elif roll < 0.55:
        pub_id = random.choice(fraud_pubs)
    else:
        pub_id = random.choice(other_pubs)
        
    offer = random.choice(offers)
    offer_id = offer["offer_id"]
    
    # Timestamp
    rand_secs = random.randint(0, total_seconds)
    click_time = start_date + timedelta(seconds=rand_secs)
    
    # Device & IP
    device = random.choices(devices, weights=device_weights)[0]
    if pub_id in fraud_pubs:
        # Repeating IP pool for fraud
        ip = f"113.161.44.{random.randint(10, 15)}"
        device = "Desktop"
    else:
        ip = f"{random.randint(14, 222)}.{random.randint(10, 250)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
    clicks.append({
        "click_id": click_id,
        "click_time": click_time.strftime("%Y-%m-%d %H:%M:%S"),
        "publisher_id": pub_id,
        "offer_id": offer_id,
        "device_type": device,
        "user_ip": ip
    })
    
    # Conversion probability
    is_fraud = (pub_id in fraud_pubs)
    base_cr = 0.08 if is_fraud else 0.045
    
    if random.random() < base_cr:
        conv_counter += 1
        conv_id = f"CONV_{conv_counter}"
        
        # Time to convert: Fraud is < 3 seconds or exact duplicate; Normal is 30s to 45 mins
        if is_fraud:
            ttc_seconds = random.randint(1, 4) # Bot spike
        else:
            ttc_seconds = random.randint(25, 2700)
            
        conv_time = click_time + timedelta(seconds=ttc_seconds)
        
        # Approval status determination
        expected_approval = offer["expected_approval_rate"]
        
        if is_fraud:
            status = random.choices(["Rejected", "Fraud", "Approved"], weights=[0.60, 0.35, 0.05])[0]
            rejection_reason = random.choice(["Fake / Bot Traffic", "Duplicate Phone", "Invalid eKYC / OCR Failed"])
        else:
            if random.random() < expected_approval:
                status = "Approved"
                rejection_reason = "None"
            else:
                status = random.choice(["Rejected", "Pending"])
                if status == "Rejected":
                    rejection_reason = random.choice(["Bad Debt History (CIC)", "Customer Cancelled", "Invalid Lead Form", "Duplicate Phone"])
                else:
                    rejection_reason = "Under Review"

        # Financial values
        rev = offer["advertiser_revenue_vnd"] if status == "Approved" else 0
        payout = offer["publisher_payout_vnd"] if status == "Approved" else 0
        
        conversions.append({
            "conversion_id": conv_id,
            "click_id": click_id,
            "conversion_time": conv_time.strftime("%Y-%m-%d %H:%M:%S"),
            "publisher_id": pub_id,
            "offer_id": offer_id,
            "time_to_convert_seconds": ttc_seconds,
            "status": status,
            "rejection_reason": rejection_reason,
            "advertiser_revenue_vnd": rev,
            "publisher_payout_vnd": payout,
            "gross_margin_vnd": rev - payout
        })

# Sort by timestamp
clicks.sort(key=lambda x: x["click_time"])
conversions.sort(key=lambda x: x["conversion_time"])

with open(os.path.join(RAW_DIR, "fact_clicks.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(clicks[0].keys()))
    writer.writeheader()
    writer.writerows(clicks)

print(f"Generated {len(clicks)} clicks.")

with open(os.path.join(RAW_DIR, "fact_conversions.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(conversions[0].keys()))
    writer.writeheader()
    writer.writerows(conversions)

print(f"Generated {len(conversions)} conversions.")
print(f"Mock data generation completed in {RAW_DIR}")
