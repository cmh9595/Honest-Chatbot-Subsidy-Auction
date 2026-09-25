# Who Builds the Honest Chatbot? A Subsidy Tender with a Compliance Audit

COMSCI/ECON 206 PS2 computational artifact · Muhan Chen. Synthetic inputs only; no human data.

**Question.** A government pays one company, from a fixed grant, to build a non-sycophantic chatbot. It runs a second-price tender and then audits the winner. How strong must the audit be for the grant to buy honesty, and what happens to spending when the audit is weak?

- Runnable notebook (Colab): [open in Google Colab](https://colab.research.google.com/drive/1XcVJLJuhNvaXDy526kxYN6wWfZH4XxHc?usp=sharing)
- Behavioral artifact (Hugging Face game, same model and seeds): [Honest_Chatbot Space](https://huggingface.co/spaces/dku-comsci-econ206-2026/Honest_Chatbot)
- Review-ready version: tag [`v1.1-review`](https://github.com/cmh9595/Honest-Chatbot-Subsidy-Auction/releases/tag/v1.1-review) (commit SHA recorded in the paper's Open Science Statement)

## Model in one paragraph

Four risk-neutral companies privately know their cost of building an honest chatbot (Uniform 0–100). In a reverse second-price tender, the lowest sealed bid at or below the cap B = 80 wins and is paid the second-lowest bid (capped at 80). The winner then complies, or secretly ships a sycophantic chatbot that costs k = 10 more to tune but earns E = 30 more engagement; the regulator audits with probability p and fines F = 50. Backward induction: cheat iff E − k > pF, so p\* = 0.4. In the tender, bidding one's cost is weakly dominant when audits deter cheating; when they do not, companies bid the expected cheating rent E − k − pF below cost. Full model, pseudocode, and parameter table are in the notebook.

## Run

**Colab (no installation).** Upload `PS2_chatbot_subsidy_auction.ipynb` to [Google Colab](https://colab.research.google.com/) (File → Upload notebook), or open it from GitHub, then choose **Runtime → Run all**. The first code cell writes `chatbot_auction.py`, so no other file is needed.

**Locally.**
```bash
pip install -r requirements.txt                 # matplotlib, figures only
python chatbot_auction.py                       # strong vs weak audit + audit sweep -> outputs/results.json
python -m unittest discover -s tests -v         # 16 tests, standard library only
jupyter nbconvert --to notebook --execute --inplace PS2_chatbot_subsidy_auction.ipynb
```

## Expected output (seed 206, 50,000 tenders per setting)

| Metric | Strong audit p = 0.5 | Weak audit p = 0.3 |
|---|---|---|
| Expected cheating rent | 0 | 5 |
| Mean government spending (exact, strong: 39.73) | 39.68 | 34.89 |
| Lowest-cost eligible company funded | 100.0% | 99.1% |
| Honest chatbot delivered | 99.9% | 0.0% |
| Mean winner profit | 19.79 | 19.96 |
| Mean fines collected | 0.00 | 14.90 |

Parameter change (audit sweep): for p < 0.4 the winner cheats, honest delivery is 0, and spending falls with p (20.79 at p = 0); for p ≥ 0.4 nothing changes (39.23). Figures: `outputs/figures/`.

## Files

| File | Purpose |
|---|---|
| `chatbot_auction.py` | Rules, benchmark bids, seeded generator, Monte Carlo, strong vs weak comparison, audit sweep, classroom-CSV summary, figures. |
| `PS2_chatbot_subsidy_auction.ipynb` | Colab notebook with saved outputs; embeds `chatbot_auction.py` verbatim. |
| `tests/test_chatbot_auction.py` | Theory checks (p\*, dominance, rent, expected spending), rules, invalid inputs, and parity. |
| `tests/js_fixture.json` | Output of the Hugging Face game's `game_logic.js` (Node) for exact cross-language parity. |
| `tools/build_notebook.py` | Regenerates the notebook from the module and `tools/results_section.md`. |
| `outputs/results.json`, `outputs/figures/` | Saved results and the three figures. |
| `data/classroom/` | Place CSV records downloaded from the game here (none yet). |
| `AI_USE_DISCLOSURE.md` | AI assistance record. |

## Parity with the Hugging Face game

Both artifacts use the same parameters, rules, and generator (mulberry32 seeded by an FNV-1a hash of the session code). The test suite checks seeds, the random stream, five-round schedules for four session codes, 82 benchmark bids under both audit strengths, resolved rounds, and CSV parsing against `tests/js_fixture.json`. To refresh the fixture after changing the game, rerun the Node snippet recorded in `AI_USE_DISCLOSURE.md`.

## Fresh-run record

| Date | Environment | Command | Result |
|---|---|---|---|
| 2026-09-25 | macOS, Python 3.12.4, matplotlib 3.8.4 | `jupyter nbconvert --execute` on the notebook | all cells ran; "All checks passed." |
| 2026-09-25 | macOS, Python 3.12.4 and 3.14 (standard library only) | `python -m unittest discover -s tests` | 16 tests OK |
| `[date]` | Google Colab | Runtime → Run all | `[record the result]` |

## Limits

Risk-neutral symmetric companies with independent uniform costs; one tender; losing companies are passive; audits are perfectly accurate; sycophancy is binary; E, k, and F are illustrative, not estimated. Classroom game records are exploratory evidence only.

## License

MIT (see `LICENSE`).
