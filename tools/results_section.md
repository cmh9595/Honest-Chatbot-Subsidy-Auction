## Results and research limits
Actual outputs above (seed 206; 50,000 tenders per setting; 10,000 per value in the sweep). These are model calculations, not observed firm or regulator behavior.

* **Strong audit ($p=0.5$).** Complying is rational ($E[\text{cheat}]-E[\text{comply}]=-5$), so every company bids its cost. Mean government spending is 39.68 (exact value 39.73). The lowest-cost eligible company wins essentially every tender, and an honest chatbot is delivered in 99.9% of tenders (in $0.2^4=0.16\%$ of tenders every cost exceeds the cap and nothing is awarded).
* **Weak audit ($p=0.3$).** Cheating pays ($+5$ in expectation), so every winner ships the flattering chatbot and the honest-delivery rate is 0. Spending *falls* to 34.89, and fines of about 14.90 per tender come in, because competition passes the expected cheating rent $\rho=5$ into lower bids. Winner profit barely changes (19.79 vs. 19.96): the rent goes to the government as lower prices, while users bear the flattery.
* **Parameter change.** The sweep shows a sharp switch at $p^\ast=0.4$: below it, honest delivery is 0 and spending falls with $p$ (20.79 at $p=0$, 34.41 at $p=0.3$); above it, nothing changes (39.23), so audits stronger than $p^\ast$ only add audit costs.
* **Project decision supported.** A grant for honest chatbots must come with an audit at $p \ge p^\ast$. A cheaper-than-expected tender is a warning sign that audits are too weak. Left unresolved: whether real bidders bid their cost and keep the promise (classroom evidence, planned).

**Limits.** Risk-neutral, symmetric companies with independent uniform costs; one tender; losing companies are passive; audits detect sycophancy perfectly; sycophancy is binary; $E$, $k$, $F$ are illustrative values, not estimates. Collusion, risk aversion, correlated costs, or imperfect audits could change both the bids and the threshold.

## Sources and AI assistance
Vickrey (1961), *Journal of Finance* 16(1):8–37, doi:10.1111/j.1540-6261.1961.tb02789.x. Becker (1968), *Journal of Political Economy* 76(2):169–217, doi:10.1086/259394. Harsanyi (1967), *Management Science* 14(3):159–182, doi:10.1287/mnsc.14.3.159.

An AI coding assistant (Cursor, Claude model) drafted the code, tests, and explanatory text on September 23 and 25, 2026, from the author's model decisions (a second-price tender, an extra tuning cost for sycophancy, a strong vs. weak audit comparison, baseline parameters). Saved outputs were produced by executing this notebook top to bottom in a fresh kernel. The author reviewed the model and reran the notebook in Colab.
