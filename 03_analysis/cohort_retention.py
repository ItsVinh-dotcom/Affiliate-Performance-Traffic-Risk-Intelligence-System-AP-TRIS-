"""
Cohort Retention & Publisher Lifetime Value (LTV) Analysis
Tracks the monthly retention rate and cumulative gross margin of Publishers
grouped by their onboarding month.
"""

import os
import csv
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "01_data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "01_data", "processed")

def load_csv(filepath):
    data = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def run_cohort_analysis():
    print("=" * 60)
    print(">> PUBLISHER COHORT RETENTION & VALUE ANALYSIS")
    print("=" * 60)

    publishers = load_csv(os.path.join(RAW_DIR, "dim_publishers.csv"))
    conversions = load_csv(os.path.join(RAW_DIR, "fact_conversions.csv"))

    # Map publisher to join month (Cohort)
    pub_cohort = {}
    cohort_sizes = defaultdict(int)
    for p in publishers:
        cohort = p["join_date"][:7] # YYYY-MM
        pub_cohort[p["publisher_id"]] = cohort
        cohort_sizes[cohort] += 1

    # Map conversions to activity month
    # Structure: cohort -> month_index -> set of active publishers
    cohort_activity = defaultdict(lambda: defaultdict(set))
    cohort_margin = defaultdict(lambda: defaultdict(float))

    for conv in conversions:
        if conv["status"] != "Approved":
            continue
        pid = conv["publisher_id"]
        if pid not in pub_cohort:
            continue
        cohort = pub_cohort[pid]
        activity_month = conv["conversion_time"][:7]

        # Calculate month difference
        c_year, c_month = int(cohort[:4]), int(cohort[5:7])
        a_year, a_month = int(activity_month[:4]), int(activity_month[5:7])
        month_idx = (a_year - c_year) * 12 + (a_month - c_month)

        if month_idx >= 0:
            cohort_activity[cohort][month_idx].add(pid)
            cohort_margin[cohort][month_idx] += float(conv.get("gross_margin_vnd", 0))

    # Print Cohort Retention Matrix
    sorted_cohorts = sorted(cohort_sizes.keys())[-6:] # Recent 6 cohorts
    print("\n[COHORT RETENTION MATRIX (% Active Publishers)]")
    print(f"{'Cohort':<10} | {'Size':<6} | {'M+0':<8} | {'M+1':<8} | {'M+2':<8} | {'M+3':<8}")
    print("-" * 55)

    matrix_rows = []
    for c in sorted_cohorts:
        size = cohort_sizes[c]
        row_str = f"{c:<10} | {size:<6} |"
        csv_row = {"cohort": c, "initial_size": size}
        for m in range(4):
            active_count = len(cohort_activity[c][m])
            ret_pct = (active_count / size * 100) if size > 0 else 0
            row_str += f" {ret_pct:>6.1f}% |"
            csv_row[f"m_{m}_pct"] = round(ret_pct, 1)
        print(row_str)
        matrix_rows.append(csv_row)

    # Save to CSV
    matrix_file = os.path.join(PROCESSED_DIR, "cohort_retention_matrix.csv")
    with open(matrix_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["cohort", "initial_size", "m_0_pct", "m_1_pct", "m_2_pct", "m_3_pct"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matrix_rows)

    print(f"\n[SUCCESS] Cohort matrix exported to: {matrix_file}")

    # Try plotting heatmap if matplotlib & seaborn are installed
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np

        # Create 2D array for heatmap
        data_matrix = []
        cohort_labels = []
        for row in matrix_rows:
            cohort_labels.append(row["cohort"])
            data_matrix.append([row["m_0_pct"], row["m_1_pct"], row["m_2_pct"], row["m_3_pct"]])

        plt.figure(figsize=(8, 5))
        sns.heatmap(data_matrix, annot=True, fmt=".1f", cmap="YlGnBu", 
                    xticklabels=["Month 0", "Month 1", "Month 2", "Month 3"],
                    yticklabels=cohort_labels, cbar_kws={'label': 'Retention Rate %'})
        plt.title("Publisher Cohort Retention Rate (%)", fontsize=14, pad=15)
        plt.xlabel("Months Since Onboarding", fontsize=11)
        plt.ylabel("Join Cohort (YYYY-MM)", fontsize=11)
        plt.tight_layout()

        img_path = os.path.join(BASE_DIR, "04_powerbi", "dashboard_screenshots", "cohort_retention_heatmap.png")
        plt.savefig(img_path, dpi=300)
        plt.close()
        print(f"[SUCCESS] Heatmap chart generated and saved to: {img_path}")
    except Exception as e:
        print(f"[NOTE] Heatmap visualization skipped (Libraries loading: {e})")

    print("=" * 60)

if __name__ == "__main__":
    run_cohort_analysis()
