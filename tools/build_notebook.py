"""Rebuilds PS2_chatbot_subsidy_auction.ipynb so its first code cell embeds chatbot_auction.py verbatim.

Run from the repository root:  python tools/build_notebook.py
Then execute it:              jupyter nbconvert --to notebook --execute --inplace PS2_chatbot_subsidy_auction.ipynb
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(ROOT, "PS2_chatbot_subsidy_auction.ipynb")


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


with open(os.path.join(ROOT, "chatbot_auction.py"), encoding="utf-8") as fh:
    MODULE = fh.read().rstrip("\n")

cells = [
    md(r"""
# Who builds the honest chatbot? A subsidy tender with a compliance audit
COMSCI/ECON 206 Computational Microeconomics · Autumn 2026 Session 1 · PS2 computational artifact · Muhan Chen

**Question.** A government pays one company, from a fixed grant, to build a non-sycophantic chatbot. It runs a second-price tender and then audits the winner. How strong must the audit be for the grant to buy honesty, and what happens to spending when the audit is weak?

**Run.** *Runtime → Run all.* Python standard library plus matplotlib (preinstalled in Colab). Deterministic: seed 206. All inputs are synthetic; no human data. The first code cell writes `chatbot_auction.py`, identical to the GitHub file, so the notebook needs no other file.

| Symbol | Meaning | Baseline |
|---|---|---|
| $n$ | companies per tender | 4 |
| $c_i$ | private cost of building the honest chatbot, i.i.d. $U[0,100]$ | — |
| $B$ | grant cap = fixed subsidy pool | 80 |
| $E$ | extra engagement revenue from a sycophantic chatbot | 30 |
| $k$ | extra tuning cost of making it sycophantic | 10 |
| $p$ | probability the regulator audits the winner | 0.5 (strong); 0.3 (weak) |
| $F$ | fine if the audit finds sycophancy | 50 |
"""),
    code("%%writefile chatbot_auction.py\n" + MODULE),
    code(r"""
import importlib, platform
import matplotlib
import chatbot_auction as ca
importlib.reload(ca)
print("Python", platform.python_version(), "| matplotlib", matplotlib.__version__)
print(ca.BASELINE)
"""),
    md(r"""
## Model and solution concept
**Players.** $n$ risk-neutral AI companies; the government sets the rules. **Information.** Each company privately knows its own cost $c_i$; costs are independent draws from $U[0,100]$. $B, E, k, p, F$ are public.

**Timing.** (1) Nature draws costs. (2) Companies submit sealed bids $b_i\in[0,100]$, the grant they ask for. (3) The **lowest** bid $\le B$ wins and is paid the **second-lowest** bid, capped at $B$ (a reverse second-price tender); if every bid exceeds $B$, nothing is awarded. (4) The winner complies (builds honest, cost $c_i$) or cheats (builds sycophantic, cost $c_i+k$, extra revenue $E$). (5) Nature audits with probability $p$; an audited cheater pays $F$.

**Payoffs.** Loser: 0. Winner: $P-c_i$ if it complies; $P-c_i+(E-k)-F\cdot\mathbf 1[\text{audited}]$ if it cheats.

**Solution (backward induction).** Stage 4: the choice does not depend on rivals, so the winner cheats iff $E-k>pF$, i.e. iff $p<p^\ast=(E-k)/F=0.4$ (Becker 1968). The grant $P$ cancels out of this comparison. Stage 2 is a Bayesian game (private costs); in a second-price tender bidding one's effective cost $\max(0,\,c_i-\rho)$ is weakly dominant (Vickrey 1961), where $\rho=\max(0,E-k-pF)$ is the expected cheating rent. With a strong audit ($p=0.5$), $\rho=0$ and the benchmark is simply *bid your cost*. With a weak audit ($p=0.3$), $\rho=5$ and every company bids 5 below cost.

**Pseudocode (one tender).**
```
input: costs c[1..n], audit draw u, parameters (B, E, k, p, F)
rho   <- max(0, E - k - p*F)
bid_i <- max(0, c_i - rho)
w     <- argmin_i bid_i  (ties: lowest index); if bid_w > B: no award, stop
pay   <- min(second-lowest bid, B)
cheat <- (rho > 0);  caught <- cheat and (u < p)
record pay, efficient = (c_w is the lowest cost <= B), honest = not cheat,
       winner profit = pay - c_w + cheat*(E - k) - caught*F
```
"""),
    code(r"""
cfg = ca.BASELINE
weak = ca.replace(cfg, audit_prob=ca.WEAK_AUDIT)
print(f"p* = (E-k)/F = {ca.audit_threshold(cfg):.2f}")
print(f"Strong audit p={cfg.audit_prob}: E[cheat]-E[comply] = {ca.expected_cheat_value(cfg):+.1f}, rent = {ca.cheating_rent(cfg):.1f}")
print(f"Weak audit   p={weak.audit_prob}: E[cheat]-E[comply] = {ca.expected_cheat_value(weak):+.1f}, rent = {ca.cheating_rent(weak):.1f}")
print(f"{'cost':>6} {'bid (strong)':>13} {'bid (weak)':>11}")
for c in (0, 3, 20, 40, 60, 79, 90):
    print(f"{c:>6} {ca.benchmark_bid(c, cfg):>13} {ca.benchmark_bid(c, weak):>11}")
