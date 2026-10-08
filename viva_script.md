# Viva Script — V1 Cat Management ABM (Australian Context)

**Target length:** ~5 min demonstration + ~10 min individual Q&A.
**Grading criteria:** V1 understanding of model, V2 defence of assumptions and alternatives, V3 ownership of personal contributions.

Use this as a rehearsal script. Memorise the opening and the five likely-question talking points; the rest is for ad-hoc reference.

**Context anchoring (memorise these two citations):**
- **Cat demographics:** Denny & Dickman (2010), *Review of Cat Ecology and Management Strategies in Australia*, Invasive Animals CRC — specifically §3.5–3.9 for breeding/survival rates, and Table 1 (p.13) for Australian cat densities.
- **Prey species:** Superb Fairy-wren (*Malurus cyaneus*), Rowley (1965) foundational monograph + Russell & Rowley (1993) demographic data from closely related Splendid Fairy-wren.

---

## 60-second opening — the pitch

> "Our research question is one sentence: at matched monthly intervention effort, how many additional prey deaths does TNR cause per cat spared from culling over 10 years?
>
> The direction is predictable — culling produces fewer prey deaths because sterilised cats keep hunting. The *quantitative exchange rate* is not. It could be close to zero (TNR is nearly as effective as culling for wildlife) or in the tens (each sterilised cat prevents many prey deaths over its remaining lifespan). The simulation produces this number. From our runs, the headline at the Gunther et al. 80% coverage reference effort is roughly 0.4 prey deaths per cat spared — meaning each cat we killed under culling saved less than half a prey animal over the decade. That's an order of magnitude below the naive 'each cat kills many prey per year' expectation, because immigration backfill and sterilised cats continuing to hunt eat most of the apparent benefit."

---

## 2-minute model walkthrough — the "WHAT"

Live demonstration while you say:

> "The model is a 50×50 grid representing a Melbourne-scale urban district of 2.5 km × 2.5 km. Starting with 300 cats on 625 hectares — 48 cats per square kilometre, which sits inside the 19 to 90 per square kilometre range Wilson et al. 1994 measured in Canberra highly-modified habitats, reported in Denny & Dickman 2010. Each cell can hold food — four tiers from zero food-deserts through low, medium, up to high at three commercial-zone hotspots. The yellow arrows are intact cats; after TNR they turn red. White dots are prey — Superb Fairy-wrens, the anchor species.
>
> Each monthly tick runs seven phases in order: cats move toward food and feed, immigration draws new cats from a Poisson distribution scaled by available food, cells regenerate food, prey random-walk, each prey rolls against predation if an adult cat is adjacent, cats and prey reproduce and age-die, and intervention processes up to N intact adult cats under the chosen strategy. There's a 12-month burn-in before intervention starts."

Click **setup**, then run **go**.

Point at the plots as they fill in:

> "Here's cumulative prey predation. Here's cat population by status. And here's the immigration rate — you can see it dropping as cats consume food and rising when culling creates vacancies."

---

## 2-minute preliminary results — the "RESULT"

Pull up the deterministic projection values or your actual Exp1 output:

> "At matched effort of 20 cats per month — our reference, chosen as the Gunther et al. 80% annual coverage threshold — cumulative predation is around 370 under culling and 480 under TNR. The gap is 110 extra prey deaths, divided by ~300 cats killed in the culling scenario, gives roughly 0.4 prey saved per cat killed. That's the headline exchange rate.
>
> We also observed a secondary structural finding: TNR at 40 cats per month is nearly indistinguishable from TNR at 20 — the total cat population stays near 300 regardless of effort. This is because sterilised cats accumulate and keep hunting while immigrants and juveniles refill the intact pool. TNR has a wildlife-impact floor that higher effort does not push past."

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

### Q: "Where did 20 cats per month come from? Is there a reference for it?"

> "At our initial population of 300 cats on a 2.5 km × 2.5 km district, 20 cats per month corresponds to 240 processings per year — 80% annual coverage of the initial population. That matches Gunther et al. 2022, a 12-year TNR field study in Rishon-LeZion, Israel, where 80% neutering coverage was the aggressive-but-realistic upper threshold a well-resourced local program could sustain. McCarthy, Levine and Reed 2013 identified 57% annual capture as the minimum for sustained decline, which maps to 15 cats per month at our density. Our sweep from 0 to 40 therefore spans well-below-minimum through aggressive-but-realistic up to operationally unrealistic — so the comparison covers the policy-relevant range."

### Q: "How is intervention intensity actually decided in practice?"

> "Three frameworks. First, percent-of-population targets — the literature uses coverage percentages, with 57% as a lower bound from McCarthy et al. and 80% as an aggressive-but-achievable upper threshold from Gunther et al. Second, operational capacity — a community TNR clinic typically processes 20 to 50 cats per month regardless of coverage, driven by vet availability and trap inventory. Third, opportunistic — many programs catch whatever is brought in without an explicit target. Our reference anchors to the first framework and we sweep across the second's typical range."

### Q: "What's your juvenile mortality rate, and why?"

> "0.25 per month, giving (1 minus 0.25) to the sixth power equals 17.8% survival to 6 months. The direct anchor is Mirmovitch 1995 in Jerusalem: seven out of forty-three urban feral kittens survived to six months — 16%, essentially the number our rate produces. That's cited in Denny & Dickman 2010 section 3.7, page 18. Combined with 0.17 monthly birth probability — which gives 2.04 litters per year, matching Jones & Coman 1982a's two litters per year — and litter size four, which sits in the 4.1 to 4.7 prenatal range Denny & Dickman report, internal R₀ comes out around 1.5. That gives roughly 20% annual unmanaged growth. The 0.025 adult rate means mean adult lifespan 3.3 years, consistent with Warner 1985's 'free-ranging survival beyond 3 to 5 years is rare.' Every one of our four cat demographic parameters maps to a specific line in Denny & Dickman."

