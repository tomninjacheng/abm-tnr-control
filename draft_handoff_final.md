# Handoff: Agent-Based Model for Stray Cat Management with Prey Species Impact — V1 (Australian Context)

This document captures the design decisions, research question, and model specification for a university project building an agent-based model (ABM) that compares stray cat management strategies by their effect on a native prey species in an Australian urban setting. It is written for another collaborator (or future-self) to pick up and continue from.

**Current state: V1 design is locked, calibration anchored to Australian primary sources (Denny & Dickman 2010 for cat demographics; Rowley 1965 / Russell & Rowley 1993 for Superb Fairy-wren as anchor prey), validated against a non-spatial deterministic projection. ODD rewritten. Ready for parameter-sensitivity analysis.**

**Primary parameter anchoring document: `parameter_anchoring.md`** — maps every quantitative parameter in the model to a specific page/number in Denny & Dickman (2010) or the Fairy-wren literature. Read it before touching any rate.

---

## 1. Project Overview

### Research question (RQ-A)

> **At matched monthly intervention effort, how many additional prey deaths does TNR cause per cat spared from culling over 10 years?**

**Why this framing.** Teacher feedback flagged that "which strategy produces lower prey mortality" has a predictable direction — culling wins because sterilised cats continue hunting. The reframed question accepts that direction and asks the quantitative **exchange rate**: how much wildlife is sacrificed per cat spared. The answer could be anywhere from near-zero (TNR almost as effective as culling) to tens (each sterilised cat prevents many prey deaths). First-principles reasoning cannot predict it; the simulation produces it.

**Primary outcome metric:**

```
wildlife-cost-per-cat-spared(N) = (prey_kills_TNR_at_N − prey_kills_cull_at_N) / cumulative_cats_culled_at_N
```

Headline value is at **N = 20 cats/month** (the Gunther et al. 2022 field threshold of 80% annual coverage at our N=300 initial population). The full `cost(N)` curve across the 0–40 sweep is reported as sensitivity.

**Secondary metrics (interpretation):** cumulative prey-years lost vs no-cat baseline (sanity check); per-strategy final cat population and prey population.

**Interpretation.** The ratio is a policy-decision support quantity. A city weighing TNR vs culling reads: "per cat killed, X extra prey saved over 10 years." If X is small, cat welfare arguments dominate (TNR is nearly as effective). If X is large, wildlife conservation dominates. The model does not take a position on the ethical weighting.

**Why 20 cats/month as the reference.** At N=300 initial cats, 20/month = 240/year = **80% annual coverage of the initial population**. Matches Gunther et al. (2022)'s field threshold from a 12-year Israeli TNR study. McCarthy et al. (2013)'s 57% minimum maps to 15 cats/month. The sweep covers 0 (unmanaged baseline) through 40 (operationally unrealistic).

### Why this question matters

Every existing simulation model of stray cat management (McCarthy et al., 2013; Miller/Boone et al., 2014; Ireland & Neilan, 2016; Belsare & Vanak, 2020; StreetDogSim 2023) measures success purely in terms of predator population numbers. None include a prey species. The core conservation objection to TNR is that sterilised cats continue to hunt wildlife for their remaining lifespan. Whether TNR's slower population decline results in more or fewer cumulative wildlife deaths than culling's faster but potentially rebounding decline has never been quantified in a model. This project is the first to do so.

### Why ABM

ABM is justified over equation-based alternatives because:

- The vacuum-effect pattern (removal increases immigration) is a spatial, agent-level phenomenon driven by resource availability. We implement it mechanistically via food consumption and immigration, so it emerges rather than being assumed.
- Heterogeneous agents matter: cats differ by sex, age, reproductive status, and location.
- Local interactions (food competition at the cell level, predation in a Moore neighbourhood) create emergent spatial patterns that aggregate population equations cannot produce.

### Marker's feedback and response

The project received proposal feedback flagging two main issues:

1. **Research question was two-part and partly trivial.** The first half ("does the strategy that minimises cat numbers also minimise prey mortality") is nearly self-evident. Fixed by replacing with a single comparative question (RQ-A above) that asks about matched-effort cumulative prey outcomes.

