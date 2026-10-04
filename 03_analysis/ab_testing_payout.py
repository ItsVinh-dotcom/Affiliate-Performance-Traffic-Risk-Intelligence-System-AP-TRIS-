"""
A/B Test Design & Analysis: Flat vs Tiered Commission for Finance & Banking offers
Project: AP-TRIS

Why the design matters: a commission policy is applied to a PUBLISHER, not to a click.
So the randomisation unit (and the unit of analysis) must be the publisher.
Splitting clicks into A/B would let the same publisher sit in both groups and
inflate significance.

Steps
1. Baseline from real data   : approved Finance conversions & margin per publisher (Aug-Sep 2026)
2. Power analysis            : how big an uplift can we detect with ~245 publishers?
3. A/A test on real data     : random split with NO treatment -> must NOT be significant.
                               Publisher volume is highly skewed, so we use stratified
                               matched-pair randomisation by baseline volume (much lower MDE).
4. Simulated experiment      : apply an ASSUMED behavioural effect of the tiered scheme
                               to group B, then analyse it exactly as a real test
                               (paired t-test + bootstrap CI on publisher-level metrics)

Step 4 uses an assumed effect (documented below) because the dataset contains no
real treatment. Steps 1-3 use the actual 1M-click dataset.
"""
import os

import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAKE = os.path.join(BASE, "01_data", "lakehouse")

ALPHA, POWER = 0.05, 0.80
TEST_WEEKS = 4
# Tiered scheme for group B (applied per publisher per month)
TIER_BASE_PAYOUT_FACTOR = 0.88       # base commission cut by 12%
TIER_BONUS_VND = 60_000              # bonus per approved card once publisher exceeds the threshold
TIER_THRESHOLD = 30                  # approved Finance conversions per month
# ASSUMPTION for the simulation: tiered bonus motivates publishers to push +15% approved volume
ASSUMED_LIFT = 0.15
RNG = np.random.default_rng(42)


def publisher_month_panel():
    conv = pd.read_csv(os.path.join(LAKE, "silver", "fact_conversions_cleansed.csv.gz"))
    pubs = pd.read_csv(os.path.join(LAKE, "silver", "dim_publishers.csv.gz"))
    offers = pd.read_csv(os.path.join(LAKE, "silver", "dim_offers.csv.gz"))
    conv["month"] = (pd.to_datetime(conv["conversion_time"]) + pd.Timedelta(hours=7)).dt.strftime("%Y-%m")
    fin = conv[(conv.vertical == "Finance & Banking") & (conv.status == "Approved")
               & conv.month.isin(["2026-08", "2026-09"])]
    fin = fin[~fin.publisher_id.isin(pubs.loc[pubs.status == "Flagged", "publisher_id"])]   # exclude fraud
    g = fin.groupby(["publisher_id", "month"]).agg(
        approved=("conversion_id", "count"),
        revenue=("advertiser_revenue_vnd", "sum"),
        payout=("publisher_payout_vnd", "sum"))
    return g.reset_index(), offers


def margin_under_scheme(panel, tiered):
    """Platform margin per publisher-month under flat or tiered commission."""
    if not tiered:
        return panel.revenue - panel.payout
    bonus = np.where(panel.approved > TIER_THRESHOLD, panel.approved * TIER_BONUS_VND, 0)
    return panel.revenue - panel.payout * TIER_BASE_PAYOUT_FACTOR - bonus


def welch(a, b):  # Welch two-sample t-test (unequal variances)
    t, p = stats.ttest_ind(b, a, equal_var=False)
    return t, p