"""),
    md(r"""
## Comparison: the same tender under a strong and a weak audit
50,000 tenders per setting with the **same** cost and audit draws, so differences come from the audit alone. Metrics: mean and standard deviation of government spending, share funding the lowest-cost eligible company (efficiency), share delivering an honest chatbot, winner profit, and fines collected. `ca.main()` also writes every number to `outputs/results.json`.
"""),
    code(r"""
results = ca.main()
comp = results["comparison"]
"""),
    md(r"""
## Parameter change: sweep the audit probability
$p$ from 0 to 1 in steps of 0.05, 10,000 tenders per value.
"""),
    code(r"""
print(f"{'p':>5} {'rent':>5} {'spending':>9} {'SD':>6} {'honest':>7} {'fines':>6}")
for r in results["audit_sweep"]:
    if r["audit_prob"] in (0.0, 0.2, 0.3, 0.35, 0.4, 0.5, 1.0):
        print(f"{r['audit_prob']:>5.2f} {r['cheating_rent']:>5.1f} {r['mean_spending']:>9.2f} "
              f"{r['sd_spending']:>6.2f} {r['honest_delivery_rate']:>7.3f} {r['mean_fines_collected']:>6.2f}")
"""),
    code(r"""
from IPython.display import Image, display
for path in ca.plot_results(cfg, comp, results["audit_sweep"]):
    display(Image(filename=path, width=460))
"""),
    md(r"""
## Parity with the Hugging Face game
The game uses the same rules and the same seeded generator (mulberry32 seeded by an FNV-1a hash of the session code). Session code `206` below reproduces the costs, audits, and rival bids a player sees; `tests/js_fixture.json` in the repository stores the game's own output for automated comparison.
"""),
    code(r"""
s = ca.make_schedule("206")
print("seed", s["seed"])
print(f"{'round':>5} {'your cost':>9} {'rival costs (= rival bids)':>28} {'audited':>8}")
for r in s["rounds"]:
    print(f"{r['round']:>5} {r['playerCost']:>9} {str(r['rivalCosts']):>28} {str(r['audited']):>8}")
"""),
    md(r"""
## Verification
Checks on the theory and the rules. The repository runs the full suite, including exact parity with the game: `python -m unittest discover -s tests -v`.
"""),
    code(r"""
import math
assert abs(ca.audit_threshold(cfg) - 0.4) < 1e-12 and not ca.rational_cheats(cfg) and ca.rational_cheats(weak)
assert ca.benchmark_bid(40, cfg) == 40 and ca.benchmark_bid(40, weak) == 35
assert ca.run_auction([30, 50, 40, 90], 80) == (0, 40)
assert ca.run_auction([30, 85, 90, 95], 80) == (0, 80)
assert ca.run_auction([85, 81, 90, 95], 80) == (-1, 0.0)
# Truthful bidding is weakly dominant on a grid of rival bids.
for cost in (5, 40, 79, 85):
    for r1 in range(0, 101, 10):
        for r2 in range(0, 101, 10):
            pay = lambda b: (lambda w, p: p - cost if w == 0 else 0)(*ca.run_auction([b, r1, r2, 100], 80, False))
            assert all(pay(cost) >= pay(d) - 1e-9 for d in range(0, 101, 5))
# Simulated strong-audit spending lies within 4 standard errors of the exact value.
st = comp["strong"]
assert abs(st["mean_spending"] - results["expected_spending_exact"]) < 4 * st["sd_spending"] / math.sqrt(st["trials"])
# The weak audit is cheaper but delivers no honest chatbot.
assert comp["weak"]["mean_spending"] < st["mean_spending"] and comp["weak"]["honest_delivery_rate"] == 0
for bad in ([math.nan, 40], [-1, 40], [101, 40]):
    try:
        ca.run_auction(bad, 80)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid bid accepted")
print("All checks passed.")
"""),
    md(r"""
## Classroom evidence (planned)
Players can download a CSV record from the Hugging Face game. Put the files in `data/classroom/` and rerun this cell to compare actual bids with the benchmark and the cheating rate among winners. Classroom play is exploratory evidence, not a population estimate.
"""),
    code(r"""
import glob
paths = sorted(glob.glob("data/classroom/*.csv"))
if paths:
    print(ca.summarize_classroom(paths))
else:
    print("No classroom records yet; planned after the September 28 symposium.")
"""),
    md("RESULTS_PLACEHOLDER"),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

RESULTS_FILE = os.path.join(ROOT, "tools", "results_section.md")
if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, encoding="utf-8") as fh:
        cells[-1] = md(fh.read())

for i, c in enumerate(cells):
    c["id"] = f"cell-{i:02d}"

with open(NB, "w", encoding="utf-8") as fh:
    json.dump(nb, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("Wrote", NB)