2. **Model scope too large.** Too many mechanisms (catchability class, multiple death pathways, hunger/health, breeding season, etc.) relative to the research question. Fixed by cutting aggressively in V1 (see §3 and §5 below) and documenting the cuts as deliberate simplifications with clear futures-extensions pathways.

The V1 model has 5 cat state variables (down from 13 in previous iterations), 2 prey state variables (down from 5), 2 grid cell attributes (down from 7), and 21 parameters (down from ~35).

---

## 2. Literature Summary

### 2.1 The TNR vs culling debate

- **Cost per animal (Benka et al., 2022):** TNR ~US$59, euthanasia ~US$87, shelter/adoption ~US$327.
- **Speed:** Culling produces immediate reduction. TNR is slow because sterilised cats remain alive for years until natural death.
- **Intensity threshold (McCarthy et al., 2013):** Neither TNR nor lethal control reduces population unless >57% of cats are processed annually.
- **Spatial contiguity requirement (Gunther et al., 2022):** A 12-year field study in Rishon-LeZion, Israel found that even 80% neutering coverage failed to reduce population when surrounding areas were untreated. Immigration-driven backfill is a documented phenomenon.
- **Demographic side effects of culling (Yoak et al., 2016):** Lethal removal skews age distribution toward younger, more aggressive animals.
- **Wildlife predation concern (Longcore et al., 2009):** Sterilised cats still hunt. Argued in prose but never modelled.

### 2.2 Scale of predation

- US: 1.3–4.0 billion birds, 6.3–22.3 billion mammals killed annually (Loss, Will & Marra, 2013).
- Australia: over 1.5 billion native animals killed annually; cats listed as threat to >200 nationally threatened species.
- Globally: cats contributed to 63 vertebrate extinctions, 14% of island bird/mammal/reptile extinctions (Doherty et al., 2016).

### 2.3 Vacuum effect

The empirical pattern (removal increases immigration) is well-documented. The *mechanism* has not been experimentally isolated — candidates include territorial vacancy, unconsumed food, faded scent marks, and reduced intraspecific competition. In V1 we operationalise it through food consumption: living cats (intact or sterilised) suppress immigration by eating food; absent cats leave food unconsumed, raising the immigration signal.

### 2.4 Hunting behaviour (Cecchetti et al., 2021)

Pet and feral cats hunt largely from instinct rather than nutritional need. This supports modelling predation as one-directional (cats reduce prey; prey decline does not feed back into cat mortality).

### 2.5 What existing models do and don't model

| Study | Platform | Spatial | Catchability het. | Prey | Cost |
|---|---|---|---|---|---|
| McCarthy et al. 2013 | custom | no | no | no | no |
| Miller/Boone 2014/19 | Vortex | no | no | no | no |
| Ireland & Neilan 2016 | ABM | colony-based | no | no | no |
| Yoak et al. 2016 (dogs) | ABM | zone-based | no | no | no |
| Belsare & Vanak 2020 (dogs) | NetLogo | no | **yes** | no | no |
| StreetDogSim 2023 (dogs) | NetLogo | no | no | no | no |
| **This project (V1)** | **NetLogo** | **grid-based** | **no** | **yes** | **post-hoc** |

The gap filled by this project is the prey species. V1 deliberately abstracts away catchability heterogeneity (which Belsare & Vanak included) because the marker flagged scope creep; it is a natural future extension.

---

## 3. V1 Model Design — Summary

### 3.1 Entities and state

**Cats** (5 state variables): position, home, sex, age, status (intact / sterilised).

**Prey** (2 state variables): position, age.

**Grid cells** (2 attributes): `food_capacity` (static, clustered), `food_current` (dynamic).

### 3.2 Scales

- Grid: 50 × 50 cells, each ~50 × 50 m, total ~2.5 km × 2.5 km (one urban district).
- Time step: 1 month.
- Duration: 120 months (10 years).

### 3.3 Process overview

Each monthly tick, in order:

