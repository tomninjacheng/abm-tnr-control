# Viva Code Walkthrough — Preparation Notes

**Purpose:** quick-reference for the viva's "point at this line and explain" / "modify this live" moments. Complements `viva_script.md` (which is prose Q&A); this doc is code-anchored.

**File:** `cat_management_mvp.nlogox` — one source file, ~670 lines of NetLogo wrapped in XML. Code lives inside the `<code><![CDATA[...]]></code>` block starting at line 3.

**Before the viva opens**, open the file in NetLogo 7.0.4, click **setup** once (verify sliders are at the ODD baseline — see §0 below), and then be ready to click **go**.

---

## 0. Reference configuration (set sliders to these before setup)

| Slider | Reference value | Why |
|---|---|---|
| `initial-cat-population` | **300** | Matches ODD baseline; gives 48 cats/km² in Wilson 1994 Canberra range (19–90) |
| `initial-prey-population` | **500** | Matches `K-prey` so prey start at carrying capacity |
| `cats-processed-per-month` | **20** | Günther et al. 2022 80% coverage reference |
| `base-immigration` | **6** | ODD default |
| `food-multiplier` | **1.0** | Baseline (not feeding-ban scenario) |
| `food-regen-rate` | **0.5** | ODD default |
| `p-predation` | **0.1** | ODD default |
| `K-prey` | **500** | Fairy-wren urban upper bound per anchoring doc |
| `strategy` | **cull** OR **tnr** | Shown in demo, swapped between runs |

Sliders now default to these values; `initial-cat-population=300` and `cats-processed-per-month=20` were corrected from earlier defaults (500 / 15) to match the ODD reference.

---

## 1. File structure (what's where)

| Lines | Section | What |
|---|---|---|
| 3–13 | Header comments | Research question + metric formula + reference effort |
| 14–42 | `globals [...]` | 11 fixed rates (hardcoded in `setup-globals`) + 8 internal counters |
| 44–56 | breeds + agent-own | `cats-own`: home-patch, sex, age, status. `preys-own`: age. |
| 58–61 | `patches-own` | food-capacity (static), food-current (dynamic) |
| 67–168 | SETUP | `setup`, `setup-globals`, `setup-patches` (four-tier food), `setup-cats`, `setup-preys` |
| 173–193 | GO loop | 7-phase tick in fixed order |
| 198–338 | PHASE PROCEDURES | 1 procedure per phase |
| 343–353 | Reporters | For monitors on the interface |
| 359–675 | TESTS | 13 `test-*` procedures runnable via `run-all-tests` in Command Center |

**One-liner for "walk me through the structure":**
> "Globals, breeds, patches-own at the top. Then setup, then a seven-phase go loop, then one procedure per phase, then reporters, then thirteen unit tests I wrote during development that I can run live via `run-all-tests` in the Command Center."

---

## 2. The go loop — the heart of the model (lines 175–189)

```netlogo
to go
  cats-move-and-feed              ;; Phase 1
  immigrate                       ;; Phase 2 (reads post-feeding, pre-regen food)
  regenerate-food                 ;; Phase 3
  prey-move                       ;; Phase 4
  predate                         ;; Phase 5
  cats-reproduce                  ;; Phase 6a
  cats-age-and-die                ;; Phase 6a
  preys-reproduce                 ;; Phase 6b
  preys-age-and-die               ;; Phase 6b
  intervene                       ;; Phase 7 — runs every tick (no burn-in)
  tally                           ;; Phase 8
  tick
  if ticks >= 120 [ stop ]
end
```

**Memorise the ordering rationale** (any examiner on this project will probe this):

1. **Feed → immigrate** so immigration reads *depleted* food = responsive vacuum effect.
2. **Immigrate → regen** so regeneration doesn't mask depletion before the signal fires.
3. **Prey move → predate** so prey chance of encounter is after their random walk.
4. **Reproduce → age → die** inside Phase 6 so kittens born this tick don't get aged + die-rolled in the same tick (they're age 0 after reproduce, age 1 after age-and-die).
5. **No burn-in guard.** V1 runs intervention from tick 0. Removed in a late design iteration (see §16 note below): because TNR and cull share the identical initial condition, the initial transient cancels in the headline-ratio numerator, so burn-in added only cosmetic cleanliness. Removing it simplifies the model and makes intervention effects start at tick 0 for a more direct demonstration.
6. **Tally before tick** so `prey-years-lost` accumulates at tick t, not t+1.

