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
# Who builds the honest chatbot? A subsidy auction with a compliance audit
COMSCI/ECON 206 Computational Microeconomics · Autumn 2026 Session 1 · PS2 computational artifact

**Question.** A government funds one company, from a fixed grant pool, to build a non-sycophantic chatbot. How do the payment rule (second-price vs. first-price reverse auction) and the audit strength change government spending, spending risk, allocation efficiency, and whether an honest chatbot is actually delivered?

**Run.** *Runtime → Run all.* Python standard library plus matplotlib (preinstalled in Colab). Deterministic: seed 206 for all simulations. All inputs are synthetic; no human data. The first code cell writes `chatbot_auction.py`, identical to the GitHub file, so the notebook needs no other file.

| Symbol | Meaning | Baseline |
|---|---|---|
| $n$ | companies per auction | 4 |
| $c_i$ | private cost of building the honest chatbot, i.i.d. $U[0,100]$ | — |
| $B$ | grant cap = fixed subsidy pool (reserve price) | 80 |
| $E$ | extra engagement revenue from a sycophantic chatbot | 30 |
| $k$ | extra tuning cost of making it sycophantic | 10 |
| $p$ | probability the regulator audits the winner | 0.5 (swept 0–1) |
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
**Players.** $n$ risk-neutral AI companies (the government is the rule-maker, not a strategic player). **Information.** Each company privately knows its own honest-build cost $c_i$; costs are independent draws from $U[0,100]$ (independent private values); $B, E, k, p, F$ are common knowledge.

**Timing.** (1) Nature draws costs. (2) Companies submit sealed bids $b_i \in [0,100]$. (3) The lowest bid $\le B$ wins; the **second-price** rule pays $\min(b_{(2)}, B)$, the **first-price** rule pays $b_{(1)}$; if every bid exceeds $B$, nothing is awarded. (4) The winner chooses to comply (build honest, cost $c_i$) or cheat (build sycophantic, cost $c_i+k$, extra revenue $E$). (5) Nature audits with probability $p$; a cheater who is audited pays $F$.

**Payoffs.** Loser: 0. Winner: $P - c_i$ if it complies; $P - c_i + (E-k) - F\cdot\mathbf 1[\text{audited}]$ if it cheats.

**Solution.** Solve backward. At stage 4 the winner's choice does not depend on rivals' private costs, so it cheats iff $E-k > pF$, i.e. iff $p < p^* = (E-k)/F = 0.4$. Denote the resulting rent $\rho = \max(0, E-k-pF)$. The bidding stage is then a Bayesian game in effective cost $e_i = c_i - \rho$:
* second price: bidding $\max(0, e_i)$ is weakly dominant (Vickrey 1961), hence a Bayesian-Nash equilibrium;
* first price: the symmetric Bayesian-Nash bid with reserve $B$ is $\beta(e) = e + \dfrac{(M-e)^n - (M-B)^n}{n\,(M-e)^{n-1}}$ for $e<B$, with $M = 100-\rho$.

At the baseline $p=0.5$, $\rho=0$: compliance is rational and both rules have the same expected spending (revenue equivalence, Myerson 1981).

**Pseudocode (one auction).**
```
input: rule, costs c[1..n], audit draw u, parameters (B, E, k, p, F)
rho   <- max(0, E - k - p*F)
bid_i <- benchmark(c_i - rho, rule)          # max(0, e) or beta(e)
w     <- argmin_i bid_i  (ties: lowest index); if bid_w > B: no award, stop
pay   <- min(second-lowest bid, B) if rule = second-price else bid_w
cheat <- (rho > 0);  caught <- cheat and (u < p)
record pay, efficient = (c_w is the lowest cost <= B), honest = not cheat,
       winner profit = pay - c_w + cheat*(E - k) - caught*F
```
"""),
    code(r"""
cfg = ca.BASELINE
print(f"p* = (E-k)/F = {ca.audit_threshold(cfg):.2f};  E[cheat] - E[comply] at p = {cfg.audit_prob}: {ca.expected_cheat_value(cfg):+.1f}")
print(f"{'cost':>6} {'second-price bid':>17} {'first-price bid':>16}")
for c in (0, 20, 40, 60, 79, 90):
    print(f"{c:>6} {ca.benchmark_bid(c, 'second'):>17} {ca.benchmark_bid(c, 'first'):>16}")
"""),
    md(r"""
