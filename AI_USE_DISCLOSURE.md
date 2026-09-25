# AI-use disclosure

| Item | Record |
|---|---|
| Tool / model | Cursor AI coding assistant (Claude model) |
| Dates | 2026-09-23 (first version); 2026-09-25 (simplified version) |
| Purpose | Draft the Hugging Face game, the Python engine, tests, notebook, and README from the author's model decisions. |
| Human decisions given to the tool | Chatbot-sycophancy framing; a subsidy tender plus a post-award compliance audit; sycophancy costs *extra* tuning k but earns engagement E; baseline N = 4, U(0,100), cap 80, E = 30, k = 10, F = 50; static HTML game; one-shot design with passive losers. On 2026-09-25 the author simplified the design to a single second-price rule with a strong audit (p = 0.5) in the game and a strong vs. weak (p = 0.3) audit comparison in the notebook, dropping the first-price rule. |
| Material suggestions by the tool | Treat the cap as a reserve price; derive p\* = 0.4; pass the cheating rent into bids when p < p\*; hide the theory until the game ends; session codes that seed identical draws for classmates; JS/Python parity via a shared generator. |
| Checks performed by the tool | Node checks of the game logic (9); Python unit tests (16), including exact parity with the game's output; full notebook execution; browser playthrough of the game. |
| Human review | The author reviewed the model, ran the notebook in Colab, and must record accepted/revised suggestions and verification in the paper's Appendix A. |
| Responsibility | The author is responsible for every claim, citation, and computation. |

## Regenerating `tests/js_fixture.json`

From the Hugging Face folder (with `game_logic.js`), run with Node:

```bash
node -e '
const L=require("./game_logic.js");const C=L.CONFIG;const fs=require("fs");
const weak=Object.assign({},C,{AUDIT_PROB:0.3});
const out={config:C,seeds:{},schedules:{},benchmarks:[],benchmarks_weak:[],rounds:[],csv:null,rng:[]};
for(const code of ["206","207","abc","课堂"]){out.seeds[code]=L.seedFromCode(code);out.schedules[code]=L.makeSchedule(code,C);}
const g=L.mulberry32(12345);for(let i=0;i<20;i++)out.rng.push(g());
for(let c=0;c<=100;c+=2.5){out.benchmarks.push([c,L.benchmarkBid(c,C)]);out.benchmarks_weak.push([c,L.benchmarkBid(c,weak)]);}
const s=out.schedules["206"];const bids=[2,20,30,90,10];const cheats=[true,false,false,false,true];
out.rounds=s.rounds.map((r,i)=>L.resolveRound(r,bids[i],cheats[i],C));
out.csv=L.toCSV(s,out.rounds,{strategy:"bid_below",clarity:"3",promise_reason:"gamble",note:"test, with \"quotes\""},C);
fs.writeFileSync("js_fixture.json",JSON.stringify(out,null,1));'
```
