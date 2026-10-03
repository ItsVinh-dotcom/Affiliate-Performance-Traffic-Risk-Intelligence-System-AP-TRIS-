"""
Database Builder & Virtual Data Server Generator for AP-TRIS
Builds:
1. SQLite Database (01_data/ap_tris.db)
2. DuckDB High-Performance Analytical Database (01_data/ap_tris.duckdb)

Allows Power BI to query data directly via ODBC/SQLite/DuckDB or Direct File Connection.
"""

import os
import csv
import gzip
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "01_data")
LAKEHOUSE_DIR = os.path.join(DATA_DIR, "lakehouse")

DB_PATH = os.path.join(DATA_DIR, "ap_tris.db")
DUCKDB_PATH = os.path.join(DATA_DIR, "ap_tris.duckdb")

def load_csv_gz(filepath):
    if not os.path.exists(filepath):
        return []
    rows = []
    with gzip.open(filepath, mode="rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def build_sqlite():
    print(f">> Building SQLite Database at: {DB_PATH}")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. dim_publishers
    pubs = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "silver", "dim_publishers.csv.gz"))
    if pubs:
        cursor.execute("""
            CREATE TABLE dim_publishers (
                publisher_id TEXT PRIMARY KEY,
                publisher_name TEXT,
                traffic_channel TEXT,
                tier TEXT,
                status TEXT,
                join_date TEXT,
                is_fraud_suspect INTEGER
            )
        """)
        cursor.executemany("""
            INSERT INTO dim_publishers VALUES (:publisher_id, :publisher_name, :traffic_channel, :tier, :status, :join_date, :is_fraud_suspect)
        """, pubs)
        print(f"   [SQLite] Loaded {len(pubs)} publishers")

    # 2. dim_offers
    offers = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "silver", "dim_offers.csv.gz"))
    if offers:
        cursor.execute("""
            CREATE TABLE dim_offers (
                offer_id TEXT PRIMARY KEY,
                offer_name TEXT,
                vertical TEXT,
                payout_model TEXT,
                advertiser_name TEXT,
                advertiser_revenue_vnd REAL,
                publisher_payout_vnd REAL,
                expected_approval_rate REAL
            )
        """)
        cursor.executemany("""
            INSERT INTO dim_offers VALUES (:offer_id, :offer_name, :vertical, :payout_model, :advertiser_name, :advertiser_revenue_vnd, :publisher_payout_vnd, :expected_approval_rate)
        """, offers)
        print(f"   [SQLite] Loaded {len(offers)} offers")

    # 3. fact_clicks
    clicks = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "bronze", "fact_clicks.csv.gz"))
    if clicks:
        cursor.execute("""
            CREATE TABLE fact_clicks (
                click_id TEXT PRIMARY KEY,
                click_time TEXT,
                publisher_id TEXT,
                offer_id TEXT,
                device_type TEXT,
                user_ip TEXT
            )
        """)
        cursor.executemany("""
            INSERT INTO fact_clicks VALUES (:click_id, :click_time, :publisher_id, :offer_id, :device_type, :user_ip)
        """, clicks)
        print(f"   [SQLite] Loaded {len(clicks)} clicks")

    # 4. fact_conversions
    convs = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "silver", "fact_conversions_cleansed.csv.gz"))
    if not convs:
        convs = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "bronze", "fact_conversions.csv.gz"))
    if convs:
        cursor.execute("""
            CREATE TABLE fact_conversions (
                conversion_id TEXT PRIMARY KEY,
                click_id TEXT,
                conversion_time TEXT,
                publisher_id TEXT,
                offer_id TEXT,
                time_to_convert_seconds INTEGER,
                status TEXT,
                rejection_reason TEXT,
                advertiser_revenue_vnd REAL,
                publisher_payout_vnd REAL,
                gross_margin_vnd REAL
            )
        """)
        # Filter keys to match schema
        clean_convs = []
        for c in convs:
            clean_convs.append({
                "conversion_id": c.get("conversion_id"),
                "click_id": c.get("click_id"),
                "conversion_time": c.get("conversion_time"),
                "publisher_id": c.get("publisher_id"),
                "offer_id": c.get("offer_id"),
                "time_to_convert_seconds": c.get("time_to_convert_seconds"),
                "status": c.get("status"),
                "rejection_reason": c.get("rejection_reason"),
                "advertiser_revenue_vnd": c.get("advertiser_revenue_vnd"),
                "publisher_payout_vnd": c.get("publisher_payout_vnd"),
                "gross_margin_vnd": c.get("gross_margin_vnd")
            })
        cursor.executemany("""
            INSERT INTO fact_conversions VALUES (:conversion_id, :click_id, :conversion_time, :publisher_id, :offer_id, :time_to_convert_seconds, :status, :rejection_reason, :advertiser_revenue_vnd, :publisher_payout_vnd, :gross_margin_vnd)
        """, clean_convs)
        print(f"   [SQLite] Loaded {len(clean_convs)} conversions")

    # 5. daily_campaign_kpi
    kpi = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "gold", "daily_campaign_kpi.csv.gz"))
    if kpi:
        cursor.execute("""
            CREATE TABLE daily_campaign_kpi (
                date TEXT,
                offer_id TEXT,
                total_conversions INTEGER,
                approved_conversions INTEGER,
                rejected_conversions INTEGER,
                approval_rate_pct REAL,
                gross_revenue_vnd REAL,
                publisher_payout_vnd REAL,
                gross_margin_vnd REAL
            )
        """)
        cursor.executemany("""
            INSERT INTO daily_campaign_kpi VALUES (:date, :offer_id, :total_conversions, :approved_conversions, :rejected_conversions, :approval_rate_pct, :gross_revenue_vnd, :publisher_payout_vnd, :gross_margin_vnd)
        """, kpi)
        print(f"   [SQLite] Loaded {len(kpi)} KPI rows")

    # 6. publisher_risk_scoring
    risk = load_csv_gz(os.path.join(LAKEHOUSE_DIR, "gold", "publisher_risk_scoring.csv.gz"))
    if risk:
        cursor.execute("""
            CREATE TABLE publisher_risk_scoring (
                publisher_id TEXT,
                total_leads INTEGER,
                approved_leads INTEGER,
                approval_rate_pct REAL,
                fast_ttc_bot_leads INTEGER,
                total_margin_vnd REAL,
                risk_level TEXT
            )
        """)
        cursor.executemany("""
            INSERT INTO publisher_risk_scoring VALUES (:publisher_id, :total_leads, :approved_leads, :approval_rate_pct, :fast_ttc_bot_leads, :total_margin_vnd, :risk_level)
        """, risk)
        print(f"   [SQLite] Loaded {len(risk)} Risk rows")

    conn.commit()
    conn.close()
    print(">> SQLite Database created successfully!\n")