1. **Cat movement + feeding.** Each cat moves to the highest-`food_current` cell within `territory_radius`; consumes `food_consumption` units from that cell.
2. **Immigration.** `Poisson(base_immigration × Σ food_current / Σ food_capacity)` new intact adult cats enter at random edge cells.
3. **Food regeneration.** Each cell recovers toward capacity by `food_regen_rate`.
4. **Prey movement.** Each prey random-walks to a cell within `prey_search_radius`.
5. **Predation.** For each prey: if ≥1 adult cat is within `predation_radius`, roll `p_predation`; prey dies on success.
6. **Reproduction and mortality.** Intact adult female cats produce litters with probability `p_birth`; cats age; cats die at `d_juvenile_cat` or `d_adult_cat` by age class. Prey reproduce logistically; prey age; prey die at `d_juvenile_prey` or `d_adult_prey` by age class.
7. **Intervention.** Up to `cats_processed_per_month` intact adult cats are selected at random; processed under current strategy (TNR / cull).

Full submodel specification is in `ODD_protocol_final.md` §§3 and 7.

### 3.4 Parameter table

See ODD §2.2 for the full table. Highlights:

| Group | Key parameter | Default |
|---|---|---|
| Cat reproduction | `p_birth`, `litter_size` | 0.17, 4 |
| Cat mortality | `d_juvenile`, `d_adult` | 0.25, 0.025 |
| Prey reproduction | `p_prey_birth`, `K_prey` | 0.25, 500 |
| Prey mortality | `d_juvenile_prey`, `d_adult_prey` | 0.30, 0.05 |
| Food | `food_capacity` (low/mid/high) | 0.3 / 1.0 / 2.0 |
| Food | `food_regen_rate`, `food_consumption` | 0.5, 1 |
| Immigration | `base_immigration` | 6 |
| Predation | `predation_radius`, `p_predation` | 1 cell, 0.1 |
| Intervention | `cats_processed_per_month` | 0 (20 in experiments) |

Total: 21 parameters.

### 3.5 Experiments

Three experiments, all answering RQ-A directly:

1. **Matched-effort comparison** (sweep `cats_processed_per_month` 0–40; two strategies TNR vs cull; 30 reps). Headline post-hoc analysis: compute `cost(20) = (prey_kills_TNR − prey_kills_cull) / cats_culled` at the reference 20 cats/month, plus `cost(N)` curve across the sweep.
2. **Immigration pressure sensitivity** (repeat Exp 1 at `base_immigration` ∈ {2, 6, 15}).
3. **Feeding-ban sensitivity** (repeat Exp 1 at `food_multiplier` ∈ {0.3, 0.7, 1.0}).

Primary output: three curves of prey-years-lost vs effort per experiment × strategy.

---

## 4. Key Design Decisions (V1)

Decisions made in response to the marker feedback and advisor review. Each is documented with its rationale.

**Why RQ-A specifically.** The original two-part question had a nearly trivial first half ("does the strategy that minimises cats also minimise prey mortality"). RQ-A fixes this by asking the comparative question that genuinely requires simulation: at matched intervention effort, do TNR's slow-decline-but-persistent-hunters outperform culling's fast-decline-but-immigrant-backfill, or the reverse? The answer is non-obvious a priori.

**Why prey-years-lost as the outcome metric.** Cumulative kills is non-monotone in harm: a strategy that drives prey extinct early records fewer "kills" than one that lets prey rebound and then be killed again. Prey-years-lost (integrated deficit vs no-cat baseline) is monotonic in harm — more prey below baseline for longer always means a larger deficit. The deterministic projection (see §7) confirms this metric cleanly separates strategies.

**Why cuts: catchability class, multiple death pathways, breeding season, density-dependent mating, nursing lockout, pregnancy state, hunger/health, prey habitat flag.** The marker explicitly flagged catchability class and multiple death pathways. We cut these plus others that added complexity without serving RQ-A. Each is a candidate future extension (see §8).

**Why kept: food dynamics for immigration.** Without food-mediated immigration, culling and TNR differ only in *how* cats are removed, not in dynamic consequence. The vacuum-effect dynamic — culling creates food "vacancies" that pull immigrants faster than TNR — is central to the TNR-vs-culling comparison the research question asks about. Removing food dynamics would make the comparison trivially one-sided. Food in V1 does NOT drive mortality — only immigration.

**Why Set B rates (p_birth = 0.17/mo, d_juvenile = 0.25/mo, d_adult = 0.025/mo) — anchored to Denny & Dickman (2010).**

Every rate in Set B maps directly to a line in the Australian cat-ecology review:

