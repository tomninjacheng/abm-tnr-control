# Viva Script — V1 Cat Management ABM

**Target length:** ~5 min demonstration + ~10 min individual Q&A.
**Grading criteria:** V1 understanding of model, V2 defence of assumptions and alternatives, V3 ownership of personal contributions.

Use this as a rehearsal script. Memorise the opening and the five likely-question talking points; the rest is for ad-hoc reference.

---

## 60-second opening — the pitch

> "Our research question is narrow and quantitative. At matched monthly intervention effort, culling will clearly produce lower prey mortality than TNR because sterilised cats continue to hunt — the direction is predictable from first principles. The interesting question is the **magnitude**: how many more cats does a TNR program need to process per month to achieve the same 10-year wildlife outcome as a culling program at 20 cats per month? We call this the **TNR effort multiplier**.
>
> The multiplier can be a finite factor like 2× or 3×, or it can be *infinite* — meaning no achievable TNR effort closes the gap, because sterilised cats keep hunting throughout their lifespans. Either answer is informative. The simulation produces this number, and we also test how it scales with immigration pressure and food availability."

---

## 2-minute model walkthrough — the "WHAT"

Live demonstration while you say:

> "The model is a 50×50 grid representing a 2.5 km × 2.5 km urban district. Each cell can hold food — four tiers from zero (food deserts) through low, medium, up to high at three commercial-zone hotspots. The yellow arrows are intact cats; after TNR they turn red. White dots are prey.
>
> Each monthly tick runs seven phases in order: cats move toward food and feed, immigration draws new cats from a Poisson distribution scaled by available food, cells regenerate food, prey random-walk, each prey rolls against predation if an adult cat is adjacent, cats and prey reproduce and age-die, and intervention processes up to N intact adult cats under the chosen strategy. There's a 12-month burn-in before intervention starts."

Click **setup**, then run **go**.

Point at the plots as they fill in:

> "Here's cumulative prey predation. Here's cat population by status. And here's the immigration rate — you can see it dropping as cats consume food and rising when culling creates vacancies."

---

## 2-minute preliminary results — the "RESULT"

Pull up the deterministic projection values or your actual Exp1 output:

> "From the deterministic projection used to validate the model before implementation: at matched effort of 20 cats per month, cumulative predation is around 160 under culling and 480 under TNR. Prey-years-lost favours culling by about 24 percentage points. Our Experiment 1 BehaviorSpace sweep tests whether TNR at higher effort can close that gap. If it can't within effort levels ≤ 40 cats per month, the structural finding is: TNR has an inherent wildlife ceiling that no reasonable program effort can push past."

---

## Likely V1 (understanding) questions

### Q: "Walk me through what happens in a single tick."

> "Seven phases in fixed order. First, every cat looks within territory radius three cells and moves to the cell with the highest current food, then consumes one unit of food. Second, immigration — the number of new intact adult cats is drawn from Poisson of base-immigration times the ratio of total current food to total food capacity, so sterilised and intact cats alike suppress immigration by eating. Third, food regenerates — each cell recovers 50% of its capacity. Fourth, prey random-walk within two cells. Fifth, predation — each prey checks whether any adult cat is within one cell; if yes, 10% monthly kill probability. Sixth, reproduction and mortality — intact adult females each roll a 17% chance of producing a litter of 4; all cats age one month; cats under 6 months die at 35% per month, adults at 2.5%. Prey are symmetric but with logistic reproduction scaled by one minus N over K prey. Seventh, if we're past burn-in, intervention: pick up to N intact adults at random, sterilise under TNR or remove under culling. Finally update the prey-years-lost accumulator and the kill counter, then tick."

### Q: "Why is immigration computed from pre-regen food?"

> "To make the immigration signal reflect the actual depletion caused by cats. If we computed it after regeneration, food would nearly always look full and immigration would be near-constant regardless of what the cats are doing. By reading post-feeding, pre-regen food, immigration responds to how hard cats are drawing on the resource — which is the vacuum-effect mechanism we want to capture."

### Q: "Why only adults hunt and get trapped?"

> "Three reasons. One: kittens are physically too small to be effective predators of ground-level birds and reptiles in reality. Two: real trapping programs target reproductively active cats, not nursing kittens with mothers nearby. Three: under our Set B rates, kittens are about half the population at any time, and 92% of them are destined to die naturally within six months — if random intervention selection included them, nearly half the effort would be wasted on nearly doomed animals. Restricting both hunt and trap eligibility to age ≥ 6 months is realistic and keeps intervention efficient."

---

## Likely V2 (defending assumptions, alternatives, limitations) questions

### Q: "That juvenile mortality rate is really high. Isn't 35% per month unrealistic?"

> "It's at the high end of the feral kitten mortality literature, which spans 50% to 90% first-year mortality. We adopted the high end deliberately. V1 doesn't explicitly model density-dependent processes — disease spreading in dense colonies, maternal food stress, kitten predation by other cats — but these are documented drivers of feral kitten death. We absorb them into this single rate. The alternative was adding three or four density-dependent mechanisms, which the proposal feedback explicitly asked us to cut. Per-female fecundity is held at literature-consistent values — two litters a year, four kittens per litter — so the biology that reviewers would check first is preserved."