### Q: "Why not use the vacuum effect through territorial exclusion rather than food?"

> "The vacuum effect as described in the literature is an empirical pattern — removing residents leads to more immigrants arriving — and the mechanism behind it hasn't been experimentally isolated. Candidates include territorial vacancy, unconsumed food, faded scent, or reduced intraspecific competition. We implement it through food consumption because food is directly measurable in the model — every cell tracks it, every cat consumes it. Territorial exclusion would require tracking per-cat territorial claims and immigrants would have to detect them, adding state and mechanism without changing the aggregate immigration dynamic our research question measures."

### Q: "Why Superb Fairy-wren as the prey species? Why not a mammal?"

> "Three reasons. First, data availability — Rowley 1965 gives us a foundational life-history monograph from Gungahlin ACT with clutch size, broods per year, longevity. Russell & Rowley 1993 on the closely related Splendid Fairy-wren gives adult annual survival at 0.59 for females, 0.70 for males — the closest demographic analogue we have. The ANU 30-year Canberra dataset gives us normal-year adult winter loss around 20%, which lets us sanity-check. Second, ecological realism — Fairy-wrens genuinely live in urban Melbourne alongside stray cats, which is exactly the system our model simulates. We considered Eastern Barred Bandicoot but on the Victorian mainland they're now almost entirely inside predator-proof fences, so the cat-prey co-occurrence we model doesn't apply. Third, vulnerability — under Dickman's rank-scoring system in Table 4 of Denny & Dickman, Fairy-wrens score high: 10 grams, terrestrial ground-forager, urban habitat, no defences. One known caveat we flag in limitations — cats mostly take Fairy-wrens as nestlings and fledglings rather than adults, so our p-predation represents an effective pooled rate rather than a literal per-adult kill probability."

### Q: "Why no catchability heterogeneity? Belsare & Vanak have it."

> "That was the single biggest cut from our earlier model iteration, and we cut it because the proposal feedback asked for scope reduction. Catchability class — easy, moderate, hard — matters for *within-strategy* mechanics like diminishing returns as programs run longer. But our research question is *inter-strategy*: comparing TNR to culling at matched effort. Both strategies would be affected equally by catchability heterogeneity, so it doesn't change the comparative answer. It's documented as a candidate future extension in the handoff."

### Q: "What are the model's limitations?"

> "Six that we'd flag honestly. First, our Fairy-wren predation is applied uniformly across the population, but real cat impact on Fairy-wrens is dominated by nest predation on fledglings rather than adult kills. Our p-predation represents an *effective* pooled rate. Second, cat sex is tracked but we don't model male-female proximity for mating; we use a direct monthly birth probability. Third, cats can't learn to avoid traps. Fourth, intervention is random across the grid; real programs target high-density areas. Fifth, sterilised cats hunt at the same rate as intact cats by default — that's the conservative assumption for TNR, so any TNR disadvantage we report is an upper bound. Sixth, the carrying-capacity dynamics come from juvenile mortality + food-driven immigration rather than an explicit density mechanism, so we can't tune cat density independently of mortality. All six are documented as future extensions."

### Q: "What if sterilised cats hunt less than intact?"

> "Our default sets `sterilised-hunting-fraction` to 1.0 — same rate as intact. We chose this as the conservative assumption per Longcore et al. 2009, who argued the evidence for reduced post-sterilisation hunting is mixed. If sterilisation did reduce hunting — say to 0.75 or 0.5 — TNR's wildlife-impact penalty would shrink. The exchange rate we report under the baseline is therefore an upper bound on the true TNR cost; under reduced-hunting scenarios the number would be smaller. Any wildlife finding we claim for TNR holds *a fortiori* under reduced hunting."

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

> "The V1 model is scoped tightly around one quantitative question — the exchange rate between prey saved and cats killed under culling versus TNR — chosen deliberately because its direction is predictable but its magnitude is not. The headline value at the Gunther 80% coverage reference is roughly 0.4 prey saved per cat killed, an order of magnitude below naive expectation because of immigration backfill and sterilised cats continuing to hunt. The model has 21 parameters, 5 cat state variables, 7 tick phases, and about 500 lines of NetLogo code. BehaviorSpace experiments are configured for the primary analysis plus sensitivity across immigration and food. Several mechanisms are documented as future extensions, each with clear rationale for being out of V1 scope."

---

## Rehearsal checklist

- [ ] Opening (60s) memorised
- [ ] Can describe each of the 7 phases without reading
- [ ] Can state the headline exchange-rate finding and interpret the units
- [ ] Can defend the 20 cats/month reference (Gunther et al. 80% benchmark)
- [ ] Can defend Set B rate calibration (specifically d-juvenile = 0.25 → Mirmovitch 1995's 16% urban kitten survival; R₀ ≈ 1.5)
- [ ] Can cite Denny & Dickman 2010 page numbers for cat demographics (§3.5–3.9, p.17–20; Table 1 p.13 density; Table 4 p.25 vulnerability)
- [ ] Can defend Superb Fairy-wren as anchor prey (Rowley 1965, Russell & Rowley 1993) and the nest-predation caveat
- [ ] Can defend food-driven immigration framing
- [ ] Can defend removing hybrid, catchability, prey habitat
- [ ] Can defend 100% sterilised hunting rate as conservative
- [ ] Can list six limitations honestly
- [ ] Prepared a personal-contribution answer that's specific and verifiable
- [ ] Prepared a contested-decision example
- [ ] Can run `setup` and `go` live
- [ ] Can modify a slider and re-run live
- [ ] Can read `run-all-tests` output live
