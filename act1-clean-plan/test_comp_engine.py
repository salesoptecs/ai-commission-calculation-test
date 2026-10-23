"""Pins the answer key, and shows that every plan rule changes somebody's check (so the test is fair and complete)."""
from datetime import date
import comp_engine as ce

KEY = {"Priya Shah": 60_000.00, "Tyler Brooks": 21_600.00, "Sarah Chen": 18_000.00, "Marcus Reed": 21_000.00,
       "Dan Ortiz": 13_333.33, "Ana Lima": 6_800.00}


def test_answer_key():
    assert {r["rep"]: r["payout"] for r in ce.statements()} == KEY


def test_accelerators_are_marginal():
    assert ce.earned(340_000) == 24_000            # retroactive 1.5x would be 34,000
    assert round(ce.earned(400_000), 2) == 30_833.33


def test_cap():
    assert ce.earned(690_000) == 60_000            # uncapped 69,500


def test_first_year_value():
    assert ce.first_year_value(216_000, 36) == 72_000
    assert ce.first_year_value(50_000, 12) == 50_000


def test_owner_on_close_date():
    hist = ce.load("account_owner_history.csv")
    moved = next(r["account"] for r in hist if r["effective_date"] == "2026-08-15")
    assert ce.owner_on(moved, date(2026, 8, 14), hist) == "Marcus Reed"
    assert ce.owner_on(moved, date(2026, 8, 15), hist) == "Dan Ortiz"


def test_clawback_only_inside_90_days():
    assert ce.clawbacks(ce.load("cancellations.csv")) == {"Tyler Brooks": 2_400.0}   # Sarah's cancel was 132 days


def test_q4_deal_excluded_and_split():
    cr = ce.credits(ce.load("deals.csv"), ce.load("account_owner_history.csv"))
    assert cr["Tyler Brooks"] == 340_000 and cr["Sarah Chen"] == 270_000


def test_draw():
    rep = {"draw": "5000", "draw_shortfall": "3000"}
    assert ce.payout(9_800, 0, rep) == 6_800
    assert ce.payout(6_000, 0, rep) == 5_000      # never below the draw
