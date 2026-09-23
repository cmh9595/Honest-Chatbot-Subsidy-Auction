# AI-use disclosure

| Item | Record |
|---|---|
| Tool / model | Cursor AI coding assistant (Claude model) |
| Date | 2026-09-23 |
| Purpose | Draft the Hugging Face game, the Python engine, tests, notebook, and README from the team's model decisions. |
| Human decisions given to the tool | Chatbot-sycophancy framing; two-layer model (subsidy auction + post-award compliance audit); sycophancy costs *extra* tuning k but earns engagement E; compare second- vs. first-price reverse auctions; baseline N = 4, U(0,100), cap 80, E = 30, k = 10, F = 50; static HTML game; one-shot design with passive losers. |
| Material suggestions by the tool | Treat the cap as a reserve price; fix p = 0.5 in the game with p\* = 0.4 as a derived threshold; pass the cheating rent into bids when p < p\*; report spending SD as budget risk; hide the theory until the game ends; session codes that seed identical draws for classmates; JS/Python parity via a shared generator. |
| Checks performed by the tool | Node checks of the game logic (11); Python unit tests (18), including exact parity with the game's output; full notebook execution; manual browser playthrough of the game. |
| Human review required | Authors must verify the derivations (first-price bid with reserve, p\*), rerun the notebook in Colab, decide on the license, and record accepted/revised suggestions and their own verification in the paper's Appendix A. |
| Responsibility | The human authors are responsible for every claim, citation, and computation. |

## Regenerating `tests/js_fixture.json`

From the Hugging Face folder (with `game_logic.js`), run with Node:

```bash
node -e '
const L=require("./game_logic.js");const C=L.CONFIG;const fs=require("fs");
const out={config:C,seeds:{},schedules:{},benchmarks:[],rounds:[],csv:null,rng:[]};
for(const code of ["206","207","abc","课堂"]){out.seeds[code]=L.seedFromCode(code);out.schedules[code]=L.makeSchedule(code,C);}
const g=L.mulberry32(12345);for(let i=0;i<20;i++)out.rng.push(g());
for(let c=0;c<=100;c+=2.5)for(const rule of ["second","first"])out.benchmarks.push([c,rule,L.benchmarkBid(c,rule,C)]);
const s=out.schedules["206"];const bids=[30,20,71,90,10,59.9];const cheats=[false,true,false,false,false,false];
out.rounds=s.rounds.map((r,i)=>L.resolveRound(r,bids[i],cheats[i],C));
out.csv=L.toCSV(s,out.rounds,{strategy_second:"bid_cost",clarity_second:"5",strategy_first:"bid_below",clarity_first:"3",promise_reason:"gamble",note:"test, with \"quotes\""},C);
fs.writeFileSync("js_fixture.json",JSON.stringify(out,null,1));'
```