## Baseline comparison: second-price vs. first-price
50,000 auctions per rule. Both rules use the **same** cost and audit draws (common random numbers), so differences come from the rule alone. Metrics: mean and standard deviation of government spending (budget risk), share of auctions funding the lowest-cost eligible company (efficiency), share delivering an honest chatbot, spending per honest chatbot, and winner profit. `ca.main()` also writes every number to `outputs/results.json`.
"""),
    code(r"""
results = ca.main()
comp = results["comparison"]
"""),
    md(r"""
## Parameter change: audit strength
Sweep $p$ from 0 to 1 (step 0.05; 10,000 auctions per rule and value). Below $p^*=0.4$ the winner cheats, and competition passes the expected cheating rent $\rho$ into lower bids.
"""),
    code(r"""
print(f"{'p':>5} {'rule':>7} {'rent':>5} {'spending':>9} {'SD':>6} {'honest':>7} {'fines':>6}")
for r in results["audit_sweep"]:
    if r["audit_prob"] in (0.0, 0.2, 0.3, 0.35, 0.4, 0.5, 1.0):
        print(f"{r['audit_prob']:>5.2f} {r['rule']:>7} {r['rent']:>5.1f} {r['mean_spending']:>9.2f} "
              f"{r['sd_spending']:>6.2f} {r['honest_delivery_rate']:>7.3f} {r['mean_fines_collected']:>6.2f}")
"""),
    code(r"""
from IPython.display import Image, display
for path in ca.plot_results(cfg, comp, results["audit_sweep"]):
    display(Image(filename=path, width=460))
"""),
    md(r"""
## Parity with the Hugging Face game
The game uses the same rules and the same seeded generator (mulberry32 seeded by an FNV-1a hash of the session code). Session code `206` below reproduces the costs, audits, and rival bids a player sees in the game; `tests/js_fixture.json` in the repository stores the game's own output for automated comparison.
"""),
    code(r"""
s = ca.make_schedule("206")
print("seed", s["seed"], "| rule order", s["ruleOrder"])
print(f"{'round':>5} {'rule':>7} {'your cost':>9} {'rival costs':>20} {'rival bids':>20} {'audited':>8}")
for r in s["rounds"]:
    rb = [ca.benchmark_bid(c, r["rule"]) for c in r["rivalCosts"]]
    print(f"{r['round']:>5} {r['rule']:>7} {r['playerCost']:>9} {str(r['rivalCosts']):>20} {str(rb):>20} {str(r['audited']):>8}")
"""),
    md(r"""
## Verification
Checks on the theory and the rules. The repository runs the full suite, including exact parity with the game: `python -m unittest discover -s tests -v`.
"""),
    code(r"""
import math
from dataclasses import replace
assert abs(ca.audit_threshold(cfg) - 0.4) < 1e-12 and not ca.rational_cheats(cfg)
assert ca.rational_cheats(replace(cfg, audit_prob=0.3)) and not ca.rational_cheats(replace(cfg, audit_prob=0.4))
assert ca.benchmark_bid(40, "first") == 54.8 and ca.benchmark_bid(40, "second") == 40
assert ca.run_auction([30, 50, 40, 90], "second", 80) == (0, 40)
assert ca.run_auction([30, 50, 40, 90], "first", 80) == (0, 30)
assert ca.run_auction([30, 85, 90, 95], "second", 80) == (0, 80)
assert ca.run_auction([85, 81, 90, 95], "first", 80) == (-1, 0.0)
# Truthful bidding is weakly dominant under second price on a grid of rival bids.
for cost in (5, 40, 79, 85):
    for r1 in range(0, 101, 10):
        for r2 in range(0, 101, 10):
            pay = lambda b: (lambda w, p: p - cost if w == 0 else 0)(*ca.run_auction([b, r1, r2, 100], "second", 80, False))
            assert all(pay(cost) >= pay(d) - 1e-9 for d in range(0, 101, 5))
# Revenue equivalence: both simulated means lie within 4 standard errors of the exact value.
for rule in ca.RULES:
    se = comp[rule]["sd_spending"] / math.sqrt(comp[rule]["trials"])
    assert abs(comp[rule]["mean_spending"] - results["expected_spending_exact"]) < 4 * se
for bad in ([math.nan, 40], [-1, 40], [101, 40]):
    try:
        ca.run_auction(bad, "second", 80)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid bid accepted")
print("All checks passed.")
"""),
    md(r"""
## Classroom evidence (planned)
Players can download a CSV record from the Hugging Face game. Put the files in `data/classroom/` and rerun this cell to compare actual bids with the benchmark under each rule and the cheating rate among winners. Classroom play is exploratory evidence, not a population estimate.
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
