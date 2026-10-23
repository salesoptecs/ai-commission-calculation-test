# Can AI Calculate Sales Commissions? A Real Test

The comp plans, CRM exports and spreadsheets from the video: https://www.youtube.com/watch?v=ZFC8hHwi3ns

Corvane Software and its six reps are made up. Everything here is safe to upload to any AI tool.

## Act 1: a clean plan (Q3)
`act1-clean-plan/`
- `data/Corvane_Q3_AE_Comp_Plan.pdf`: the plan (quota, marginal accelerators, a 3x cap, a 90 day clawback, a draw for new reps)
- `data/deals.csv`, `cancellations.csv`, `account_owner_history.csv`, `reps.csv`: the CRM exports, traps included
- `comp_engine.py`: the answer key, one small function per plan rule. Run `python comp_engine.py`
- `test_comp_engine.py`: pins the answer key and checks that every rule changes somebody's payout. Run `pytest`

## Act 2: a messy plan (Q4)
`act2-messy-plan/`
- `data/Corvane_Q4_AE_Comp_Plan.pdf`: the plan
- `data/amendment_email.txt`: the VP of Sales email (renewals count at 50%)
- `data/spiff_slack.txt`: the November SPIFF, announced in Slack
- `data/deals.csv`, `fx_rates.csv`, `reps.csv`: the dirty export (euros and pounds, a duplicate, a 110% split, an unapproved discount, a rep who resigned, a new hire)
- `data/Corvane_Q4_Payouts_Spreadsheet.xlsx`: both spreadsheets. `Typical` is the sheet most teams start with. `Fixed` adds a column for every rule and matches the answer key
- `comp_engine.py`: the answer key. `build_sheet.py` rebuilds the spreadsheet

## Try it on your own plan
1. Build a small answer key: last quarter's paid statements, or three reps worked by hand.
2. Run the same prompt twice in fresh chats and compare.
3. Ask for a spreadsheet, and spot check the deals that moved money.
4. Read the list of assumptions. That's where the real questions about your plan show up.
5. Check your company's policy before you upload real pay data to any AI tool.

The prompts, typed into a fresh Claude Desktop chat (Opus 5.5) with the plan and exports attached:

> Act 1: Here's our Q3 AE comp plan and the quarter's exports. Calculate each rep's Q3 payout.
>
> Act 2: Here's our Q4 AE comp plan and the quarter's exports. Calculate each rep's Q4 payout.

In Act 2 the spreadsheet was not attached. It's the comparison at the end of the video.

MIT License. Made by [SalesOptecs](https://salesoptecs.com).
