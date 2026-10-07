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

## Ordering check

Prey-years lost: cull ___ < TNR ___ < unmanaged ___

If this holds qualitatively, V1 is validated. If not, debug the mechanism breaking the ordering before running Experiment 1.

## Observations / issues found

_(fill in as you go)_

## Calibration notes

If results are extreme in either direction, these parameters are the main tuning knobs:
- `p-predation` — raises/lowers predation pressure (currently 0.1)
- `K-prey` — raises/lowers prey resilience (currently 500)
- `food-multiplier` — raises/lowers overall food availability (currently 1.0)
- `base-immigration` — raises/lowers how much culling-created vacancies refill (currently 6)
- Food capacity scale (hardcoded in `setup-patches`, low/mid/high = 0.3 / 1.0 / 2.0) — affects immigration responsiveness
