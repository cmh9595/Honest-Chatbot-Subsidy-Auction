"""Who builds the honest chatbot? A reverse subsidy auction with a post-award compliance audit.

COMSCI/ECON 206 PS2 computational artifact. Python standard library only (matplotlib is used
only by the optional plotting helpers). The rules, benchmarks, and seeded random generator are
a line-by-line port of the Hugging Face game's game_logic.js, so a session code produces the
same costs, audits, and outcomes in both artifacts.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import asdict, dataclass, replace

MASK = 0xFFFFFFFF
RULES = ("second", "first")
RULE_NAMES = {"second": "Second-price", "first": "First-price"}
RIVAL_NAMES = ("Rival A", "Rival B", "Rival C")


@dataclass(frozen=True)
class Config:
    n: int = 4                     # companies per auction
    cost_max: float = 100.0        # private cost of the honest chatbot ~ Uniform(0, cost_max)
    cap: float = 80.0              # fixed subsidy pool: maximum grant (reserve price)
    engagement_gain: float = 30.0  # E: extra engagement revenue from a sycophantic chatbot
    extra_tuning_cost: float = 10.0  # k: extra cost of tuning the chatbot to be sycophantic
    audit_prob: float = 0.5        # p: probability the regulator audits the winner
    fine: float = 50.0             # F: fine when the audit finds sycophancy
    rounds_per_rule: int = 3       # game rounds under each rule

    def __post_init__(self):
        values = asdict(self)
        if any(not math.isfinite(v) for v in values.values()):
            raise ValueError("Parameters must be finite.")
        if self.n < 2 or self.rounds_per_rule < 1:
            raise ValueError("Need at least 2 companies and 1 round per rule.")
        if not 0 < self.cap <= self.cost_max:
            raise ValueError("Cap must lie in (0, cost_max].")
        if not 0 <= self.audit_prob <= 1:
            raise ValueError("Audit probability must lie in [0, 1].")
        if min(self.engagement_gain, self.extra_tuning_cost, self.fine) < 0:
            raise ValueError("Gain, tuning cost, and fine must be nonnegative.")
        if cheating_rent(self) > self.cost_max - self.cap:
            raise ValueError("Cheating rent must not exceed cost_max - cap for the first-price formula.")


def round1(x: float) -> float:
    """JavaScript Math.round(x * 10) / 10 (round half up), for exact parity with the game."""
    return math.floor(x * 10 + 0.5) / 10


def seed_from_code(code) -> int:
    """FNV-1a over UTF-16 code units, matching the game's seedFromCode."""
    data = str(code).encode("utf-16-le")
    h = 0x811C9DC5
    for i in range(0, len(data), 2):
        h ^= data[i] | (data[i + 1] << 8)
        h = (h * 0x01000193) & MASK
    return h


def mulberry32(seed: int):
    """32-bit mulberry32 generator returning floats in [0, 1), matching the game."""
    a = seed & MASK

    def imul(x, y):
        return (x * y) & MASK

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = imul(a ^ (a >> 15), a | 1)
        t ^= (t + imul(t ^ (t >> 7), t | 61)) & MASK
        return ((t ^ (t >> 14)) & MASK) / 4294967296

    return rng


def cheat_gain(cfg: Config) -> float:
    """Net gain from shipping the sycophantic chatbot before any fine: E - k."""
    return cfg.engagement_gain - cfg.extra_tuning_cost


def expected_cheat_value(cfg: Config) -> float:
    """Expected value of cheating relative to complying: (E - k) - pF."""
    return cheat_gain(cfg) - cfg.audit_prob * cfg.fine


def audit_threshold(cfg: Config) -> float:
    """Audit probability at which a risk-neutral winner is indifferent: p* = (E - k) / F."""
    return cheat_gain(cfg) / cfg.fine if cfg.fine > 0 else math.inf


def rational_cheats(cfg: Config) -> bool:
    return expected_cheat_value(cfg) > 1e-9


def cheating_rent(cfg: Config) -> float:
    """Expected cheating rent a rational bidder passes into its bid; zero when audits deter cheating."""
    return max(0.0, expected_cheat_value(cfg))


BASELINE = Config()


def benchmark_bid_exact(cost: float, rule: str, cfg: Config) -> float:
    """Risk-neutral IPV benchmark bid for a company with the given honest-build cost.

    Second price: bid the effective cost e = cost - rent, floored at 0 (weakly dominant).
    First price: symmetric BNE of a reverse auction with reserve `cap` and e ~ U[-rent, M],
        b(e) = e + [(M - e)^n - (M - cap)^n] / [n (M - e)^(n-1)],  M = cost_max - rent.
    """
    rent = cheating_rent(cfg)
    e = cost - rent
    if rule == "second":
        return max(0.0, e)
    if rule != "first":
        raise ValueError(f"Unknown rule: {rule}")
    if e >= cfg.cap:
        return e
    m, n = cfg.cost_max - rent, cfg.n
    return e + ((m - e) ** n - (m - cfg.cap) ** n) / (n * (m - e) ** (n - 1))


