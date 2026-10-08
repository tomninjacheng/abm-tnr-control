# ODD Protocol (V1): Agent-Based Model Comparing Stray Cat Management Strategies and their Impact on a Co-occurring Prey Species

Following the ODD (Overview, Design concepts, Details) protocol standard (Grimm et al., 2006; 2010). This document specifies the simplified V1 model, which abstracts away several mechanisms present in earlier design iterations (catchability class, food-mediated mortality, breeding seasonality, density-dependent mating, habitat confinement, hybrid strategy) in response to proposal feedback that the model should be scoped tightly around a single research question.

---

## 1. Purpose

This model compares two stray cat management strategies — trap-neuter-return (TNR) and culling — in terms of their effects on a co-occurring native prey species over a 10-year period. The prey species is generic and can represent ground-nesting birds, small reptiles, or small mammals depending on parameter calibration.

**Framing.** At matched monthly intervention effort, culling will inevitably produce lower cumulative prey mortality than TNR because culling removes hunters while TNR keeps them alive (sterilised cats continue hunting). The direction is predictable from first principles. The question of research interest is not the direction but the **magnitude**: how much more TNR effort is required to close that wildlife gap, and does the required effort multiplier change with ecological context (immigration pressure, food availability)?

**Research question (RQ-A, narrow):** How many cats per month must a TNR program process to match the 10-year cumulative wildlife outcome (cumulative prey predation events) of a culling program processing 20 cats/month? Does this "TNR effort multiplier" depend on immigration pressure and food availability?

**Why the reference effort is 20 cats/month.** At our initial population of 300 cats, 20 cats/month = 240 processings per year = **80% annual coverage of the initial population**. This matches the Gunther et al. (2022) field benchmark from a 12-year Israeli TNR study: 80% neutering coverage was the aggressive-but-realistic upper threshold of a well-resourced local program (and was *still* insufficient when surrounding areas were untreated, which the sensitivity across `base_immigration` levels addresses). McCarthy et al. (2013)'s 57% annual-capture minimum threshold corresponds to 15 cats/month at our density. The 0–40 cats/month sweep therefore spans "well below the minimum" (0–10) through "aggressive but realistic" (15–20) up to "operationally unrealistic" (25+) for a real community program.

**Primary outcome metric:** cumulative prey predation events over 120 months (direct count of cat-caused prey deaths). The multiplier is derived post-hoc as `smallest N such that median(TNR-kills at effort N) ≤ median(cull-kills at effort 20)`, divided by 20.

**Three possible answer shapes, each informative:**

