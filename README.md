# Who Builds the Honest Chatbot? Subsidy Auction with a Compliance Audit

COMSCI/ECON 206 PS2 computational artifact. Synthetic inputs only; no human data.

**Question.** A government funds one company, from a fixed grant pool, to build a non-sycophantic chatbot. How do the payment rule (second-price vs. first-price reverse auction) and the audit strength change spending, spending risk, allocation efficiency, and whether an honest chatbot is delivered?

- Runnable notebook (Colab): [open in Google Colab](https://colab.research.google.com/drive/1XcVJLJuhNvaXDy526kxYN6wWfZH4XxHc?usp=sharing)
- Behavioral artifact (Hugging Face game, same model and seeds): [Honest_Chatbot Space](https://huggingface.co/spaces/dku-comsci-econ206-2026/Honest_Chatbot)
- Review-ready version: tag [`v1.0-review`](https://github.com/cmh9595/Honest-Chatbot-Subsidy-Auction/releases/tag/v1.0-review) (commit SHA recorded in the paper's Open Science Statement)

## Model in one paragraph

Four risk-neutral companies privately know their cost of building an honest chatbot (Uniform 0–100). The lowest sealed bid at or below the cap B = 80 wins. The **second-price** rule pays min(second-lowest bid, 80); the **first-price** rule pays the winner's bid. The winner then complies, or secretly ships a sycophantic chatbot that costs k = 10 more to tune but earns E = 30 more engagement; the regulator audits with probability p and fines F = 50. Backward induction: cheat iff E − k > pF, so p\* = 0.4. The bidding stage is a Bayesian game: truthful bidding is weakly dominant under second price; the first-price bid is the symmetric Bayesian-Nash bid with reserve 80. Full model, pseudocode, and parameter table are in the notebook.

## Run

**Colab (no installation).** Upload `PS2_chatbot_subsidy_auction.ipynb` to [Google Colab](https://colab.research.google.com/) (File → Upload notebook), or open it from GitHub once the repository is public, then choose **Runtime → Run all**. The first code cell writes `chatbot_auction.py`, so no other file is needed.

**Locally.**
```bash
pip install -r requirements.txt                 # matplotlib, figures only
python chatbot_auction.py                       # baseline comparison + audit sweep -> outputs/results.json
python -m unittest discover -s tests -v         # 18 tests, standard library only
jupyter nbconvert --to notebook --execute --inplace PS2_chatbot_subsidy_auction.ipynb
```

## Expected output (seed 206)

| Metric (50,000 auctions per rule, p = 0.5) | Second price | First price |
|---|---|---|
| Mean government spending (exact: 39.73) | 39.68 | 39.78 |
| SD of spending (budget risk) | 19.73 | 12.09 |
| Lowest-cost eligible company funded | 100.0% | 100.0% |
| Honest chatbot delivered | 99.9% | 99.9% |
| Mean winner profit | 19.79 | 19.88 |

Parameter change (audit sweep): for p < 0.4 the winner cheats under both rules, honest delivery falls to 0, and spending falls (p = 0.3: 34.41 / 34.86) because competition passes the cheating rent into lower bids. Figures: `outputs/figures/`.

## Files

| File | Purpose |
|---|---|
| `chatbot_auction.py` | Rules, benchmark bids, seeded generator, Monte Carlo, audit sweep, classroom-CSV summary, figures. |
| `PS2_chatbot_subsidy_auction.ipynb` | Colab notebook with saved outputs; embeds `chatbot_auction.py` verbatim. |
| `tests/test_chatbot_auction.py` | Theory checks (p\*, dominance, best response, revenue equivalence), rules, invalid inputs, and parity. |
| `tests/js_fixture.json` | Output of the Hugging Face game's `game_logic.js` (Node) for exact cross-language parity. |
| `tools/build_notebook.py` | Regenerates the notebook from the module and `tools/results_section.md`. |
| `outputs/results.json`, `outputs/figures/` | Saved results and the three figures. |
| `data/classroom/` | Place CSV records downloaded from the game here (none yet). |
| `AI_USE_DISCLOSURE.md` | AI assistance record. |

## Parity with the Hugging Face game

Both artifacts use the same parameters, rules, and generator (mulberry32 seeded by an FNV-1a hash of the session code). The test suite checks seeds, the random stream, full six-round schedules for four session codes, 82 benchmark bids, resolved rounds, and CSV parsing against `tests/js_fixture.json`. To refresh the fixture after changing the game, rerun the Node snippet recorded in `AI_USE_DISCLOSURE.md`.

## Fresh-run record

| Date | Environment | Command | Result |
|---|---|---|---|
| 2026-09-23 | macOS, Python 3.12.4, matplotlib 3.8.4 | `jupyter nbconvert --execute` on the notebook | all cells ran; "All checks passed." |
| 2026-09-23 | macOS, Python 3.12.4 and 3.14 (standard library only) | `python -m unittest discover -s tests` | 18 tests OK |
| 2026-09-23 | Google Colab, Python 3.13.15, matplotlib 3.10.0 | Runtime → Run all (cells executed 1–9 in order) | no errors; every printed number identical to the local run; "All checks passed." |
## Limits

Risk-neutral symmetric companies with independent uniform costs; one auction; losing companies are passive; audits are perfectly accurate; sycophancy is binary; E, k, and F are illustrative, not estimated. Classroom game records are exploratory evidence only.

## License

MIT (see `LICENSE`).