def benchmark_bid(cost: float, rule: str, cfg: Config = BASELINE) -> float:
    """Benchmark bid rounded to 0.1, as displayed and used by the game's computer rivals."""
    return round1(benchmark_bid_exact(cost, rule, cfg))


def valid_bid(bid) -> bool:
    return isinstance(bid, (int, float)) and not isinstance(bid, bool) and math.isfinite(bid) and 0 <= bid <= 100


def run_auction(bids, rule: str, cap: float, rounding: bool = True):
    """Lowest bid <= cap wins; ties go to the lower index (the player is index 0).

    Second price pays min(second-lowest bid, cap); first price pays the winner's bid.
    Returns (winner, payment) with winner = -1 when no bid is at or below the cap.
    """
    if len(bids) < 2 or not all(valid_bid(b) for b in bids):
        raise ValueError("Bids must be at least two numbers between 0 and 100.")
    order = sorted(range(len(bids)), key=lambda i: (bids[i], i))
    winner = order[0]
    if bids[winner] > cap:
        return -1, 0.0
    if rule == "second":
        payment = min(bids[order[1]], cap)
    elif rule == "first":
        payment = bids[winner]
    else:
        raise ValueError(f"Unknown rule: {rule}")
    return winner, round1(payment) if rounding else payment


def is_efficient(costs, winner: int, cap: float) -> bool:
    """True when the lowest-cost company with cost <= cap wins, or nobody wins because all costs exceed cap."""
    eligible = [i for i, c in enumerate(costs) if c <= cap]
    if not eligible:
        return winner == -1
    best = min(eligible, key=lambda i: (costs[i], i))
    return winner != -1 and costs[winner] == costs[best]


def round_profit(won: bool, payment: float, cost: float, cheat: bool, caught: bool,
                 cfg: Config = BASELINE, rounding: bool = True) -> float:
    if not won:
        return 0.0
    profit = payment - cost
    if cheat:
        profit += cheat_gain(cfg) - (cfg.fine if caught else 0.0)
    return round1(profit) if rounding else profit


