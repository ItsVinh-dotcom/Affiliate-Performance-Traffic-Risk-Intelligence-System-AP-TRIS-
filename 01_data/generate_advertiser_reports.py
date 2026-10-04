"""
Simulate advertiser-side monthly conversion reports (second data source).

In practice, each advertiser (bank / brand) sends back its own monthly file of
leads it received and the final status it assigned. The file is matched to the
platform's tracking data via click_id (passed to the advertiser as sub_id).

To make reconciliation meaningful, the simulated files deliberately contain
the discrepancy types seen in real affiliate operations:
  - MISSING_AT_ADVERTISER : postback/lead lost, advertiser never received it
  - MISSING_IN_TRACKING   : advertiser has a lead the platform did not track
  - STATUS_MISMATCH       : advertiser's final status differs (late cancel,
                            pending lead finalised, re-review after audit)
  - AMOUNT_MISMATCH       : advertiser pays a different rate (old price list,
                            promotional rate not applied)

Output: 01_data/sources/advertiser_reports/advertiser_report_<YYYY-MM>.csv.gz
"""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
LAKE = os.path.join(BASE, "lakehouse")
OUT = os.path.join(BASE, "sources", "advertiser_reports")
VN_OFFSET = pd.Timedelta(hours=7)          # tracking timestamps are stored in UTC

RATE_MISSING_AT_ADV = 0.015
RATE_STATUS_MISMATCH = 0.025
RATE_AMOUNT_MISMATCH = 0.010
RATE_EXTRA_AT_ADV = 0.004


def main():
    rng = np.random.default_rng(2026)
    os.makedirs(OUT, exist_ok=True)

    conv = pd.read_csv(os.path.join(LAKE, "silver", "fact_conversions_cleansed.csv.gz"))
    offers = pd.read_csv(os.path.join(LAKE, "silver", "dim_offers.csv.gz"))
    conv["conversion_time"] = pd.to_datetime(conv["conversion_time"]) + VN_OFFSET
    conv["month"] = conv["conversion_time"].dt.strftime("%Y-%m")
    conv = conv[conv["month"].isin(["2026-08", "2026-09"])].copy()

    rate = offers.set_index("offer_id")["advertiser_revenue_vnd"]
    n = len(conv)
    u = rng.random(n)

    adv = conv[["click_id", "offer_id", "advertiser_name", "conversion_time", "status", "month"]].copy()
    adv["adv_status"] = adv["status"].replace({"Fraud": "Rejected"})
    # Platform "Pending" leads are finalised by the advertiser at month end
    pend = adv["adv_status"].eq("Pending")
    adv.loc[pend, "adv_status"] = np.where(rng.random(pend.sum()) < 0.55, "Approved", "Rejected")

    # 1) missing at advertiser
    keep = u >= RATE_MISSING_AT_ADV
    # 2) status mismatch on remaining approved/rejected records
    sm = (u >= RATE_MISSING_AT_ADV) & (u < RATE_MISSING_AT_ADV + RATE_STATUS_MISMATCH) & ~pend.values
    adv.loc[sm, "adv_status"] = np.where(adv.loc[sm, "adv_status"].eq("Approved"), "Rejected", "Approved")
    # 3) amount: contractual rate, with some records billed at a lower old rate
    adv["adv_revenue_vnd"] = np.where(adv["adv_status"].eq("Approved"), adv["offer_id"].map(rate), 0.0)
    am = (u >= RATE_MISSING_AT_ADV + RATE_STATUS_MISMATCH) & \
         (u < RATE_MISSING_AT_ADV + RATE_STATUS_MISMATCH + RATE_AMOUNT_MISMATCH) & adv["adv_status"].eq("Approved").values
    adv.loc[am, "adv_revenue_vnd"] = (adv.loc[am, "adv_revenue_vnd"] * 0.85).round(-3)
    adv = adv[keep]

    # 4) leads the advertiser has but platform tracking missed
    n_extra = int(n * RATE_EXTRA_AT_ADV)
    src = conv.sample(n_extra, random_state=7)
    extra = pd.DataFrame({
        "click_id": [f"CLK_X{9000000 + i}" for i in range(n_extra)],
        "offer_id": src["offer_id"].values,
        "advertiser_name": src["advertiser_name"].values,
        "conversion_time": src["conversion_time"].values,
        "status": None,
        "month": src["month"].values,
        "adv_status": "Approved",
    })
    extra["adv_revenue_vnd"] = extra["offer_id"].map(rate)
    adv = pd.concat([adv, extra], ignore_index=True)

    adv = adv.rename(columns={"click_id": "sub_id", "conversion_time": "lead_time"})
    cols = ["sub_id", "advertiser_name", "offer_id", "lead_time", "adv_status", "adv_revenue_vnd"]
    for m, part in adv.groupby("month"):
        path = os.path.join(OUT, f"advertiser_report_{m}.csv.gz")
        part.sort_values("lead_time")[cols].to_csv(path, index=False, compression="gzip")
        print(f"[OK] {os.path.relpath(path, BASE)}  ({len(part):,} rows)")


if __name__ == "__main__":
    main()
