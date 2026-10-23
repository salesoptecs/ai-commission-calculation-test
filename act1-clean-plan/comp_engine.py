"""Answer key for "Can AI Calculate Commissions?": the Corvane Software Q3 AE plan, rule by rule.

Inputs (data/): deals.csv (the CRM export), cancellations.csv, account_owner_history.csv, reps.csv.
The plan lives in one PLAN dict and each rule is its own small function."""
import csv, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

PLAN = {
    "q_start": date(2026, 7, 1), "q_end": date(2026, 9, 30),
    "quota": 300_000, "target_incentive": 20_000,
    "tiers": [(1.00, 1.0), (1.25, 1.5), (None, 2.0)],   # (attainment upper bound, multiplier); marginal
    "cap_multiple": 3.0,                                  # variable pay capped at 3x target
    "clawback_days": 90,
}


def d(s):
    y, m, dd = map(int, s.split("-"))
    return date(y, m, dd)


def load(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def first_year_value(amount, term_months):
    """Rule 3: credit first-year value only (Amount is total contract value)."""
    return amount if term_months <= 12 else amount * 12 / term_months


def owner_on(account, day, history):
    """Rule 6: the rep who owned the account on the close date (the export shows today's owner)."""
    rows = sorted((r for r in history if r["account"] == account), key=lambda r: d(r["effective_date"]))
    owner = None
    for r in rows:
        if d(r["effective_date"]) <= day:
            owner = r["owner"]
    return owner


def credits(deals, history, plan=PLAN):
    """Rules 3, 4, 6, 8: Closed Won, closed inside the quarter, first-year value, split by share, credited to the
    account owner on the close date (the split partner keeps their share)."""
    out = {}
    for r in deals:
        close = d(r["close_date"])
        if r["stage"] != "Closed Won" or not (plan["q_start"] <= close <= plan["q_end"]):
            continue
        value = first_year_value(float(r["amount"]), int(r["term_months"]))
        owner = owner_on(r["account"], close, history) or r["owner"]
        if r["split_rep"]:
            share = float(r["split_pct"]) / 100
            out[owner] = out.get(owner, 0) + value * (1 - share)
            out[r["split_rep"]] = out.get(r["split_rep"], 0) + value * share
        else:
            out[owner] = out.get(owner, 0) + value
    return out


def earned(credit, plan=PLAN):
    """Rules 1 and 2: marginal accelerator bands, then the cap."""
    quota, rate = plan["quota"], plan["target_incentive"] / plan["quota"]
    pay, lower = 0.0, 0.0
    for upper, mult in plan["tiers"]:
        top = credit if upper is None else min(credit, upper * quota)
        if top > lower:
            pay += (top - lower) * rate * mult
        if upper is not None:
            lower = upper * quota
        if upper is None or credit <= upper * quota:
            break
    return min(pay, plan["cap_multiple"] * plan["target_incentive"])


def clawbacks(cancels, plan=PLAN):
    """Rule 5: a deal cancelled within 90 days of close gives back the commission paid on it, in the cancel quarter."""
    out = {}
    for r in cancels:
        cancel = d(r["cancel_date"])
        if plan["q_start"] <= cancel <= plan["q_end"] and (cancel - d(r["close_date"])).days <= plan["clawback_days"]:
            out[r["rep"]] = out.get(r["rep"], 0) + float(r["commission_paid"])
    return out


def payout(earned_amt, clawback_amt, rep):
    """Rule 7: recover a draw shortfall from this quarter's earnings, never paying below the draw."""
    net = earned_amt - clawback_amt
    draw, owed = float(rep["draw"] or 0), float(rep["draw_shortfall"] or 0)
    if draw:
        return max(draw, net - owed)
    return net


def statements(plan=PLAN):
    deals, history, cancels, reps = load("deals.csv"), load("account_owner_history.csv"), load("cancellations.csv"), load("reps.csv")
    cr, cb = credits(deals, history, plan), clawbacks(cancels, plan)
    rows = []
    for rep in reps:
        name = rep["rep"]
        c = cr.get(name, 0.0)
        e = earned(c, plan)
        rows.append({"rep": name, "credit": round(c, 2), "attainment": round(c / plan["quota"], 4), "earned": round(e, 2),
                     "clawback": round(cb.get(name, 0.0), 2), "payout": round(payout(e, cb.get(name, 0.0), rep), 2)})
    return rows


if __name__ == "__main__":
    for r in statements():
        print(f"{r['rep']:<14} credit {r['credit']:>11,.0f}  {r['attainment']:>6.0%}  earned {r['earned']:>9,.2f}  clawback {r['clawback']:>8,.2f}  payout {r['payout']:>9,.2f}")