If asked "what happens if you reorder?":
> "The two most load-bearing orderings are feed-before-immigrate (otherwise the vacuum signal flatlines) and reproduce-before-age-and-die (otherwise kittens die on their birth tick). I'd flag either reordering as changing model behaviour. The others — e.g., prey-move vs predate order — would shift stochasticity but not the mean outcome."

If asked "why no burn-in":
> "The headline metric is a ratio with a numerator that's a *difference* between TNR and cull cumulative predation. Both scenarios share the same initial condition, so initial transient predation contributes equally and cancels in the difference. Burn-in therefore adds no scientific value for this metric — only cosmetic cleanliness. We simplified the model by removing it; intervention runs from tick 0."

---

## 3. Phase 1 — `cats-move-and-feed` (lines 198–207)

```netlogo
to cats-move-and-feed
  ask cats [
    let candidates patches in-radius territory-radius
    let target max-one-of candidates [food-current]
    if target != nobody [ move-to target ]
    ask patch-here [
      set food-current max (list 0 (food-current - food-consumption))
    ]
  ]
end
```

**Line-by-line quick notes:**
- `patches in-radius territory-radius` — a *disc* of patches within Euclidean distance 3. Includes current patch. Not a Moore 7×7 square.
- `max-one-of candidates [food-current]` — picks the patch with the highest food-current; **random tiebreak** built in.
- `if target != nobody [ move-to target ]` — guards against empty agentset (defensive; shouldn't fire in practice).
- `max (list 0 ...)` — floor at zero; prevents negative food.

**Likely V2 question: "You process cats sequentially. What if two cats want the same patch?"**
> "The randomised processing order inside `ask cats` makes it first-come-first-served. The first cat eats, lowering food-current on that patch; by the time the second cat computes `max-one-of`, that same patch has less food and may no longer be the max. Deliberate: it captures competition without needing explicit resource contention logic."

**Likely V2 question: "Why not weight the move by sex or hunger?"**
> "Mating is not spatial in V1 — reproduction is a direct monthly probability per intact female. And we deliberately removed the hunger/health state from an earlier iteration for scope. So territory-radius here is pure food-search; a sex-specific or hunger-driven move adds state without changing the inter-strategy comparison."

---

## 4. Phase 2 — `immigrate` (lines 210–235)

```netlogo
to immigrate
  let total-cap sum [food-capacity] of patches
  let total-cur sum [food-current] of patches
  ifelse total-cap <= 0 [
    set current-immigration-rate 0
  ] [
    set current-immigration-rate base-immigration * (total-cur / total-cap)
  ]
  let n-new random-poisson current-immigration-rate
  ...
  create-cats n-new [
    move-to one-of edges
    ...
    set age 12 + random 25    ;; uniform 12..36
    ...
  ]
end
```

**Likely V1 question: "Explain the immigration formula."**
> "`current-immigration-rate` is `base-immigration × (total food currently available / total food capacity)`. At full food (nobody's eaten), ratio is 1 and rate equals the slider. At zero food (everything consumed), rate is 0. Half-food → half-rate. We then draw the integer number of actual immigrants from a Poisson with that mean, so we get stochastic monthly variation."

**Likely V2 question: "Why Poisson?"**
> "Immigration is a rare-event count: each hour of each day, some cat may or may not wander in. Over a month that produces a Poisson count with a stable rate parameter. Standard choice for arrival processes in population ecology."

**Likely V2 question: "Why read food BEFORE regeneration?"**
See the viva_script.md Q&A on this — the answer is in prose form there. Short version: makes signal responsive to actual depletion.

**Likely V2 question: "Why do immigrants arrive at age 12–36 months?"**
> "They're adults — kittens don't disperse alone. The 12–36 range is uniform; a dispersing feral is realistically a young adult, not a geriatric cat."

---

## 5. Phase 3 — `regenerate-food` (lines 237–243)

Simple one — each patch regains `food-regen-rate × food-capacity` units, capped at `food-capacity`. Also updates `pcolor` for visualisation.

**Likely V1 question: "What's `scale-color green ... 0 (3 * food-multiplier)`?"**
> "Maps food-current to green intensity. The `0 (3 × food-multiplier)` is the colour-scale range — zero at the dark end, 3× the multiplier at the bright end. We use 3 instead of 2 so even the 2.0-capacity cells aren't fully white, which was happening when the range was 2."

---

## 6. Phase 4 — `prey-move` (lines 245–249)

```netlogo
to prey-move
  ask preys [ move-to one-of patches in-radius prey-search-radius ]
end
```

**Shortest procedure in the model.** Prey random-walk within radius 2 cells. No habitat preference, no cat avoidance.

**Likely V2 question: "Why no cat avoidance?"**
> "Scope cut. In reality Fairy-wrens have some capacity to detect and avoid cats, but modelling perceptual range + flight response adds state without serving the research question. The simplification biases prey mortality upward uniformly across both strategies, so the inter-strategy comparison is unaffected."

---

## 7. Phase 5 — `predate` (lines 252–265)

```netlogo
to predate
  set prey-deaths-this-month 0
  ask preys [
    let adults-nearby cats in-radius predation-radius with [age >= 6]
    if any? adults-nearby [
      if random-float 1 < p-predation [
        set prey-deaths-this-month prey-deaths-this-month + 1
        set cumulative-prey-deaths cumulative-prey-deaths + 1
        die
      ]
    ]
  ]
end
```

**Key design choice: binary presence.** Two or more cats in range doesn't double the kill probability — it's `p-predation` regardless. See `viva_script.md` Q&A "Why only adults hunt..." for the three-reason defence.

**Likely V2 question: "Why not scale by cat density?"**
> "We tested both formulations during design. The scaled version (`1 - (1 - p)^n_cats`) made cat clusters near food hotspots the sole driver of predation and the inter-strategy difference nearly vanished. The binary version lets spatial clustering matter without being deterministic. The ODD §4 Key Assumptions documents this choice."

**Likely modification exercise: "Make sterilised cats hunt at a different rate."**
Live modification (good to practice):
```netlogo
;; In predate, replace line:
;;   let adults-nearby cats in-radius predation-radius with [age >= 6]
;; With:
let intact-nearby cats in-radius predation-radius with [age >= 6 and status = "intact"]
let steri-nearby  cats in-radius predation-radius with [age >= 6 and status = "sterilised"]
if any? intact-nearby or any? steri-nearby [
  let effective-p (ifelse-value any? intact-nearby [p-predation] [0]) +
                  (ifelse-value any? steri-nearby [p-predation * sterilised-hunting-fraction] [0])
  if random-float 1 < min (list 1 effective-p) [ ... die ... ]
]
```
Add a slider for `sterilised-hunting-fraction` with default 1.0 (= current behaviour). Explain to examiner this reproduces our baseline when the slider = 1 and makes TNR look better as it drops.

---

## 8. Phase 6a — `cats-reproduce` and `cats-age-and-die` (lines 267–291)

```netlogo
to cats-reproduce
  ask cats with [sex = "F" and age >= 6 and status = "intact"] [
    if random-float 1 < p-birth [
      hatch litter-size [
        set age 0
        set status "intact"
        set sex ifelse-value (random-float 1 < 0.5) ["F"] ["M"]
        set home-patch [patch-here] of myself
        ...
      ]
    ]
  ]
end
```

**Key:** `hatch` creates offspring of the same breed at the parent's location, inheriting their position. Each kitten gets a 50/50 sex coin. `[patch-here] of myself` → the mother's patch (`myself` inside a `hatch` refers to the parent).

```netlogo
to cats-age-and-die
  ask cats [
    set age age + 1
    let p-die ifelse-value (age < 6) [d-juvenile-cat] [d-adult-cat]
    if random-float 1 < p-die [ die ]
  ]
end
```

**Note the ordering:** `age + 1` BEFORE the mortality check, so a cat that just turned 6 months old is checked against `d-adult-cat`, not `d-juvenile-cat`. The test `test-cats-age-and-die` verifies this (line 568 in the code — a cat starting at age 5 should die at the adult rate because `age + 1 = 6`).

**Likely V2 question: "Why juvenile mortality 0.25?"**
See the main viva_script.md Q&A — answer is anchored to Mirmovitch 1995 urban kitten survival of 16% from Denny & Dickman 2010 §3.7, p.18.

---

## 9. Phase 6b — `preys-reproduce` and `preys-age-and-die` (lines 293–318)

```netlogo
to preys-reproduce
  let n-prey count preys
  let factor max (list 0 (1 - (n-prey / K-prey)))
  ask preys with [age >= 2] [
    if random-float 1 < 0.5 [          ;; implicit 50/50 sex ratio for prey
      if random-float 1 < (p-prey-birth * factor) [
        hatch prey-litter-size [ ... ]
      ]
    ]
  ]
end
```

**Logistic reduction via `factor`:** at N = K, factor = 0 (no births). At N = 0, factor = 1 (max rate). This prevents prey from exploding when cats are suppressed. Without it, prey rates would give 50%/year growth → 500 → 60,000 over 10 years.

**Implicit sex ratio:** we didn't store sex on preys to keep state small. The `random-float 1 < 0.5` gate is the equivalent of filtering to females.

**Likely V2 question: "Why no explicit sex on preys?"**
> "Scope. The prey-level mating logic doesn't appear anywhere in the research question — we only need recruitment rate. One scalar for 'is this bird reproducing this month' captures what we need. If we later want male-biased surplus or male-only cat kills, we'd add it."

---

## 10. Phase 7 — `intervene` (lines 320–338)

```netlogo
to intervene
  let pool cats with [status = "intact" and age >= 6]
  if not any? pool [ stop ]
  let n-take min (list cats-processed-per-month count pool)
  let selected n-of n-take pool

  if strategy = "tnr" [
    ask selected [ set status "sterilised" set color red ]
    set cumulative-tnr-count cumulative-tnr-count + n-take
  ]
  if strategy = "cull" [
    ask selected [ die ]
    set cumulative-cull-count cumulative-cull-count + n-take
  ]
end
```

**Key points:**
- `pool` filters to intact adults — kittens and already-sterilised cats are not eligible (defended in viva_script.md).
- `n-take` is the min of effort and pool size, so if the population crashes below the effort level, we just process everyone intact and no further.
- `n-of n-take pool` is random selection without replacement.
- TNR mutates `status` and `color`; cull calls `die`. Culled cats are gone from `cats` on the next tick.
- The counters `cumulative-tnr-count` and `cumulative-cull-count` are the denominators for the headline metric.

**Likely V2 question: "Why random selection and not spatially-targeted?"**
> "Scope. Real programs target high-density areas; we don't. The ODD §4 limitations list flags this. Adding spatial targeting is a candidate V2 extension."

**Likely modification exercise: "Change the strategy to prefer catching females over males."**
```netlogo
;; In intervene, replace:
;;   let pool cats with [status = "intact" and age >= 6]
;; With:
let female-pool cats with [status = "intact" and age >= 6 and sex = "F"]
let male-pool   cats with [status = "intact" and age >= 6 and sex = "M"]
let selected (sentence (n-of (min (list n-take-females count female-pool)) female-pool)
                        (n-of (...) male-pool))
```
Flag to examiner: "In reality TNR programs don't preferentially target females because trap-shy behaviour is sex-independent, but this would let us test what happens if they did."

---

## 11. Internal state / counters (lines 32–40)

| Counter | Role in metric |
|---|---|
| `cumulative-prey-deaths` | Numerator — raw predation count over the run |
| `cumulative-cull-count` | Denominator of cost(20) — only incremented under cull strategy |
| `cumulative-tnr-count` | Reported for interpretation; not in the metric |
| `prey-years-lost` | Secondary metric; integrated deficit vs baseline |
| `prey-deaths-this-month`, `immigrants-this-month` | For live plots on the interface |
| `current-immigration-rate` | The λ you can watch dropping/rising live |

**Live-demo tip:** point at `current-immigration-rate` or `cumulative-cull-count` in a monitor as the run progresses. Narrate: "immigration drops when cats pack a food cluster; the cull counter ticks up by ~20 every month after month 12."

---

## 12. Tests (lines 359–675)

Thirteen `test-*` procedures. Run via `run-all-tests` in the Command Center.

If asked "did you test this?" or "how do we know this works?":
> "Yes — thirteen unit tests I wrote during development, covering patch food distribution, agent setup, each of the seven phase procedures with specific scenarios, and a full 12-tick go run. For example, `test-predate` has three scenarios: no cat → prey survives; adult cat present → statistical kill rate within 3σ of p-predation across 500 trials; kitten present → no kills. I can run them live via `run-all-tests` in the Command Center."

**Do run `run-all-tests` once in rehearsal** to confirm every test still passes with the current code. Takes a few seconds.

---

## 13. Interface sliders (lines 673–696)

All 9 controls:
- **Chooser** `strategy` (tnr / cull)
- **Sliders** for the 8 numeric parameters listed in §0

**Hardcoded in `setup-globals` (NOT on sliders):** `p-birth`, `litter-size`, `d-juvenile-cat`, `d-adult-cat`, `p-prey-birth`, `prey-litter-size`, `d-juvenile-prey`, `d-adult-prey`, `territory-radius`, `food-consumption`, `predation-radius`, `prey-search-radius`.

**Why some are sliders and others aren't:**
> "Design parameters a user might want to sweep for sensitivity are on sliders — strategy, effort, immigration, food, predation, carrying capacity. Demographic rates are hardcoded in `setup-globals` because they're anchored to the Denny & Dickman literature and shouldn't drift during a demo. The sensitivity analysis in `sensitivity_notes.md` perturbs the hardcoded ones programmatically — the slider defaults aren't the right place for exploratory wiggle."

---

## 14. BehaviorSpace experiments (end of .nlogox file)

Three experiments pre-configured:

- **Exp1_matched_effort** — strategy × effort{0..40 step 5} × 30 reps = 540 runs. Primary. Produces cost(N) curve.
- **Exp2_immigration_sensitivity** — strategy × effort × base-immigration{2,6,15} × 30 reps = 900 runs.
- **Exp3_feeding_ban** — strategy × effort × food-multiplier{0.3, 0.7, 1.0} × 30 reps = 900 runs.

See `behaviorspace_notes.md` for running them and the post-hoc analysis.

If asked "have you run these?":
> "Not full 30-rep sweeps yet — those take 1–3 hours each. We ran a 2-rep dry run on Exp1 to confirm the output CSV structure is correct. Our OAT sensitivity analysis in `sensitivity_notes.md` is the first-pass finding we have ready today, from the deterministic non-spatial projection. Full NetLogo BehaviorSpace is the follow-up."

---

## 15. Likely "modify this live" exercises — practice list

Pick two of these and actually try them in NetLogo before the viva:

1. **Turn off immigration.** Set `base-immigration = 0` on the slider → setup → go. Observation: unmanaged cat population should slowly decline because internal R₀ ≈ 1.5 is marginal and immigration was the main growth driver. Culling becomes trivially effective.
2. **Run with no intervention.** Set `cats-processed-per-month = 0` → setup → go for 120 ticks. Observation: cat count should drift upward from immigration + internal reproduction; prey should decline from predation.
3. **Switch strategy mid-run.** Setup, run 60 ticks with cull, then change the chooser to tnr and continue. Narrate what happens to the intact/sterilised plot.
4. **Add a new reporter.** In the Command Center: `print mean [age] of cats` — gives the mean cat age right now. Good for showing you can introspect model state live.
5. **Compute cost(20) by hand.** After two runs (one cull, one tnr at effort 20), read off `cumulative-prey-deaths` and `cumulative-cull-count` from the monitors and compute the ratio. Compare against the sensitivity-analysis baseline value (~0.08).

---

## 16. Known inconsistencies to acknowledge if challenged

Be ready to flag these honestly if the examiner spots them:

1. **Slider default `base-immigration = 6`** vs **deterministic projection used `base-immigration = 10`**. The deterministic projection baseline cost(20) = 0.076 would be *higher* (~0.13 by interpolation) if re-run at base-immigration = 6. Rank-order sensitivity findings are not affected.
2. **ODD specifies 500 prey; slider default is 500 ✓**, but K-prey is also 500 so prey start at carrying capacity → no "initial growth" phase. If asked why no initial prey growth phase: "By design — we want to measure cat impact on an at-equilibrium prey population, not during a boom phase."
3. **No burn-in in V1.** Earlier design iterations had a 12-month burn-in before intervention; removed because the headline-ratio metric is a difference between TNR and cull scenarios that share the same initial transient — the transient cancels in the numerator, so burn-in added only cosmetic cleanliness. Say: "Intervention runs from tick 0. The initial transient is identical in TNR and cull scenarios, so it cancels in the headline ratio. We simplified by removing burn-in; the metric interpretation stays the same and the demo starts cleanly at tick 0."
4. **No seed control.** Each run is non-deterministic unless the examiner calls `random-seed N` in the Command Center first. If asked for reproducibility: "You can call `random-seed 42` before setup; the behaviorspace_notes.md documents a seed-determinism check for Exp1."

---

## 17. Final checklist for day-of

- [ ] NetLogo 7.0.4 open with the .nlogox file loaded
- [ ] Sliders at the §0 reference values before setup
- [ ] `run-all-tests` executed once in rehearsal; all PASS
- [ ] Can click setup + go + show live plots while narrating
- [ ] Can switch strategy chooser and re-setup to show the other scenario
- [ ] Can open BehaviorSpace (Tools → BehaviorSpace) to show the three experiments exist
- [ ] Can show `results/sensitivity_tornado.png` if asked about sensitivity
- [ ] Have `parameter_anchoring.md`, `ODD_protocol_final.md`, `sensitivity_notes.md`, and `viva_script.md` open in another window for ad-hoc reference