| Rate | Produces | Denny & Dickman anchor | Page |
|---|---|---|---|
| `d_juvenile_cat = 0.25` | 17.8% survival to 6 mo | Mirmovitch 1995 urban feral (7/43 = 16%) | §3.7, p.18 |
| `d_adult_cat = 0.025` | mean adult life 3.3 yr | Warner 1985: "beyond 3–5 yr rare" | §3.8, p.19 |
| `p_birth = 0.17/mo` | 2.04 litters/yr | Jones & Coman 1982a: 2 litters/yr | §3.5, p.17 |
| `litter_size = 4` | — | Deag 2000: 3.88; prenatal 4.1–4.7 | §3.6, p.18 |

Combined, these produce internal R₀ ≈ 1.5 → ~20% annual unmanaged growth. This is slower than the 8.5-month population-doubling Short & Turner (2005) measured at Heirisson Prong WA (Denny & Dickman p.19) — but that's a resource-rich pulse scenario, not an urban-feral baseline. The high juvenile mortality implicitly absorbs density-dependent processes (disease transmission, intraspecific predation on kittens, maternal food stress) that we do not model explicitly.

**Why initial density 48 cats/km² (300 cats on 6.25 km²).** Wilson et al. 1994 reported Canberra highly-modified habitat densities of 19, 38, 90 cats/km² — our density sits in the middle of this range (Denny & Dickman Table 1, p.13).

**Why logistic prey reproduction + prey-years-lost metric.** Without a regulator, prey rates give R0 ≈ 2.45, so prey grow 50%/year unchecked (500 → 60,000 over 10 years). Logistic reproduction with `K_prey = 500` prevents explosion. Combined with prey-years-lost metric (which is monotonic in harm), the model produces answerable dynamics that the deterministic projection confirms.

**Why Superb Fairy-wren (*Malurus cyaneus*) as the anchor prey.** Three reasons:

1. **Data density.** Rowley (1965) is the foundational life-history monograph (clutch size 3.2, max 3 broods/yr, max longevity 10 yr 4 mo, from Gungahlin ACT). Russell & Rowley (1993) on the closely related Splendid Fairy-wren gives adult annual survival (M: 0.70, F: 0.59) and juvenile first-year survival (0.31, range 0.11–0.59). The ANU 30-year Canberra long-term dataset gives normal-year adult winter loss of ~20%.
2. **Ecological realism.** Superb Fairy-wrens are common in Melbourne urban parks and gardens today — the system our model simulates. The alternative Melbourne-local anchor, Eastern Barred Bandicoot, is now confined to predator-proof fenced sanctuaries on the mainland, so cat–prey co-occurrence doesn't apply.
3. **Vulnerability profile.** Under Dickman's (1996) rank-scoring system in Denny & Dickman (2010) Table 4 (p.25): ~10 g (score 3), terrestrial ground-forager (habitat score 3, behaviour score 2) — cumulative "high" vulnerability.

**Prey-parameter anchor mapping:**

| Model parameter | Value | Fairy-wren anchor |
|---|---|---|
| `d_adult_prey = 0.05/mo` | annual survival 0.54 | Russell & Rowley 1993: 0.59 (F), 0.70 (M); model value absorbs cat-pressure in Melbourne urban that is absent from the WA forest reference |
| `p_prey_birth × litter 2 = 0.5/mo offspring` | ~6 offspring/F/yr | Rowley 1965: 3 broods × 3.2 eggs × ~60% fledging ≈ 5.8/yr |
| `K_prey = 500` | ~0.8 adults/ha urban | Parsons et al. 2007 / BirdLife urban territory 1.4 ha → ~1.5 adults/ha in good habitat × 625 ha × ~35% suitable habitat ≈ 325–470 |

**Known limitation.** Cats take Fairy-wrens disproportionately as nestlings/fledglings rather than adults — our `p_predation` is an *effective* pooled rate, not a literal per-adult kill probability. Flagged in the limitations list and in the viva script.

**Why food capacity scaled down from earlier iterations.** Earlier capacity values (total ~8,000 units) were so large that cats consumed only ~4% of monthly regen, so immigration stayed near max regardless of colony state — the food-driven dynamic didn't fire. Scaled-down values (total ~1,225) produce a visible immigration response: ~3/month at full colony, ~6/month at empty.