def main():
    panel, _ = publisher_month_panel()
    per_pub = panel.groupby("publisher_id").agg(approved=("approved", "mean"),
                                                 revenue=("revenue", "mean"), payout=("payout", "mean"))
    n_pub = len(per_pub)
    print("=" * 70)
    print(">> A/B TEST: FLAT vs TIERED COMMISSION (Finance & Banking offers)")
    print("=" * 70)

    # 1. Baseline
    mu, sd = per_pub.approved.mean(), per_pub.approved.std()
    print(f"\n[1] BASELINE (real data, {n_pub} non-flagged publishers)")
    print(f"    Approved Finance conversions / publisher / month: mean {mu:.1f}, sd {sd:.1f}")
    print(f"    Publishers above tier threshold ({TIER_THRESHOLD}/month): "
          f"{(panel.approved > TIER_THRESHOLD).mean() * 100:.0f}% of publisher-months")

    # 2. Power analysis (two-sample, equal split, monthly metric)
    z = stats.norm.ppf(1 - ALPHA / 2) + stats.norm.ppf(POWER)
    mde_abs = z * sd * np.sqrt(2 / (n_pub / 2))
    print(f"\n[2] POWER ANALYSIS (alpha={ALPHA}, power={POWER}, {n_pub // 2} publishers per group)")
    print(f"    Minimum detectable effect: +{mde_abs:.1f} approved/publisher/month (= +{mde_abs / mu * 100:.0f}%)")
    print("    -> Publisher volume is very uneven (a few large publishers), so only large effects are detectable;")
    print("       options: run longer, stratify by tier, or use CUPED with pre-period data.")

    # 3. A/A tests: simple vs stratified (matched-pair) randomisation
    ids = per_pub.index.to_numpy().copy()
    RNG.shuffle(ids)
    t, p = welch(per_pub.loc[ids[: n_pub // 2], "approved"], per_pub.loc[ids[n_pub // 2:], "approved"])
    print(f"\n[3] A/A TEST on real data (no treatment applied)")
    print(f"    a) Simple random split      : t={t:+.2f}, p={p:.3f} "
          f"-> {'balanced' if p > ALPHA else 'NOT balanced: a few big publishers landed in one group'}")
    # matched pairs: sort by baseline volume, randomise A/B inside each consecutive pair
    order = per_pub.sort_values("approved", ascending=False).index.to_numpy()[: (n_pub // 2) * 2]
    pairs = order.reshape(-1, 2)
    flip = RNG.random(len(pairs)) < 0.5
    a_ids = np.where(flip, pairs[:, 0], pairs[:, 1])
    b_ids = np.where(flip, pairs[:, 1], pairs[:, 0])
    d = per_pub.loc[b_ids, "approved"].to_numpy() - per_pub.loc[a_ids, "approved"].to_numpy()
    t, p = stats.ttest_1samp(d, 0)
    print(f"    b) Stratified (matched pairs): t={t:+.2f}, p={p:.3f} -> {'balanced' if p > ALPHA else 'NOT balanced'}")
    mde_pair = z * d.std(ddof=1) / np.sqrt(len(d))
    print(f"       MDE with matched pairs: +{mde_pair:.1f} approved/publisher/month (= +{mde_pair / mu * 100:.0f}%) "
          f"vs +{mde_abs / mu * 100:.0f}% with simple split")

    # 4. Simulated experiment on the matched-pair design
    pa = panel[panel.publisher_id.isin(a_ids)].copy()
    pb = panel[panel.publisher_id.isin(b_ids)].copy()
    lift = RNG.normal(ASSUMED_LIFT, 0.10, len(pb))                    # heterogeneous response per publisher-month
    scale = np.clip(1 + lift, 0.5, None)
    pb["approved"] = np.round(pb.approved * scale)
    pb["revenue"] = pb.revenue * scale
    pb["payout"] = pb.payout * scale
    pa["margin"] = margin_under_scheme(pa, tiered=False)
    pb["margin"] = margin_under_scheme(pb, tiered=True)
    A = pa.groupby("publisher_id")[["approved", "margin"]].mean().reindex(a_ids).fillna(0)
    B = pb.groupby("publisher_id")[["approved", "margin"]].mean().reindex(b_ids).fillna(0)

    print(f"\n[4] SIMULATED EXPERIMENT (assumed behavioural lift ~ +{ASSUMED_LIFT * 100:.0f}% in group B, "
          f"{len(pairs)} matched pairs)")
    for metric, label in (("approved", "Approved / publisher / month"),
                          ("margin", "Platform margin / publisher / month (VND)")):
        diff = B[metric].to_numpy() - A[metric].to_numpy()
        t, p = stats.ttest_1samp(diff, 0)
        boot = [RNG.choice(diff, len(diff)).mean() for _ in range(5000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        rel = (B[metric].mean() / A[metric].mean() - 1) * 100
        print(f"    {label}")
        print(f"      A={A[metric].mean():,.1f} | B={B[metric].mean():,.1f} | diff {rel:+.1f}% | "
              f"paired t={t:.2f}, p={p:.4f} | 95% bootstrap CI [{lo:,.1f}; {hi:,.1f}]")

    print("\n[RECOMMENDATION]")
    print("  - Decide on PLATFORM MARGIN, not on volume: the bonus can raise volume while eroding margin.")
    print("  - If the margin CI includes 0, do not roll out; re-test with stratification by tier or a longer window.")
    print("=" * 70)


if __name__ == "__main__":
    main()
