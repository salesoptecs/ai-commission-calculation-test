"""Answer key for Act 2 (messy Q4 plan). Rules: plan PDF + Tom's Nov 3 amendment email (renewals 50%) + Slack SPIFF post."""
import csv, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data")
Q0, Q1, PAY = date(2026, 10, 1), date(2026, 12, 31), date(2027, 1, 15)
QUOTA, TI, TIERS, CAP = 300_000, 20_000, [(1.00, 1.0), (1.25, 1.5), (None, 2.0)], 3.0
MONTHS = [(date(2026, 10, 1), date(2026, 10, 31)), (date(2026, 11, 1), date(2026, 11, 30)), (date(2026, 12, 1), date(2026, 12, 31))]


def d(s):
    return date(*map(int, s.split("-"))) if s else None


def load(n):
    with open(os.path.join(DATA, n), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fx_rate(cur, day, fx):
    if cur == "USD":
        return 1.0
    rows = [r for r in fx if r["currency"] == cur and d(r["week_of"]) <= day]
    return float(max(rows, key=lambda r: r["week_of"])["usd_per_unit"])


def full_months(rep):
    s, e = d(rep["start_date"]), d(rep["end_date"])
    return sum(1 for a, b in MONTHS if s <= a and (e is None or e >= b))


def earned(credit, quota, ti):
    rate, pay, lower = ti / quota, 0.0, 0.0
    for upper, m in TIERS:
        top = credit if upper is None else min(credit, upper * quota)
        if top > lower:
            pay += (top - lower) * rate * m
        if upper is None or credit <= upper * quota:
            break
        lower = upper * quota
    return min(pay, CAP * ti)


def statements():
    deals, fx, reps = load("deals.csv"), load("fx_rates.csv"), load("reps.csv")
    seen, credit, spiff, held, notes = set(), {}, {}, [], []
    for r in deals:
        close = d(r["close_date"])
        if r["stage"] != "Closed Won" or not (Q0 <= close <= Q1):
            continue
        if r["opportunity_id"] in seen:
            notes.append(f"duplicate {r['opportunity_id']} ignored"); continue
        seen.add(r["opportunity_id"])
        if float(r["discount_pct"] or 0) > 20 and not r["vp_approval"]:
            notes.append(f"{r['opportunity_id']} {r['discount_pct']}% discount, no VP approval: not commissionable"); continue
        usd = float(r["amount"]) * fx_rate(r["currency"], close, fx)
        if r["type"] == "Renewal":
            usd *= 0.5
        if r["split_rep"]:
            sp = float(r["split_pct"]) / 100
            op = float(r["owner_pct"]) / 100 if r["owner_pct"] else 1 - sp
            if abs(sp + op - 1) > 1e-9:
                held.append(r["opportunity_id"]); notes.append(f"{r['opportunity_id']} split totals {sp+op:.0%}: held"); continue
            credit[r["split_rep"]] = credit.get(r["split_rep"], 0) + usd * sp
            usd *= op
        credit[r["owner"]] = credit.get(r["owner"], 0) + usd
        if r["new_logo"] == "Yes" and close.month == 11 and usd > 50_000:
            spiff[r["owner"]] = spiff.get(r["owner"], 0) + 500
    out = []
    for rep in reps:
        n = rep["rep"]; m = full_months(rep) if d(rep["start_date"]) > Q0 else 3
        q, ti = QUOTA * m / 3, TI * m / 3
        c = credit.get(n, 0.0); e = earned(c, q, ti); s = spiff.get(n, 0)
        employed = not rep["end_date"] or d(rep["end_date"]) >= PAY
        out.append({"rep": n, "quota": q, "credit": round(c, 2), "attain": c / q, "earned": round(e, 2), "spiff": s,
                    "payout": round(e + s, 2) if employed else 0.0})
    return out, notes


if __name__ == "__main__":
    rows, notes = statements()
    for r in rows:
        print(f"{r['rep']:<13} quota {r['quota']:>9,.0f} credit {r['credit']:>11,.2f} {r['attain']:>6.1%} earned {r['earned']:>10,.2f} spiff {r['spiff']:>5} payout {r['payout']:>10,.2f}")
    print(*notes, sep="\n")