**Why phase ordering: feeding → immigration → regeneration.** Immigration ratio is computed from post-feeding (depleted) food state so it responds to current colony pressure rather than idealised capacity. Regeneration happens afterward to prepare for the next tick.

**Why only adult cats (age ≥ 6 months) hunt and are trappable.**
Kittens are a substantial share of the population at Set B rates. If they counted toward predation, cat clusters would be deadlier for prey than their adult-hunter count alone would suggest. If they were trappable, random intervention selection would spend significant effort on kittens that are destined to die naturally within six months anyway — distorting the comparison. Restricting both hunt and trap eligibility to adults (age ≥ 6 months) is realistic and keeps the model's logic clean.

**Why single territory radius for both sexes (assumption).** Intact males typically range further than females in reality. V1 uses a single 3-cell radius because at monthly resolution the primary role of `territory_radius` is food-search range, and mating is not modelled through proximity in V1 (reproduction is a direct monthly draw per intact female). Reintroducing a sex-specific split is straightforward if calibration later shows it matters.

**Why sterilised cats hunt at intact rate by default (assumption).** This is the conservative choice for TNR per Longcore et al. (2009) — if sterilisation actually reduces hunting (as some studies suggest), TNR's wildlife-impact advantage reported by this model would be *larger* than observed. The baseline result holds *a fortiori* under reduced-hunting scenarios.

**Why food-driven immigration is framed as "operationalising the vacuum effect pattern" rather than "modelling the vacuum effect".** The vacuum effect's underlying mechanism (territorial vacancy vs food vs scent vs competition) has not been experimentally isolated. V1 reproduces the observed pattern (resident cats suppress immigration; absent cats raise it) through a mechanistically transparent pathway — food consumption — without committing to a particular causal mechanism.

**Why 10-year horizon.** Matches Boone et al. and Benka et al. for comparability. TNR effects are slow; shorter runs would make TNR look artificially bad. Longer runs amplify uncertainty.

**Why 50×50 grid.** Represents ~6.25 km², roughly one urban district. Small enough for 30+ replicates × multiple parameter sweeps to be computationally feasible. Large enough for spatial dynamics (food clustering, predation hotspots) to matter.

---

## 5. Simplifications and Known Limitations

The following are deliberately not modelled in V1. Each is noted as a future extension.

| Simplification | Rationale | Future extension |
|---|---|---|
| No catchability heterogeneity | Marker-flagged scope creep. All cats equally trappable. | Add 3-class catchability (easy/mod/hard) with per-class success probabilities. |
| No food-driven mortality | Marker-flagged "multiple death pathways". Age-based flat rates only. | Add starvation surcharge triggered at low food. |
| No breeding season | Simplification. Year-round constant rates. | Add seasonal gating with user-set breeding months. |
| No density-dependent mating / Allee effect | Simplification. Direct monthly birth draw. | Add intact-male-proximity check with density-dependent mating probability. |
| No pregnancy / gestation state | Simplification. Births are instantaneous outcomes of monthly draw. | Add 2-month gestation timer; TNR of a pregnant female terminates the pregnancy. |
| No nursing lockout | Simplification. | Add 1-month post-litter lockout preventing immediate re-pregnancy. |
| No prey habitat flag | Marker-flagged scope creep. Prey distributed uniformly. | Add habitat flag; prey preferentially occupy habitat cells. |
| No spatial targeting of intervention | Random selection across grid. | Add high-density-area targeting (Ireland & Neilan 2016 pattern). |
| No trap learning | Catchability (if added) is fixed per cat. | Trap-failed cats become harder to catch next month. |
| No budget constraint | Cost is post-hoc only. | Add monthly budget cap that bounds `cats_processed_per_month`. |
| Sex-unified territory radius | Simplification. 3 cells for all cats. | Sex-specific split (2 for F, 3+ for M). |
| Sterilised hunting rate = intact | Conservative for TNR (Longcore et al. 2009). | Sweep `sterilised_hunting_fraction` ∈ {1.0, 0.75, 0.5}. |
| High kitten mortality absorbs density effects | Avoids explicit density dependence. | Replace with density-dependent kitten mortality or logistic cat reproduction. |
| Hybrid strategy (mixed TNR + cull) removed for V1 | Cleaner two-way comparison. | Re-add hybrid as a third strategy in a V2 iteration if a specific mixed-policy question is motivated. |