1. **Finite multiplier.** TNR achieves equivalent wildlife outcomes at `N×` the effort of culling. Quantitative policy-relevant answer (e.g., "TNR needs 2.5× culling's effort").
2. **No achievable multiplier (TNR floor exceeds culling's output).** No TNR effort within the achievable range closes the gap, because sterilised cats continue hunting throughout their natural lifespan (average ~3 years post-sterilisation). This would be a structural finding about an inherent limit of TNR.
3. **Near-1× multiplier.** TNR and culling produce near-equivalent wildlife outcomes because culling's advantage is offset by immigrant backfill. Would overturn the naive intuition.

**Secondary metric:** cumulative prey-years lost vs no-cat baseline, retained as a monotonic-in-harm sanity check and for cross-comparison with the predation-count metric.

**Validation patterns.** The following should emerge from agent interactions:

1. Unmanaged cat population grows upward from accumulated immigration (internal reproduction is near replacement at the chosen rates).
2. Culling drives the intact population down quickly; immigration backfill partly offsets this.
3. TNR produces a slow decline in total cats, but sterilised cats persist and continue consuming food and hunting.
4. Food-driven immigration responds to colony state: full colonies suppress immigration via food consumption; depleted colonies attract more immigrants.

---

## 2. Entities, State Variables, and Scales

### 2.1 Entities

The model contains three types of entities: cat agents, prey agents, and grid cells.

**Cat agents** represent individual free-roaming cats:

| Variable | Type | Description |
|---|---|---|
| position | (x, y) integer | Current grid cell |
| home | (x, y) integer | Home-cell anchor for movement |
| sex | F or M | Assigned at birth, 50:50 ratio |
| age | integer (months) | Incremented each tick |
| status | intact / sterilised | Reproductive state; sterilised cats remain alive and continue consuming food and hunting |

**Prey agents** represent individuals of a generic ground-level native species:

| Variable | Type | Description |
|---|---|---|
| position | (x, y) integer | Current grid cell |
| age | integer (months) | Incremented each tick |

**Grid cells** represent 50 m × 50 m patches:

| Variable | Type | Description |
|---|---|---|
| food_capacity | float | Maximum cat food the cell can hold (static; clustered to simulate commercial-zone hotspots) |
| food_current | float | Cat food available this tick; depleted by cat feeding, restored by regeneration |

### 2.2 Global parameters

| Parameter | Default | Group |
|---|---|---|
| `initial_cat_population` | 300 | Initialisation |
| `initial_prey_population` | 500 | Initialisation |
| `grid_size` | 50 × 50 | Spatial scale |
| `simulation_length` | 120 months | Temporal scale |
| **Cat reproduction** | | |
| `p_birth` | 0.17 / month | Monthly birth probability per intact adult female |
| `litter_size` | 4 | Fixed litter size |
| **Cat mortality (age-based flat rates)** | | |
| `d_juvenile_cat` | 0.35 / month | Monthly death probability for cats aged < 6 months |
| `d_adult_cat` | 0.025 / month | Monthly death probability for cats aged ≥ 6 months |
| **Cat movement** | | |
| `territory_radius` | 3 cells | Food-search range (sex-unified; see §4) |
| **Prey reproduction (logistic)** | | |
| `p_prey_birth` | 0.25 / month | Base monthly birth probability per adult female prey |
| `prey_litter_size` | 2 | Fixed prey litter size |
| `K_prey` | 500 | Logistic carrying capacity for prey |
| **Prey mortality** | | |
| `d_juvenile_prey` | 0.30 / month | Monthly death probability for prey aged < 2 months |
| `d_adult_prey` | 0.05 / month | Monthly death probability for prey aged ≥ 2 months |
| **Prey movement** | | |
| `prey_search_radius` | 2 cells | Max distance of random prey movement per month |
| **Food / immigration** | | |
| `base_immigration` | 6 / month | Immigration rate at full food availability |
| `food_regen_rate` | 0.5 | Fraction of food capacity restored per month |
| `food_consumption` | 1 unit | Food consumed per cat per month at the cat's current cell |
| `food_multiplier` | 1.0 | Scenario scaling of `food_capacity` (for feeding-ban experiments) |
| **Predation** | | |
| `predation_radius` | 1 cell | Max distance at which a cat threatens a prey |
| `p_predation` | 0.1 / month | Monthly kill probability per prey with any adult cat in range |
| **Intervention** | | |
| `cats_processed_per_month` | 0 (20 in experiments) | Direct intervention effort (adult intact cats processed per month) |
| `strategy` | TNR | TNR / cull |

### 2.3 Scales

- **Spatial:** 50 × 50 grid, each cell ~50 m × 50 m, total ~2.5 km × 2.5 km (one urban district). Outer-ring cells serve as the immigration zone.
- **Temporal:** 1 month per time step; simulation duration 120 months (10 years).

---

## 3. Process Overview and Scheduling

Each monthly time step proceeds through seven phases in fixed order. Within each phase, individuals are processed in randomised order.

**Phase 1 — Cat movement and feeding.**
Each cat moves to the cell with the highest `food_current` within its `territory_radius` (default 3 cells). On arrival, it consumes `food_consumption` units from the cell: `food_current ← max(0, food_current − food_consumption)`. Ties broken randomly.

**Phase 2 — Immigration.**
`λ = base_immigration × (Σ food_current / Σ food_capacity)` (ratio evaluated *after* feeding, *before* regeneration — this makes immigration respond to the depleted colony state rather than idealised capacity). Number of immigrants drawn as `Poisson(λ)`. Each immigrant is placed at a random edge cell as an intact adult (age drawn uniformly from 12–36 months).

**Phase 3 — Food regeneration.**
For each cell: `food_current ← min(food_capacity × food_multiplier, food_current + food_regen_rate × food_capacity × food_multiplier)`.

**Phase 4 — Prey movement.**
Each prey animal moves to a random cell within `prey_search_radius` (default 2 cells) of its current position. No habitat restriction, no food-seeking.

**Phase 5 — Predation.**
For each prey animal: count the number of adult (age ≥ 6 months) cats within `predation_radius` of its position. If at least one adult cat is present, draw a uniform random number; if less than `p_predation`, the prey dies. (Binary presence check — a single adult cat in range is sufficient to put the prey at risk; the probability is not scaled by the number of cats.)

**Phase 6 — Reproduction and mortality.**

*Cats:*
- Each intact female of age ≥ 6 months independently produces a litter of `litter_size` kittens at her current cell with probability `p_birth`. New kittens enter at age 0, status intact, sex drawn 50:50, home set to the mother's cell.
- Each cat ages by 1 month. Each cat then dies with monthly probability `d_juvenile_cat` (if age < 6 months) or `d_adult_cat` (if age ≥ 6 months).

*Prey:*
- Each adult female (age ≥ 2 months) produces `prey_litter_size` offspring at her current cell with probability `p_prey_birth × max(0, 1 − N_prey / K_prey)` (logistic reduction).
- Each prey animal ages by 1 month. Each prey animal then dies with monthly probability `d_juvenile_prey` (if age < 2 months) or `d_adult_prey` (if age ≥ 2 months).

**Phase 7 — Intervention.**
Up to `cats_processed_per_month` adult (age ≥ 6 months) intact cats are selected uniformly at random from the grid. If fewer such cats exist than the quota, all available are processed. On selection:

- **TNR:** cat's status changes from intact to sterilised; it remains at its current position.
- **Culling:** cat is removed from the model.

Only intact adults are eligible — kittens (age < 6 months) and already-sterilised cats cannot be selected. This reflects (a) the practical reality that programs target reproductively active cats and (b) that kittens are typically trapped with their mother or not at all (not modelled here).

**Phase 8 — Data collection.**
Monthly: adult cat counts (intact / sterilised), total cat count including kittens, prey count (juvenile / adult / total), prey deaths from predation this month, immigrants this month, cumulative processings (TNR / cull), total food available (Σ food_current / Σ food_capacity).

---

## 4. Design Concepts

**Basic principles.** The model draws on four standard ecological ideas: food-driven immigration dynamics (source-sink: unmanaged areas supply the managed district with cats, moderated by food availability), territorial foraging (cats move toward food within a home range), spatial clustering (food distribution determines where cats concentrate), and one-directional predator–prey interaction (cats reduce prey numbers; prey decline does not feed back into cat mortality, consistent with Loss et al., 2013, since urban cats are sustained by human food waste rather than hunting, and Cecchetti et al., 2021, which documents instinct-driven rather than nutrition-driven hunting).

**Vacuum-effect framing.** Immigration is driven by food in this model rather than by territorial vacancy. The empirical phenomenon known as the vacuum effect — removal of residents raises immigration — has not been experimentally isolated as to its underlying mechanism. We operationalise it through food consumption: sterilised cats and intact cats alike consume food and therefore suppress the immigration signal; culled cats are gone and the food they would have consumed stays available, raising the signal. This reproduces the observed vacuum-effect pattern without committing to a particular mechanism.

**Emergence.** The following emerge from agent interactions:
- An unmanaged cat population that grows upward from accumulated immigration, with internal reproduction near replacement.
- Different trajectories under TNR and culling interventions — including the TNR-specific pattern where sterilised cats accumulate and continue to consume food and prey even as new births decline.
- A vacuum-effect dynamic: culling increases immigration (food goes unconsumed), partially offsetting the removal; TNR does not.
- Spatial clustering of cats around food-hotspot cells, producing predation hotspots that prey wander into randomly.
- Different prey trajectories under each strategy, with culling best preserving prey abundance at matched intervention effort (predicted; subject to simulation).

**Adaptation.** None. Cats and prey follow fixed movement rules.

**Objectives.** Cats implicitly seek food through the move-toward-food rule. Prey do not actively seek anything (random walk). The intervention agency follows a fixed strategy and effort level set by the user; it does not adapt.

**Learning.** None.

**Prediction.** None.

**Sensing.** Cats sense `food_current` of cells within `territory_radius`. Prey do not sense anything. For both species, "sensing" at this scale is a time-resolution abstraction: over a month of daily movement, an animal effectively ends up at the location it would have gravitated to; the search radius represents how far it typically ranges, not a literal sensory distance.

**Interaction.** Cat-cat interaction is implicit (food competition at the cell level — first-come-first-served within a tick's randomised processing order). Cat-prey interaction is predation (binary presence check in a Moore neighbourhood). Prey-prey interaction is implicit (logistic reproduction).

**Stochasticity.** Agent processing order, cat movement tiebreaking, prey random walk, mating birth draws, mortality draws, predation success, immigration count (Poisson), intervention selection. Minimum 30 replicate runs per parameter combination.

**Collectives.** None.

**Observation.** See Phase 8 above. Primary end-of-run output: integrated prey-years lost vs no-cat baseline. Secondary outputs: cumulative predation kills, mean prey abundance, final cat population by status, cat and prey trajectory plots.

**Key assumptions.** The following simplifying assumptions have been made deliberately for V1 scope. Each is a candidate future extension.

1. **Food has no effect on cat death.** Mortality is purely age-based; food dynamics drive only immigration. Reality: starvation is a documented mortality source in feral colonies. The abstraction holds because urban free-roaming cats are typically sustained by human food waste; food scarcity more plausibly reduces immigration than kills resident cats.
2. **No catchability heterogeneity.** All intact adult cats are equally selectable. Reality: trap-shyness varies across individuals (Belsare & Vanak, 2020). Simplified away in V1 to focus on inter-strategy comparison rather than within-strategy mechanics.
3. **Juvenile mortality is high (0.35/month for cats, 0.30/month for prey).** These absorb the density-dependent processes (disease, intraspecific competition, nest predation for prey) that we do not model explicitly. The alternative — modelling those processes directly — would add state and complexity without changing the inter-strategy comparison that answers RQ-A.
4. **Sterilised cats hunt at the same rate as intact cats.** This is the conservative assumption for TNR per Longcore et al. (2009); if sterilisation actually reduces hunting, TNR's wildlife-impact advantage would be *larger* than this model reports.
5. **Sex-unified territory radius.** Intact males typically range further than females in reality; we use a single 3-cell radius since mating is not modelled through proximity in V1, and the primary role of `territory_radius` here is food-search range.
6. **No breeding season.** Seasonal pulses are abstracted into constant monthly rates. At a 10-year horizon, the comparative TNR-vs-culling outcome is not expected to shift from this.
7. **Prey are uniformly distributed, no habitat flag.** The habitat flag in earlier iterations was a modeller-chosen input that would drive results. Removing it means spatial separation between predator and prey emerges from cat clustering alone (near food cells), without an arbitrary binary split.
8. **Only two strategies compared (TNR vs culling).** Hybrid (mixed TNR + culling) was considered in earlier iterations and dropped for V1 to produce a cleaner two-way comparison. Hybrid is trivially re-addable as a future extension.

---

## 5. Initialisation

**Cat population.** 300 cats placed uniformly at random across the grid (no bias — cats will migrate toward food after step 1). Age drawn uniformly from 6–48 months (all start as adults; no initial kittens). Sex 50:50. All intact. Home set to initial position.

**Prey population.** 500 prey animals placed uniformly at random. Age drawn uniformly from 2–36 months.

**Grid cells.** `food_capacity` assigned by a three-tier distribution:

- 80% of cells: low (0.3 units)
- 15% of cells: medium (1.0 units)
- 5% of cells: high (2.0 units)

High-capacity cells are spatially clustered into 3 groups to simulate commercial zones with dumpsters. Total capacity ≈ 1,225 units across the grid. `food_current` initialised equal to `food_capacity × food_multiplier`.

**Burn-in.** No intervention is applied for the first 12 months to let the population settle away from the uniform-random initial distribution before experiments begin.

---

## 6. Input Data

The model does not use external time-series inputs. All environmental conditions are set at initialisation and remain static (apart from `food_current`, which evolves endogenously, and `food_capacity` which may be scaled by `food_multiplier` for feeding-ban scenarios).

---

## 7. Submodels

### 7.1 Cat movement and feeding (Phase 1)

Each cat:

1. Identifies the cell with maximum `food_current` within Moore distance `territory_radius` (default 3). Ties broken randomly.
2. Moves to that cell.
3. Consumes food: `food_current ← max(0, food_current − food_consumption)`.

### 7.2 Immigration (Phase 2)

Mean monthly immigrants:

```
λ = base_immigration × (Σ food_current / Σ food_capacity_effective)
```

where `food_capacity_effective = food_capacity × food_multiplier`. Ratio evaluated after Phase 1 feeding, before Phase 3 regeneration.

Number of immigrants drawn as `Poisson(λ)`. Each immigrant placed at a uniformly random outer-ring cell as an intact adult (sex 50:50, age Uniform(12, 36)), home set to arrival cell.

### 7.3 Food regeneration (Phase 3)

For each cell:

```
food_current ← min(food_capacity × food_multiplier,
                   food_current + food_regen_rate × food_capacity × food_multiplier)
```

Default `food_regen_rate = 0.5` recovers each cell to full capacity in two months.

### 7.4 Prey movement (Phase 4)

Each prey moves to a cell drawn uniformly at random from Moore cells within distance `prey_search_radius` of its current position. The move always occurs (no "stay" option). No habitat restriction.

### 7.5 Predation (Phase 5)

For each prey animal:

```
n_cats_in_range = count of cats with age ≥ 6 months within Moore distance predation_radius
if n_cats_in_range ≥ 1:
    if random-uniform() < p_predation:
        prey dies
```

Kittens (age < 6 months) do not count toward the predation presence check — only adult cats hunt effectively. The check is binary in cat presence (one or more adult cats = exposure); the probability is not scaled by cat density.

### 7.6 Cat reproduction and mortality (Phase 6, cat portion)

**Reproduction.** Each intact female cat with age ≥ 6 months independently draws Bernoulli(`p_birth`). On success, she produces `litter_size` kittens at her current cell. Kittens have age 0, status intact, sex drawn independently 50:50 per kitten, home set to the mother's cell.

**Mortality + ageing.** All cats age by 1 month. Each cat then dies with probability:

- `d_juvenile_cat` = 0.35/month if age < 6 months
- `d_adult_cat` = 0.025/month if age ≥ 6 months

Rationale for high juvenile mortality: this absorbs density-dependent processes (disease transmission in dense colonies, intraspecific predation on kittens, maternal food stress) that are documented in feral colony studies but not explicitly modelled in V1. Per-female fecundity is held at literature-consistent values (~2 litters/year, 4 kittens/litter — equivalent to `p_birth = 0.17/month`).

### 7.7 Prey reproduction and mortality (Phase 6, prey portion)

**Reproduction (logistic).** Each adult female prey (age ≥ 2 months) independently draws Bernoulli(`p_prey_birth × max(0, 1 − N_prey_total / K_prey)`). On success, she produces `prey_litter_size` offspring at her current cell.

**Mortality + ageing.** All prey age by 1 month. Each prey then dies with probability:

- `d_juvenile_prey` = 0.30/month if age < 2 months
- `d_adult_prey` = 0.05/month if age ≥ 2 months

High juvenile prey mortality absorbs predation by non-cat species, nest predation, exposure, and other sources we do not model explicitly.

### 7.8 Intervention (Phase 7)

Let `pool = { cats with status = intact AND age ≥ 6 months }`. Let `N = min(cats_processed_per_month, |pool|)`.

Draw `N` cats uniformly at random without replacement from `pool`.

- **TNR:** for each selected cat, status ← sterilised. Cat remains at current position.
- **Culling:** each selected cat is removed from the model.
Cost estimation (post-hoc, not a simulation constraint):

```
total_cost = (cumulative_cats_TNRed × 59) + (cumulative_cats_culled × 87)
```

Costs per Benka et al. (2022). Reported alongside ecological outcomes.

---

## 8. Experimental Design

Three experiments, each directly tied to RQ-A.

**Experiment 1 — Matched-effort comparison (primary).**
Sweep `cats_processed_per_month` from 0 to 40 in steps of 5. At each level, run two strategies (TNR, cull). 30 replicates each. 2 × 9 × 30 = 540 runs. Primary output: cumulative prey predation events (and prey-years-lost as secondary) at each (strategy, effort) point.

**Post-hoc multiplier derivation.** From the Exp1 output:
1. Compute `T = median(cumulative-prey-deaths | strategy=cull, effort=20)` across replicates. This is the reference wildlife outcome.
2. For each TNR effort level `N ∈ {5, 10, 15, 20, 25, 30, 35, 40}`, compute `K_N = median(cumulative-prey-deaths | strategy=tnr, effort=N)`.
3. Find smallest `N*` such that `K_{N*} ≤ T`. If no such `N*` exists in the sweep range, report "no equivalence achievable at effort ≤ 40 cats/month" (Answer shape 2 above).
4. Report multiplier = `N* / 20`.

**Experiment 2 — Immigration pressure sensitivity.**
Repeat Experiment 1 at `base_immigration` ∈ {2, 6, 15}. For each immigration level, derive the TNR effort multiplier using the same post-hoc procedure. Expected pattern: multiplier may shrink as immigration rises (culling's benefit is offset by immigrant backfill, so TNR looks relatively more competitive).

**Experiment 3 — Feeding-ban sensitivity.**
Repeat Experiment 1 at `food_multiplier` ∈ {0.3, 0.7, 1.0}. For each food level, derive the TNR effort multiplier. Expected pattern: multiplier may rise under feeding bans (fewer total cats, each cat removal matters more, so culling's lead expands).

Statistical analysis: median and interquartile range across replicates. The multiplier is derived from the median trajectories at each effort level. Confidence in the multiplier is bounded by the IQR overlap of adjacent effort levels (if adjacent IQRs overlap heavily, the multiplier estimate is uncertain and should be reported as a range rather than a point value).

---

## References

Belsare, A. V. & Vanak, A. T. (2020). Modelling the challenges of managing free-ranging dog populations. *Scientific Reports*, 10, 18874.

Benka, V. A., Boone, J. D., Miller, P. S., et al. (2022). Guidance for management of free-roaming community cats: a bioeconomic analysis. *Journal of Feline Medicine and Surgery*, 24(10), 975–985.

Cecchetti, M., Crowley, S. L., Goodwin, C. E. D. & McDonald, R. A. (2021). Provision of high meat content food and object play reduce predation of wild animals by domestic cats. *Current Biology*, 31(5), 1107–1111.e5.

Grimm, V., Berger, U., Bastiansen, F., et al. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, 198(1–2), 115–126.

Grimm, V., Berger, U., DeAngelis, D. L., et al. (2010). The ODD protocol: a review and first update. *Ecological Modelling*, 221(23), 2760–2768.

Ireland, T. & Neilan, R. M. (2016). A spatial agent-based model of feral cats and analysis of population and nuisance controls. *Ecological Modelling*, 337, 123–136.

Longcore, T., Rich, C. & Sullivan, L. M. (2009). Critical assessment of claims regarding management of feral cats by trap-neuter-return. *Conservation Biology*, 23(4), 887–894.

Loss, S. R., Will, T. & Marra, P. P. (2013). The impact of free-ranging domestic cats on wildlife of the United States. *Nature Communications*, 4, 1396.

McCarthy, R. J., Levine, S. H. & Reed, J. M. (2013). Estimation of effectiveness of three methods of feral cat population control by use of a simulation model. *Journal of the American Veterinary Medical Association*, 243(4), 502–511.

Miller, P. S., Boone, J. D., Briggs, J. R., et al. (2014). Simulating free-roaming cat population management options in open demographic environments. *PLoS ONE*, 9, e113553.
