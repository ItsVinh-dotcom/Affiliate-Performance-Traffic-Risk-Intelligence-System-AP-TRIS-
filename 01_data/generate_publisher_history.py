"""
Publisher History Generator (12 months) - input for Cohort Analysis
Project: AP-TRIS

The detailed click/conversion dataset only covers the 250 publishers that are
ACTIVE in Aug-Sep 2026. A cohort analysis needs everyone who ever registered,
including publishers who never activated or who churned.

This script simulates the full publisher base (Oct 2025 - Sep 2026):
  * the 250 active publishers (same IDs, channel, tier, join date as dim_publishers);
    their Aug-Sep 2026 activity is taken from the REAL fact table, earlier months
    are back-filled with a ramp-up curve;
  * ~950 long-tail / self-serve publishers (never activated, churned, or still active
    with small volume). Only the 250 managed publishers have click-level tracking data.

Simulation assumptions (documented so results are not mistaken for real findings):
  * 30% of new registrants never produce an approved conversion (no activation)
  * monthly churn hazard differs by traffic channel (see CHURN_BY_CHANNEL)
  * new publishers ramp up: month 0 = 35%, month 1 = 70%, month 2+ = 100% of steady volume

Outputs:
  01_data/sources/publisher_registry.csv.gz           (one row per registered publisher)
  01_data/sources/publisher_monthly_activity.csv.gz   (publisher x month, only months with activity)
"""
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
LAKE = os.path.join(BASE, "lakehouse")
OUT = os.path.join(BASE, "sources")
MONTHS = pd.period_range("2025-10", "2026-09", freq="M")
N_EXTRA = 950
NO_ACTIVATION_RATE = 0.30
CHURN_BY_CHANNEL = {            # monthly probability that an active publisher stops
    "Facebook Media Buyer": 0.32,
    "TikTok Creator": 0.28,
    "Telegram/Zalo Community": 0.30,
    "Google Ads Specialist": 0.20,
    "YouTube Reviewer": 0.16,
    "SEO Content Hub": 0.10,
}
RAMP = {0: 0.35, 1: 0.70}
MARGIN_PER_APPROVED = 55_000     # avg platform margin per approved conversion (from real data)


def main():
    rng = np.random.default_rng(11)
    os.makedirs(OUT, exist_ok=True)
    pubs = pd.read_csv(os.path.join(LAKE, "silver", "dim_publishers.csv.gz"))
    conv = pd.read_csv(os.path.join(LAKE, "silver", "fact_conversions_cleansed.csv.gz"))
    conv["month"] = (pd.to_datetime(conv.conversion_time) + pd.Timedelta(hours=7)).dt.to_period("M")
    real = conv[(conv.status == "Approved") & conv.month.isin(MONTHS[-2:])] \
        .groupby(["publisher_id", "month"]).agg(approved=("conversion_id", "count"),
                                                margin_vnd=("gross_margin_vnd", "sum")).reset_index()

    rows = []
    # ---- 250 currently active publishers
    steady = real.groupby("publisher_id").approved.mean()
    for p in pubs.itertuples():
        jm = pd.Period(p.join_date, "M")
        for m in MONTHS[:-2]:
            if m < jm:
                continue
            age = (m - jm).n
            lam = steady.get(p.publisher_id, 1) * RAMP.get(age, 1.0)
            a = rng.poisson(max(lam, 0.3))
            if a > 0:
                rows.append((p.publisher_id, str(m), a, a * MARGIN_PER_APPROVED * rng.uniform(0.85, 1.15)))
    for r in real.itertuples():
        rows.append((r.publisher_id, str(r.month), r.approved, r.margin_vnd))
    registry = pubs[["publisher_id", "traffic_channel", "tier", "join_date"]].assign(current_status="Active (managed)")

    # ---- long-tail publishers: never activated, churned, or still active with small volume
    channels = list(CHURN_BY_CHANNEL)
    extra = []
    month_w = np.linspace(1.0, 1.4, len(MONTHS)); month_w /= month_w.sum()   # sign-ups grow slowly
    for i in range(N_EXTRA):
        pid = f"PUB_{251 + i:04d}"
        ch = rng.choice(channels)
        jm = MONTHS[rng.choice(len(MONTHS), p=month_w)]
        join = jm.to_timestamp() + pd.Timedelta(days=int(rng.integers(0, 28)))
        tier = rng.choice(["Bronze", "Silver", "Gold"], p=[0.75, 0.20, 0.05])
        status = "Never activated"
        if rng.random() > NO_ACTIVATION_RATE:
            steady_vol = rng.lognormal(mean=2.0, sigma=0.8)        # median ~7 approved / month
            for age, m in enumerate(MONTHS[MONTHS.get_loc(jm):]):
                a = rng.poisson(steady_vol * RAMP.get(age, 1.0))
                if a > 0:
                    rows.append((pid, str(m), a, a * MARGIN_PER_APPROVED * rng.uniform(0.85, 1.15)))
                    status = "Active (long-tail)" if m == MONTHS[-1] else "Churned"
                if rng.random() < CHURN_BY_CHANNEL[ch]:
                    break
        extra.append((pid, ch, tier, join.strftime("%Y-%m-%d"), status))
    registry = pd.concat([registry, pd.DataFrame(extra, columns=registry.columns)], ignore_index=True)

    act = pd.DataFrame(rows, columns=["publisher_id", "month", "approved_conversions", "gross_margin_vnd"])
    act["gross_margin_vnd"] = act.gross_margin_vnd.round(-3)
    registry.to_csv(os.path.join(OUT, "publisher_registry.csv.gz"), index=False, compression="gzip")
    act.sort_values(["publisher_id", "month"]).to_csv(os.path.join(OUT, "publisher_monthly_activity.csv.gz"),
                                                      index=False, compression="gzip")
    print(f"[OK] publisher_registry: {len(registry):,} publishers "
          f"({registry.current_status.value_counts().to_dict()})")
    print(f"[OK] publisher_monthly_activity: {len(act):,} publisher-months")


if __name__ == "__main__":
    main()