---

## 6. Implementation Notes

**Platform.** NetLogo. Belsare & Vanak (2020) and StreetDogSim (2023) use NetLogo for comparable models; BehaviorSpace handles parameter sweeps for the experimental design.

**Validation approach.** Before running experiments, verify the four patterns in ODD §1:

1. Unmanaged cat population drifts upward from accumulated immigration (not exponential explosion, not plateau).
2. Culling drives intact cats down quickly; immigration partly offsets.
3. TNR produces slow decline with persistent sterilised stock.
4. Food-driven immigration swings between ~3/month (full colony) and ~6/month (empty).

These are sanity checks, not parameter fitting.

**Statistical requirements.** Minimum 30 replicates per parameter combination. Report medians and interquartile ranges. Mann-Whitney U or Kruskal-Wallis for comparisons.

**Key outputs.**

1. Prey-years-lost curves vs effort for each strategy (primary metric).
2. Cumulative-kills curves (secondary).
3. Spatial density maps (cats, prey, overlap).
4. Immigration-rate time series showing vacuum-effect dynamic.

**NetLogo-specific notes.** Model will have two breeds (`cats` and `preys`). Patches have two state variables (`food-capacity`, `food-current`). BehaviorSpace experiments will be configured for the three experiments in §3.5.

---

## 7. Validation Projection (Pre-implementation)

Before implementation, a non-spatial deterministic projection of V1 aggregate dynamics was run for 120 months under TNR @ 20/mo and cull @ 20/mo at the Günther et al. (2022) 80% coverage reference effort. Current script: `results/sensitivity_oat.py` (includes both the baseline and the OAT sensitivity perturbations).

**Headline finding at the reference effort (no burn-in, Set B rates, base-immigration=10):**

| Scenario | Cumulative prey kills | Cumulative cull count |
|---|---|---|
| Cull @ 20/mo | ~230 | ~1,529 |
| TNR @ 20/mo | ~487 | 0 |

**cost(20) = (487 − 230) / 1529 ≈ 0.17 prey saved per cat killed.**

**Supporting findings.**

- **Food-driven immigration responds mechanistically** to colony state: suppressed when cats fully consume available food, elevated when cats are removed.
- **Logistic prey reproduction keeps prey bounded** at K-prey rather than growing unchecked.
- **OAT sensitivity across all 10 parameters** keeps cost(20) in the range 0.09–0.33 — strictly positive, no sign flips. See `sensitivity_notes.md` and `results/sensitivity_tornado.png`.
- **Pre-registered sensitivity predictions confirmed:** cost(20) decreases with higher immigration; increases with less food.

The projection confirms V1 is answerable, produces a policy-relevant finding, and is robust to parameter uncertainty within the anchored ranges. Full NetLogo BehaviorSpace runs will refine absolute magnitudes.

---

## 8. Future Extensions

Prioritised list for V2 and beyond:

1. **Catchability heterogeneity** (Belsare & Vanak 2020 pattern). Three-class system with per-attempt success probabilities. Reinstates "effort ≠ catches" distinction and creates diminishing-returns dynamics.
2. **Sterilised hunting fraction sensitivity.** Sweep `sterilised_hunting_fraction` ∈ {1.0, 0.75, 0.5} to test TNR's wildlife-impact robustness.
3. **Spatial targeting.** Concentrate intervention on high-cat-density areas rather than random selection. Reflects real program design (Ireland & Neilan 2016).
4. **Trap learning.** Cats escaping an attempt become harder to catch in subsequent months.
5. **Prey habitat structure.** Habitat flag with preferential prey occupancy; tests how urban green-space planning interacts with cat management.
6. **Breeding seasonality.** Realistic seasonal reproduction pulse.
7. **Density-dependent mating / Allee effect.** Captures acceleration of decline past a density threshold.
8. **Pregnancy / gestation state and nursing lockout.** More realistic reproductive dynamics; relevant for pregnant-female TNR outcomes.

---

## 9. References

### Primary anchor references

Denny, E. A. & Dickman, C. R. (2010). *Review of Cat Ecology and Management Strategies in Australia*. Invasive Animals Cooperative Research Centre, Canberra. ISBN 978-0-9806716-6-7. **[Primary cat-demography anchor.]**