def make_schedule(code, cfg: Config = BASELINE) -> dict:
    """Deterministic game schedule: costs, audits, and rule order for a session code."""
    seed = seed_from_code(code)
    rng = mulberry32(seed)
    rule_order = ["second", "first"] if seed % 2 == 0 else ["first", "second"]
    rounds = []
    for i in range(2 * cfg.rounds_per_rule):
        player_cost = round1(rng() * cfg.cost_max)
        rival_costs = [round1(rng() * cfg.cost_max) for _ in range(cfg.n - 1)]
        audited = rng() < cfg.audit_prob
        rounds.append({
            "round": i + 1,
            "rule": rule_order[i // cfg.rounds_per_rule],
            "playerCost": player_cost,
            "rivalCosts": rival_costs,
            "audited": audited,
        })
    return {"code": str(code), "seed": seed, "ruleOrder": rule_order, "rounds": rounds}


def resolve_round(r: dict, player_bid: float, player_cheats: bool, cfg: Config = BASELINE) -> dict:
    """One game round given the player's bid and comply/cheat choice (same fields as the game)."""
    rival_bids = [benchmark_bid(c, r["rule"], cfg) for c in r["rivalCosts"]]
    bids = [player_bid] + rival_bids
    costs = [r["playerCost"]] + r["rivalCosts"]
    winner, payment = run_auction(bids, r["rule"], cfg.cap)
    cheated = None
    if winner == 0:
        cheated = bool(player_cheats)
    elif winner > 0:
        cheated = rational_cheats(cfg)
    caught = cheated is True and r["audited"]
    bench = benchmark_bid(r["playerCost"], r["rule"], cfg)
    return {
        "round": r["round"],
        "rule": r["rule"],
        "playerCost": r["playerCost"],
        "playerBid": player_bid,
        "benchmarkBid": bench,
        "bidGap": round1(player_bid - bench),
        "rivalCosts": list(r["rivalCosts"]),
        "rivalBids": rival_bids,
        "winner": winner,
        "winnerName": "Nobody" if winner == -1 else "You" if winner == 0 else RIVAL_NAMES[winner - 1],
        "payment": payment,
        "efficient": is_efficient(costs, winner, cfg.cap),
        "cheated": cheated,
        "audited": None if winner == -1 else r["audited"],
        "caught": caught,
        "honestDelivered": None if winner == -1 else cheated is False,
        "playerProfit": round_profit(winner == 0, payment, r["playerCost"], cheated, caught, cfg),
    }


def simulate(rule: str, cfg: Config = BASELINE, trials: int = 20000, seed: int = 206) -> dict:
    """Monte Carlo of the rational benchmark: all n companies bid the benchmark, the winner
    complies or cheats rationally, and the regulator audits with probability p.

    Uses unrounded bids and payments. The same seed gives both rules identical cost and audit
    draws (common random numbers), so differences come from the rule alone.
    """
    if trials < 1:
        raise ValueError("trials must be positive.")
    rng = mulberry32(seed)
    cheats = rational_cheats(cfg)
    payments, winner_costs, profits = [], [], []
    awarded = efficient = honest = fines = 0
    for _ in range(trials):
        costs = [rng() * cfg.cost_max for _ in range(cfg.n)]
        audited = rng() < cfg.audit_prob
        bids = [min(100.0, benchmark_bid_exact(c, rule, cfg)) for c in costs]
        winner, payment = run_auction(bids, rule, cfg.cap, rounding=False)
        efficient += is_efficient(costs, winner, cfg.cap)
        payments.append(payment)
        if winner == -1:
            continue
        awarded += 1
        caught = cheats and audited
        honest += not cheats
        fines += cfg.fine if caught else 0.0
        winner_costs.append(costs[winner])
        profits.append(round_profit(True, payment, costs[winner], cheats, caught, cfg, rounding=False))
    total_spend = sum(payments)
    return {
        "rule": rule,
        "trials": trials,
        "seed": seed,
        "mean_spending": total_spend / trials,
        "sd_spending": statistics.pstdev(payments),
        "mean_payment_when_awarded": total_spend / awarded if awarded else None,
        "award_rate": awarded / trials,
        "efficient_rate": efficient / trials,
        "honest_delivery_rate": honest / trials,
        "spending_per_honest_chatbot": total_spend / honest if honest else None,
        "mean_winner_cost": statistics.fmean(winner_costs) if winner_costs else None,
        "mean_winner_profit": statistics.fmean(profits) if profits else None,
        "mean_fines_collected": fines / trials,
        "winner_cheats": cheats,
    }


def compare_rules(cfg: Config = BASELINE, trials: int = 20000, seed: int = 206) -> dict:
    return {rule: simulate(rule, cfg, trials, seed) for rule in RULES}


def audit_sweep(cfg: Config = BASELINE, probs=None, trials: int = 10000, seed: int = 206) -> list:
    """Parameter change: vary the audit probability p and rerun both rules."""
    probs = probs if probs is not None else [i / 20 for i in range(21)]
    rows = []
    for p in probs:
        c = replace(cfg, audit_prob=p)
        for rule in RULES:
            s = simulate(rule, c, trials, seed)
            rows.append({"audit_prob": p, "rule": rule, "rent": cheating_rent(c), **{
                k: s[k] for k in ("mean_spending", "sd_spending", "honest_delivery_rate",
                                  "spending_per_honest_chatbot", "mean_winner_profit", "mean_fines_collected")}})
    return rows


def expected_spending_exact(cfg: Config = BASELINE, steps: int = 20000) -> float:
    """Expected second-price spending with no cheating rent, by midpoint integration:
    E[min(C_(2), cap) * 1{C_(1) <= cap}]. Revenue equivalence says first price matches."""
    n, cmax, cap = cfg.n, cfg.cost_max, cfg.cap
    total, h = 0.0, cmax / steps
    for i in range(steps):
        x = (i + 0.5) * h
        f = x / cmax
        density = n * (n - 1) * f * (1 - f) ** (n - 2) / cmax  # second-lowest of n uniform costs
        total += min(x, cap) * density * h
    # If every cost exceeds the cap (then C_(2) > cap too) nothing is paid instead of cap.
    return total - cap * (1 - cap / cmax) ** n


def summarize_classroom(paths) -> dict:
    """Aggregates CSV records downloaded from the Hugging Face game (one file per player)."""
    rows = []
    for path in paths:
        with open(path, newline="", encoding="utf-8") as fh:
            rows.extend(csv.DictReader(fh))
    out = {"players": len(paths), "rounds": len(rows)}
    for rule in RULES:
        rr = [r for r in rows if r["rule"] == rule]
        gaps = [float(r["bid_minus_benchmark"]) for r in rr]
        wins = [r for r in rr if r["winner"] == "You"]
        out[rule] = {
            "rounds": len(rr),
            "mean_bid_gap": statistics.fmean(gaps) if gaps else None,
            "share_within_1_of_benchmark": sum(abs(g) <= 1 for g in gaps) / len(gaps) if gaps else None,
            "player_wins": len(wins),
            "player_cheat_rate": sum(r["winner_cheated"] == "true" for r in wins) / len(wins) if wins else None,
        }
    return out


def plot_results(cfg: Config, comparison: dict, sweep: list, out_dir: str = "outputs/figures"):
    """Three figures used in the paper and poster. Requires matplotlib."""
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    paths = []

    costs = [i / 10 for i in range(0, int(cfg.cost_max * 10) + 1)]
    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.plot(costs, [benchmark_bid_exact(c, "second", cfg) for c in costs], label="Second-price: bid = cost")
    ax.plot(costs, [benchmark_bid_exact(c, "first", cfg) for c in costs], label="First-price: equilibrium bid")
    ax.axhline(cfg.cap, color="grey", ls="--", lw=1, label=f"Grant cap = {cfg.cap:g}")
    ax.set_xlabel("Private cost of the honest chatbot")
    ax.set_ylabel("Benchmark bid")
    ax.set_title("Rational bids under the two rules")
    ax.legend(fontsize=8)
    fig.tight_layout()
    paths.append(os.path.join(out_dir, "fig1_bid_functions.png"))
    fig.savefig(paths[-1], dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.6))
    rules = list(RULES)
    means = [comparison[r]["mean_spending"] for r in rules]
    sds = [comparison[r]["sd_spending"] for r in rules]
    ax.bar([RULE_NAMES[r] for r in rules], means, yerr=sds, capsize=6, color=["#14877d", "#315efb"])
    for i, (m, s) in enumerate(zip(means, sds)):
        ax.text(i, m + s + 1, f"mean {m:.1f}\nSD {s:.1f}", ha="center", fontsize=8)
    ax.set_ylabel("Government spending per auction")
    ax.set_title("Same expected spending, different risk")
    ax.set_ylim(0, max(m + s for m, s in zip(means, sds)) + 12)
    fig.tight_layout()
    paths.append(os.path.join(out_dir, "fig2_spending_by_rule.png"))
    fig.savefig(paths[-1], dpi=200)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(5.4, 3.6))
    ax2 = ax1.twinx()
    for rule, color in (("second", "#14877d"), ("first", "#315efb")):
        rows = [r for r in sweep if r["rule"] == rule]
        ps = [r["audit_prob"] for r in rows]
        ax1.plot(ps, [r["mean_spending"] for r in rows], color=color, label=f"{RULE_NAMES[rule]} spending")
    rows = [r for r in sweep if r["rule"] == "second"]
    ax2.step([r["audit_prob"] for r in rows], [r["honest_delivery_rate"] for r in rows], where="post",
             color="#b4461f", ls="--", label="Honest chatbot delivered (both rules)")
    ax1.axvline(audit_threshold(cfg), color="grey", lw=1, ls=":")
    ax1.text(audit_threshold(cfg) + 0.01, 0.9, f"p* = {audit_threshold(cfg):.2f}", fontsize=8,
             transform=ax1.get_xaxis_transform())
    ax1.set_xlabel("Audit probability p")
    ax1.set_ylabel("Mean government spending")
    ax1.set_ylim(0, 1.25 * max(r["mean_spending"] for r in sweep))
    ax2.set_ylabel("Honest chatbot share")
    ax2.set_ylim(-0.05, 1.25)
    ax1.set_title("Weak audits look cheaper but buy sycophancy")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=7, loc="center right")
    fig.tight_layout()
    paths.append(os.path.join(out_dir, "fig3_audit_sweep.png"))
    fig.savefig(paths[-1], dpi=200)
    plt.close(fig)
    return paths