### Q: "Why not use the vacuum effect through territorial exclusion rather than food?"

> "The vacuum effect as described in the literature is an empirical pattern — removing residents leads to more immigrants arriving — and the mechanism behind it hasn't been experimentally isolated. Candidates include territorial vacancy, unconsumed food, faded scent, or reduced intraspecific competition. We implement it through food consumption because food is directly measurable in the model — every cell tracks it, every cat consumes it. Territorial exclusion would require tracking per-cat territorial claims and immigrants would have to detect them, adding state and mechanism without changing the aggregate immigration dynamic our research question measures."

### Q: "Why no catchability heterogeneity? Belsare & Vanak have it."

> "That was the single biggest cut from our earlier model iteration, and we cut it because the proposal feedback asked for scope reduction. Catchability class — easy, moderate, hard — matters for *within-strategy* mechanics like diminishing returns as programs run longer. But our research question is *inter-strategy*: comparing TNR to culling at matched effort. Both strategies would be affected equally by catchability heterogeneity, so it doesn't change the comparative answer. It's documented as a candidate future extension in the handoff."

### Q: "What are the model's limitations?"

> "Six that we'd flag honestly. First, prey are generic — no specific taxon with calibrated life history. Second, cat sex is tracked but we don't model male-female proximity for mating; we use a direct monthly birth probability. Third, cats can't learn to avoid traps. Fourth, intervention is random across the grid; real programs target high-density areas. Fifth, sterilised cats hunt at the same rate as intact cats by default — that's the conservative assumption for TNR, so any TNR advantage we report is a lower bound. Sixth, the carrying-capacity ceiling comes from our high juvenile mortality rather than an explicit mechanism, so we can't tune cat density independently of mortality. All six are documented as future extensions."

### Q: "What if sterilised cats hunt less than intact?"

> "Our default sets `sterilised-hunting-fraction` to 1.0 — same rate as intact. We chose this as the conservative assumption per Longcore et al. 2009, who argued the evidence for reduced post-sterilisation hunting is mixed. If sterilisation did reduce hunting — say to 0.75 or 0.5 — TNR's wildlife-impact penalty would shrink. The multiplier we report under the baseline is therefore an upper bound; the true multiplier under reduced-hunting scenarios would be smaller. Any wildlife finding we claim for TNR holds *a fortiori* under reduced hunting."

### Q: "Why is the carrying-capacity story a bit hand-wavy?"

> "Honest answer: we tried an explicit K parameter early and rejected it. In the V1 model, population is bounded by rate balance: at the Set B rates, internal R₀ is near replacement, so unmanaged populations drift upward only through accumulated immigration. The ceiling emerges from food-mediated immigration suppression — once cats fully consume available food, immigration drops to near zero. It's not a hard cap but a soft asymptote. We validated this behaviour with a deterministic projection before implementation. The limitation is that we can't tune K and the demographic rates independently; they come as a package."

---

## Likely V3 (personal contribution) questions

### Q: "What was your personal contribution to this model?"

Prepare an honest, specific answer. Think about:

- Which design decisions did you specifically weigh in on?
- Did you write the ODD, the handoff, the model code, the test suite, the BehaviorSpace experiments, the validation projection?
- Did you do the pre-implementation deterministic projection?
- Which assumptions did you push back on or defend during the design discussions?
- What parts did your teammate drive versus you?

**Don't claim to have done everything.** Honest co-contribution is more defensible than inflated solo claims. The teaching team will cross-check with your teammate's answer.

### Q: "Walk me through a design choice that was contested in your team."

Pick one real example. Candidates:

- Whether to keep the hybrid strategy (we removed it in V1 for scope).
- The food-driven vs vacancy-driven immigration mechanism.
- Set B rate calibration vs lower-fecundity alternatives.
- Whether to make the model non-spatial.
- Whether to use prey-years-lost vs cumulative kills as the primary metric.

Describe: what you proposed, what your teammate proposed (or what the alternative was), how you resolved it, and what the trade-off was.

---

## 30-second close

> "The V1 model is scoped tightly around one quantitative question — the TNR effort multiplier — chosen deliberately because its direction is predictable but its magnitude is not. The model has 21 parameters, 5 cat state variables, 7 tick phases, and ~500 lines of NetLogo code. We've validated behaviour against a deterministic projection run before implementation. BehaviorSpace experiments are configured for the primary analysis plus sensitivity across immigration and food. Several mechanisms are documented as future extensions, each with clear rationale for being out of V1 scope."

---

## Rehearsal checklist

- [ ] Opening (60s) memorised
- [ ] Can describe each of the 7 phases without reading
- [ ] Can state the three answer shapes for the multiplier
- [ ] Can defend Set B rate calibration (specifically the high kitten mortality)
- [ ] Can defend food-driven immigration framing
- [ ] Can defend removing hybrid, catchability, prey habitat
- [ ] Can defend 100% sterilised hunting rate as conservative
- [ ] Can list six limitations honestly
- [ ] Prepared a personal-contribution answer that's specific and verifiable
- [ ] Prepared a contested-decision example
- [ ] Can run `setup` and `go` live
- [ ] Can modify a slider and re-run live
- [ ] Can read `run-all-tests` output live
