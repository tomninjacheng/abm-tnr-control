# V1 Model Validation — NetLogo vs Deterministic Projection

**Date:** 2026-10-08
**Reference projection:** `scratchpad/v1_projection_v2.py`
**Parameter anchoring:** `parameter_anchoring.md` (Denny & Dickman 2010 + Rowley 1965 / Russell & Rowley 1993)

## Research question (RQ-A)

> At matched monthly intervention effort, how many additional prey deaths does TNR cause per cat spared from culling over 10 years?

**Primary outcome metric:**
```
cost(N) = (prey_kills_TNR_at_N − prey_kills_cull_at_N) / cumulative_cats_culled_at_N
```

Headline value is `cost(20)` at our reference effort of 20 cats/month (= 80% annual coverage of initial N=300, matching Gunther et al. 2022's field threshold).

## Expected (from projection with Set B rates, base-immigration=10)

| Scenario | Final cats | Final prey | Cumulative kills |
|---|---|---|---|
| Unmanaged | ~1,900 (6× growth) | ~2 | ~477 |
| Cull @ 10 | ~317 | ~20 | ~490 |
| Cull @ 15 | ~0 by year 10 | ~82 | ~453 |
| Cull @ 20 | ~0 by year 5 | ~160 | ~366 |
| TNR @ 20 | ~314 | ~16 | ~484 |
| TNR @ 40 | ~311 | ~18 | ~485 |

**Projected headline value:** `cost(20) = (484 − 366) / ~300 ≈ 0.4 prey per cat killed`.

NetLogo results will differ in absolute magnitude due to:
- Spatial clustering (cats cluster near food, prey scattered — not captured in non-spatial projection)
- Stochasticity across replicates
- Different predation implementation (binary Moore-neighborhood check vs. exposure saturation function in projection)

What should **qualitatively match**:
- Unmanaged cat population grows substantially (not flat)
- TNR @ 40 is near-indistinguishable from TNR @ 20 (sterilised cats don't disappear faster at higher effort)
- Culling at or above 15 cats/month drives cats toward zero over the 10-year horizon
- `cost(20)` is positive and small-to-moderate (not zero, not hundreds)

## NetLogo baseline scenario results (fill in after running)

### Scenario 1 — Unmanaged (cats-processed-per-month = 0)

- strategy: tnr (irrelevant at effort = 0)
- base-immigration: 6 (default)
- food-multiplier: 1.0

| Metric | NetLogo value |
|---|---|
| Final adult cat count | |
| Final prey count | |
| Cumulative prey deaths | |

### Scenario 2 — TNR @ 20

| Metric | NetLogo value |
|---|---|
| Final adult intact | |
| Final adult sterilised | |
| Final prey | |
| Cumulative prey deaths | |
| Cumulative TNR'd | |

### Scenario 3 — Culling @ 20

| Metric | NetLogo value |
|---|---|
| Final adult cats | |
| Final prey | |
| Cumulative prey deaths | |
| Cumulative culled | |

### Headline derivation

```
cost(20) = (NetLogo TNR cumulative-prey-deaths at effort 20
           − NetLogo cull cumulative-prey-deaths at effort 20)
         / NetLogo cumulative-cull-count at effort 20
```

Fill in: cost(20) = ___ prey saved per cat killed.

## Post-hoc analysis across the full sweep (headline finding)

After Experiment 1 BehaviorSpace completes:

### Effort-to-coverage mapping at N=300:

| cats/month | annual coverage | literature anchor |
|---|---|---|
| 5 | 20% | well below minimum |
| 10 | 40% | below McCarthy threshold |
| 15 | 60% | near McCarthy et al. 57% threshold |
| 20 | 80% | **Gunther et al. threshold — reference** |
| 25 | 100% | aggressive, approaching unrealistic |
| 30+ | 120%+ | operationally unrealistic |

### Procedure

For each effort `N ∈ {5, 10, 15, 20, 25, 30, 35, 40}`:

1. In each replicate, compute `cost_rep = (prey_kills_TNR_rep − prey_kills_cull_rep) / cull_count_rep`.
2. Take the median across the 30 replicates for each effort level.
3. Report `cost(N)` curve. Headline value is `cost(20)`.

### Sensitivity

- Across `base_immigration ∈ {2, 6, 15}` (Exp2): expect `cost(20)` to **decrease** under high immigration (culling's benefit offset by backfill, so each cat killed saves fewer prey).
- Across `food_multiplier ∈ {0.3, 0.7, 1.0}` (Exp3): expect `cost(20)` to **increase** under feeding bans (fewer total cats, each removal matters more).

## Calibration knobs

If results are extreme in either direction, these are the main tuning parameters:
- `p-predation` — raises/lowers predation pressure (currently 0.1)
- `K-prey` — raises/lowers prey resilience (currently 500)
- `d-juvenile-cat` — raises/lowers cat population growth (currently 0.25)
- `base-immigration` — slider; sweeps in Exp2
- `food-multiplier` — slider; sweeps in Exp3