def main(out_path: str = "outputs/results.json", trials: int = 50000, seed: int = 206) -> dict:
    import os
    import platform

    cfg = BASELINE
    comparison = compare_rules(cfg, trials, seed)
    sweep = audit_sweep(cfg, seed=seed)
    results = {
        "python": platform.python_version(),
        "config": asdict(cfg),
        "audit_threshold": audit_threshold(cfg),
        "expected_cheat_value": expected_cheat_value(cfg),
        "expected_spending_exact": expected_spending_exact(cfg),
        "comparison": comparison,
        "audit_sweep": sweep,
        "game_session_206": make_schedule("206", cfg),
    }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    print(f"Python {results['python']} | seed {seed} | {trials} auctions per rule")
    print(f"p* = {results['audit_threshold']:.2f}; E[cheat - comply] at p = {cfg.audit_prob} is "
          f"{results['expected_cheat_value']:.1f}")
    print(f"Exact expected spending (both rules): {results['expected_spending_exact']:.2f}")
    print(f"{'metric':32s}{'second':>10s}{'first':>10s}")
    for key in ("mean_spending", "sd_spending", "efficient_rate", "honest_delivery_rate",
                "mean_winner_cost", "mean_winner_profit"):
        print(f"{key:32s}{comparison['second'][key]:10.3f}{comparison['first'][key]:10.3f}")
    print(f"Wrote {out_path}")
    return results


if __name__ == "__main__":
    main()
