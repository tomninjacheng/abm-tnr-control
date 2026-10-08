# V1 Model Validation — NetLogo vs Deterministic Projection

**Date:** 2026-10-07
**Reference projection:** `/private/tmp/claude-501/-Users-tomcheng-Master-unimelb-S2-computational-modelling-ass2/27ca16ec-a811-4dc4-9b04-bc1ea117f044/scratchpad/v1_projection.py`

## Expected (from deterministic projection, non-spatial aggregate)

| Strategy | Final adult cats | Final prey | Prey-years lost | % deficit |
|---|---|---|---|---|
| Unmanaged | ~344 | ~20 | ~47,700 | 79.5% |
| TNR @ 20/mo | ~204 | ~40 | ~46,400 | 77.3% |
| Cull @ 20/mo | 0 | ~190 | ~33,500 | 55.9% |

**Required ordering (lower prey-years-lost = better for conservation):**
`cull < TNR < unmanaged`

NetLogo may show different absolute numbers because:
- Spatial clustering (not in projection) affects local predation
- Stochasticity means each run varies; the projection is deterministic
- The predation exposure function in the projection is a non-spatial approximation

What should **always** match:
- The ordering above
- Order-of-magnitude values (within 2× of projection)
- Unmanaged population drifts upward (not exponential explosion, not plateau at starting value)
- Culling @ 20/mo drives cats to zero
- TNR @ 20/mo leaves ~half the cats as sterilised adults

## NetLogo results (fill in after running)

### Scenario 1 — Unmanaged (cats-processed-per-month = 0)

- strategy: tnr (irrelevant at effort = 0)
- base-immigration: 6
- food-multiplier: 1.0
- Random seed used (if any): ____

| Metric | NetLogo value |
|---|---|
| Adult intact (tick 120) | |
| Adult sterilised | 0 |
| Kittens | |
| Prey | |
| Prey-years lost | |
| Cumulative prey deaths | |
| Immigration rate at tick 120 | |

### Scenario 2 — TNR @ 20/mo

- strategy: tnr
- cats-processed-per-month: 20
- base-immigration: 6
- food-multiplier: 1.0

| Metric | NetLogo value |
|---|---|
| Adult intact (tick 120) | |
| Adult sterilised | |
| Kittens | |
| Prey | |
| Prey-years lost | |
| Cumulative TNR'd | |

### Scenario 3 — Culling @ 20/mo

- strategy: cull
- cats-processed-per-month: 20

| Metric | NetLogo value |
|---|---|
| Adult intact (tick 120) | |
| Prey | |
| Prey-years lost | |
| Cumulative culled | |

## Ordering check (model sanity)

Prey-years lost: cull ___ < TNR ___ < unmanaged ___
Cumulative prey predation: cull ___ < TNR ___ < unmanaged ___

If both orderings hold qualitatively, the model is behaving sensibly. If not, debug before running Experiment 1.

## Post-hoc multiplier analysis (headline finding)

### Why cull @ 20 is the reference

At initial N=300, 20 cats/month = 240/year = **80% annual coverage of the initial population**. This matches Gunther et al. (2022)'s field threshold — aggressive-but-realistic for a well-resourced local program. See the ODD §1 Purpose for full literature anchoring.

Effort-to-coverage mapping at N=300:

| cats/month | annual coverage |
|---|---|
| 5 | 20% |
| 10 | 40% |
| 15 | 60% (near McCarthy et al. 57% threshold) |
| 20 | 80% (Gunther et al. threshold — reference) |
| 25 | 100% |
| 30 | 120% (operationally unrealistic) |
| 40 | 160% (operationally unrealistic) |

### Procedure

After the Experiment 1 BehaviorSpace run completes, open the CSV in Python/R/Excel and compute:

1. `T = median(cumulative-prey-deaths | strategy=cull, effort=20)` across the 30 replicates.
2. For each TNR effort `N ∈ {5, 10, 15, 20, 25, 30, 35, 40}`:
   - `K_N = median(cumulative-prey-deaths | strategy=tnr, effort=N)`.
3. Find smallest `N*` such that `K_{N*} ≤ T`.
4. Report the **TNR effort multiplier = `N* / 20`**.

Report possibilities:
- Clean multiplier (e.g., N* = 50, multiplier = 2.5×): "TNR needs 2.5× culling's effort for equivalent wildlife outcomes."
- No matching N* in the sweep: "TNR does not match culling at any effort level up to 40 cats/month; the TNR floor exceeds culling's output by X%."
- N* ≤ 20: "TNR achieves equivalence at or below culling's reference effort — strategies are near-equivalent at baseline."

Repeat the derivation across the three immigration levels (`base_immigration` ∈ {2, 6, 15}, Experiment 2) and three food levels (`food_multiplier` ∈ {0.3, 0.7, 1.0}, Experiment 3) to produce the sensitivity story.

## Observations / issues found

_(fill in as you go)_

## Calibration notes

If results are extreme in either direction, these parameters are the main tuning knobs:
- `p-predation` — raises/lowers predation pressure (currently 0.1)
- `K-prey` — raises/lowers prey resilience (currently 500)
- `food-multiplier` — raises/lowers overall food availability (currently 1.0)
- `base-immigration` — raises/lowers how much culling-created vacancies refill (currently 6)
- Food capacity scale (hardcoded in `setup-patches`, low/mid/high = 0.3 / 1.0 / 2.0) — affects immigration responsiveness