def build_duckdb():
    try:
        import duckdb
        print(f">> Building DuckDB Database at: {DUCKDB_PATH}")
        if os.path.exists(DUCKDB_PATH):
            os.remove(DUCKDB_PATH)
        con = duckdb.connect(DUCKDB_PATH)
        con.execute(f"ATTACH DATABASE '{DB_PATH}' AS sqlite_db (TYPE SQLITE);")
        con.execute("CREATE TABLE dim_publishers AS SELECT * FROM sqlite_db.dim_publishers;")
        con.execute("CREATE TABLE dim_offers AS SELECT * FROM sqlite_db.dim_offers;")
        con.execute("CREATE TABLE fact_clicks AS SELECT * FROM sqlite_db.fact_clicks;")
        con.execute("CREATE TABLE fact_conversions AS SELECT * FROM sqlite_db.fact_conversions;")
        con.execute("CREATE TABLE daily_campaign_kpi AS SELECT * FROM sqlite_db.daily_campaign_kpi;")
        con.execute("CREATE TABLE publisher_risk_scoring AS SELECT * FROM sqlite_db.publisher_risk_scoring;")
        con.close()
        print(">> DuckDB Database created successfully!\n")
    except ImportError:
        print(">> duckdb package not installed, skipping DuckDB generation (SQLite ready).")

if __name__ == "__main__":
    build_sqlite()
    build_duckdb()