Rowley, I. C. R. (1965). The life history of the Superb Blue Wren, *Malurus cyaneus*. *Emu*, 64(4), 251–297. **[Primary Fairy-wren life-history anchor.]**

Russell, E. M. & Rowley, I. C. R. (1993). Demography of the cooperatively breeding Splendid Fairy-wren, *Malurus splendens*. *Australian Journal of Zoology*, 41(5), 475–505. **[Closest demographic analogue for annual survival rates.]**

### Secondary references (cited in Denny & Dickman 2010)

Jones, E. & Coman, B. J. (1982a). Ecology of the feral cat, *Felis catus* (L.), in south-eastern Australia. *Wildlife Research*, 8, 537–547.

Mirmovitch, V. (1995). Spatial organisation of urban feral cats in Jerusalem. *Wildlife Research*, 22, 299–310.

Warner, R. E. (1985). Demography and movements of free-ranging domestic cats in rural Illinois. *Journal of Wildlife Management*, 49, 340–346.

Wilson, G. R., Dexter, N., O'Brien, P. & Bomford, M. (1994). *Pest Animals in Australia*. Bureau of Rural Resources, Canberra.

Parsons, H., Major, R. E. & French, K. (2007). Species interactions and habitat associations of birds inhabiting urban areas of Sydney, Australia. *Austral Ecology*, 32(2), 217–226.

### Model-structure references

Belsare, A. V. & Vanak, A. T. (2020). Modelling the challenges of managing free-ranging dog populations. *Scientific Reports*, 10, 18874.

Benka, V. A., Boone, J. D., Miller, P. S., et al. (2022). Guidance for management of free-roaming community cats: a bioeconomic analysis. *Journal of Feline Medicine and Surgery*, 24(10), 975–985.

Boone, J. D., Miller, P. S., Briggs, J. R., et al. (2019). A long-term lens: Cumulative impacts of free-roaming cat management strategy and intensity on preventable cat mortalities. *Frontiers in Veterinary Science*, 6, 238.

Cecchetti, M., Crowley, S. L., Goodwin, C. E. D. & McDonald, R. A. (2021). Provision of high meat content food and object play reduce predation of wild animals by domestic cats. *Current Biology*, 31(5), 1107–1111.e5.

Doherty, T. S., Glen, A. S., Nimmo, D. G., Ritchie, E. G. & Dickman, C. R. (2016). Invasive predators and global biodiversity loss. *PNAS*, 113(40), 11261–11265.

Gunther, I., Hawlena, H., Azriel, L., Gibor, D., Berke, O. & Klement, E. (2022). Reduction of free-roaming cat population requires high-intensity neutering in spatial contiguity to mitigate compensatory effects. *PNAS*, 119(15), e2119000119.

Ireland, T. & Neilan, R. M. (2016). A spatial agent-based model of feral cats and analysis of population and nuisance controls. *Ecological Modelling*, 337, 123–136.

Legge, S., Woinarski, J. C. Z. & Dickman, C. R. (2019). *Cats in Australia: Companion and Killer.* CSIRO Publishing, Melbourne.

Longcore, T., Rich, C. & Sullivan, L. M. (2009). Critical assessment of claims regarding management of feral cats by trap-neuter-return. *Conservation Biology*, 23(4), 887–894.

Loss, S. R., Will, T. & Marra, P. P. (2013). The impact of free-ranging domestic cats on wildlife of the United States. *Nature Communications*, 4, 1396.

McCarthy, R. J., Levine, S. H. & Reed, J. M. (2013). Estimation of effectiveness of three methods of feral cat population control by use of a simulation model. *JAVMA*, 243(4), 502–511.

Miller, P. S., Boone, J. D., Briggs, J. R., et al. (2014). Simulating free-roaming cat population management options in open demographic environments. *PLoS ONE*, 9, e113553.

StreetDogSim (2023). Assessing multiple free-roaming dog control strategies in a flexible agent-based model. *Scientific Reports*, 13.

Yoak, A. J., Reece, J. F., Gehrt, S. D. & Hamilton, I. M. (2016). Optimizing free-roaming dog control programs using agent-based models. *Ecological Modelling*, 341, 53–61.
