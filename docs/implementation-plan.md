# NetLogo MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working NetLogo MVP of the V1 cat-management ABM, validated against the deterministic projection, with BehaviorSpace experiments configured for RQ-A.

**Architecture:** A single-file NetLogo model with two breeds (`cats`, `preys`), two patch variables (`food-capacity`, `food-current`), and a seven-phase `go` procedure matching the ODD. Each phase is a top-level procedure; `setup` initialises the world; data collection runs each tick; BehaviorSpace handles parameter sweeps.

**Tech Stack:** NetLogo 6.3+ (user-installed). No external dependencies. Python 3 (standard library) for ad-hoc verification against the deterministic projection in the scratchpad.

**Spec:**
- `/Users/tomcheng/Master/unimelb/S2/computational-modelling/ass2/ODD_protocol_final.md` (V1 ODD)
- `/Users/tomcheng/Master/unimelb/S2/computational-modelling/ass2/draft_handoff_final.md` (V1 design-decision handoff)

## Global Constraints

- **Platform:** NetLogo 6.3 or later.
- **Scales:** 50×50 world; monthly ticks; 120-tick simulations.
- **Reproducibility:** Every stochastic call uses NetLogo's RNG. Model must be fully deterministic given `random-seed`.
- **Performance target:** A single 120-tick run completes in ≤5 seconds on a modern laptop so that `3 strategies × 9 effort levels × 30 replicates = 810 runs` finishes in ~1 hour for Experiment 1.
- **Breed conventions:** Both breeds use `age` as an internal state variable. Cats also use `sex`, `status`, `home-patch`. Preys only use `age`.
- **Mortality semantics:** All death probabilities are *monthly* (per tick) and applied as independent Bernoulli draws per agent per tick.
- **Phase order (ODD §3):** feed → immigrate → regenerate → prey-move → predate → repro-and-mortality → intervene → tally. This order is load-bearing — immigration must read post-feeding (not post-regen) food.
- **Intervention eligibility:** Only cats with `age ≥ 6` AND `status = "intact"` are selectable. Kittens (<6 months) do not hunt or get trapped.
- **Metric:** Primary outcome is `prey-years-lost = Σ_t (K_prey_baseline − N_prey_t)` over all ticks. Secondary: cumulative predation kills.

## Review Focus

Five input classes / failure modes implied by the spec that no task's unit tests directly exercise but will bite real runs. Each is pinned to the task listed in parentheses with the test added to that task.

1. **Zero-population edges.** With heavy culling, intact-adult pool goes to 0; intervention must not error, immigration still fires correctly, prey predation iterates safely. (Task 11)
2. **Food fully depleted.** When Σ `food-current` = 0, immigration ratio must be 0 (not NaN or infinite); regen must still restore capacity. (Task 6)
3. **Age-boundary reclassification.** A cat aging from 5 to 6 months within a single tick must become eligible for intervention *and* a hunter in the same tick, in the correct order. (Task 9)
4. **Random seed determinism.** Two runs with the same `random-seed` and the same parameters must produce bit-identical trajectories. (Task 16)
5. **Fractional-litter edge.** `floor(cats_processed_per_month × hybrid_tnr_fraction)` with odd × 0.5 must still process the correct whole-cat count (e.g. 5 × 0.5 = 2 TNR, 3 cull). (Task 11)

---

## Project File Structure

```
ass2/
├── cat_management_mvp.nlogo         # The model (single-file; NetLogo convention)
├── docs/superpowers/plans/
│   └── 2026-10-07-netlogo-mvp.md    # This plan
├── scratchpad/
│   └── v1_projection.py             # Already in session scratchpad; reference for validation
├── validation_notes.md              # Short notes on validation runs (Task 15)
└── behaviorspace_notes.md           # Notes on BehaviorSpace experiments (Task 16)
```

The NetLogo model is one `.nlogo` file. All procedures live inside it in the Code tab. Interface widgets, plots, and BehaviorSpace experiments are stored in the same file but authored via the NetLogo GUI.

---

## Task 1: Scaffold the .nlogo file and initialise git

**Files:**
- Create: `cat_management_mvp.nlogo`
- Create: `.gitignore`

**Interfaces:**
- Consumes: nothing
- Produces: a NetLogo file with globals, breeds, breed-own, patches-own declared. No procedures yet.

- [ ] **Step 1: Initialise git repository**

```bash
cd /Users/tomcheng/Master/unimelb/S2/computational-modelling/ass2
git init
git branch -M main
```

- [ ] **Step 2: Create .gitignore**

Write to `.gitignore`:
```
.DS_Store
__pycache__/
*.pyc
.ipynb_checkpoints/
```

- [ ] **Step 3: Create the empty NetLogo file skeleton**

Create `cat_management_mvp.nlogo` with the following initial content. The `@#$#@#$#@` markers are NetLogo's section separators; the standard template needs them even for a code-only MVP.

```netlogo
;; Cat Management MVP — V1
;; Spec: ODD_protocol_final.md
;; Research question: at matched effort, which strategy (TNR / cull / hybrid)
;; produces the lowest cumulative prey-years lost over 10 years?

globals [
  ;; immigration tracking
  current-immigration-rate
  immigrants-this-month

  ;; prey tracking
  prey-deaths-this-month
  cumulative-prey-deaths

  ;; intervention tracking
  cumulative-tnr-count
  cumulative-cull-count

  ;; primary metric
  prey-years-lost
  prey-baseline  ;; = initial-prey-population, used as no-cat baseline reference
]

breed [cats cat]
breed [preys prey]

cats-own [
  home-patch
  sex       ;; "F" or "M"
  age       ;; months
  status    ;; "intact" or "sterilised"
]

preys-own [
  age       ;; months
]

patches-own [
  food-capacity    ;; static (clustered distribution set at setup)
  food-current     ;; dynamic (depleted by cat feeding, restored by regen)
]

;; procedures go below; added in later tasks
```

- [ ] **Step 4: Verify the file loads in NetLogo**

Open `cat_management_mvp.nlogo` in NetLogo. In the Code tab, click "Check" (the checkmark button). Expected: "Nothing named `go` has been defined" is OK — the model has no procedures yet, but declarations should parse without errors. If `globals`, `breed`, or `patches-own` declarations fail, fix the typo.

- [ ] **Step 5: Commit**

```bash
git add .gitignore cat_management_mvp.nlogo
git commit -m "feat: scaffold NetLogo file with declarations"
```

---

## Task 2: Patch food setup

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `setup-patches` procedure

**Interfaces:**
- Consumes: `food-multiplier` global (not yet a slider; hardcode 1.0 initially)
- Produces: `setup-patches` procedure. Postcondition: every patch has `food-capacity ∈ {0.3, 1.0, 2.0}` and `food-current = food-capacity`.

- [ ] **Step 1: Add a test procedure for the food distribution**

Add to the bottom of the Code tab:

```netlogo
to test-patch-food-distribution
  setup-patches
  let total-patches count patches
  let low count patches with [food-capacity = 0.3]
  let mid count patches with [food-capacity = 1.0]
  let high count patches with [food-capacity = 2.0]

  print (word "Low cells:  " low " (expected ~" (round (0.80 * total-patches)) ")")
  print (word "Mid cells:  " mid " (expected ~" (round (0.15 * total-patches)) ")")
  print (word "High cells: " high " (expected ~" (round (0.05 * total-patches)) ")")

  ;; Fuzzy pass criterion: each tier within ±3% of target
  let tol 0.03 * total-patches
  if abs (low  - 0.80 * total-patches) > tol [ error "FAIL: low tier off" ]
  if abs (mid  - 0.15 * total-patches) > tol [ error "FAIL: mid tier off" ]
  if abs (high - 0.05 * total-patches) > tol [ error "FAIL: high tier off" ]

  ;; Food-current should equal food-capacity after setup
  if any? patches with [food-current != food-capacity] [
    error "FAIL: food-current != food-capacity after setup"
  ]
  print "PASS: test-patch-food-distribution"
end
```

- [ ] **Step 2: Run the test; verify it fails**

In the NetLogo command center, type:
```
test-patch-food-distribution
```
Expected: error "Nothing named `setup-patches` has been defined."

- [ ] **Step 3: Implement `setup-patches`**

Add to the Code tab (above `test-patch-food-distribution`):

```netlogo
to setup-patches
  ;; Three-tier food distribution: 80% low (0.3), 15% mid (1.0), 5% high (2.0).
  ;; High cells cluster into 3 "commercial zones" at random grid locations.

  ;; Default everyone to low
  ask patches [ set food-capacity 0.3 ]

  ;; Randomly promote 15% to mid
  ask n-of (floor (0.15 * count patches)) patches with [food-capacity = 0.3] [
    set food-capacity 1.0
  ]

  ;; Place 3 high-food clusters
  let n-high floor (0.05 * count patches)
  let per-cluster floor (n-high / 3)
  repeat 3 [
    let center one-of patches
    ask center [
      ;; promote this patch and its neighbors within radius 2 (plus small random spread)
      ask patches in-radius 2 [
        if food-capacity < 2.0 and random-float 1 < 0.6 [
          set food-capacity 2.0
        ]
      ]
    ]
  ]

  ;; Scale by food-multiplier (allows feeding-ban scenarios later; default 1.0)
  ask patches [
    set food-capacity food-capacity * food-multiplier
    set food-current food-capacity
  ]

  ;; Visualisation (optional, nice for debugging)
  ask patches [ set pcolor scale-color green food-capacity 0 (2 * food-multiplier) ]
end
```

Note: `food-multiplier` is used but not yet declared. For now, declare it as a global by adding `food-multiplier` to the `globals` block and set it to 1.0 in a later setup task. If the test fails because of this, see Step 5.

- [ ] **Step 4: Declare and initialise food-multiplier**

In the `globals` block (top of file), add `food-multiplier` to the list. Then create a short `setup-globals` procedure above `setup-patches`:

```netlogo
to setup-globals
  set food-multiplier 1.0
  set prey-baseline 500
  set current-immigration-rate 0
  set immigrants-this-month 0
  set prey-deaths-this-month 0
  set cumulative-prey-deaths 0
  set cumulative-tnr-count 0
  set cumulative-cull-count 0
  set prey-years-lost 0
end
```

Modify `test-patch-food-distribution` to call `setup-globals` first:
```netlogo
to test-patch-food-distribution
  clear-all
  setup-globals
  setup-patches
  ... (rest unchanged)
end
```

- [ ] **Step 5: Run the test; verify it passes**

```
test-patch-food-distribution
```
Expected: three lines of count output, then `PASS: test-patch-food-distribution`. The visual should show a greenish map with ~3 brighter clusters.

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: patch food distribution with 3-tier clustered layout"
```

---

## Task 3: Agent initialization and setup wrapper

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `setup-cats`, `setup-preys`, and the top-level `setup` procedure.

**Interfaces:**
- Consumes: `initial-cat-population`, `initial-prey-population` globals (default 300 and 500).
- Produces: `setup` procedure. Postcondition: 300 cats placed uniformly, 500 preys placed uniformly, both with correct state variables.

- [ ] **Step 1: Add globals for initial populations**

Add to the `globals` list: `initial-cat-population`, `initial-prey-population`. Then in `setup-globals`, initialise them:

```netlogo
set initial-cat-population 300
set initial-prey-population 500
```

- [ ] **Step 2: Write the test**

```netlogo
to test-agent-setup
  setup
  if count cats != initial-cat-population [ error "FAIL: wrong cat count" ]
  if count preys != initial-prey-population [ error "FAIL: wrong prey count" ]
  ;; Cat sex ratio approx 50/50
  let n-female count cats with [sex = "F"]
  let imbalance abs (n-female - 0.5 * count cats)
  if imbalance > 30 [ error "FAIL: cat sex ratio too skewed" ]
  ;; All cats intact, ages 6–48
  if any? cats with [status != "intact"] [ error "FAIL: non-intact cats at setup" ]
  if any? cats with [age < 6 or age > 48] [ error "FAIL: cat age out of range" ]
  ;; Prey ages 2–36
  if any? preys with [age < 2 or age > 36] [ error "FAIL: prey age out of range" ]
  print "PASS: test-agent-setup"
end
```

- [ ] **Step 3: Run the test; verify failure**

```
test-agent-setup
```
Expected: error "Nothing named `setup` has been defined."

- [ ] **Step 4: Implement `setup-cats`, `setup-preys`, and `setup`**

Add to the Code tab:

```netlogo
to setup-cats
  create-cats initial-cat-population [
    setxy random-xcor random-ycor
    set home-patch patch-here
    set sex ifelse-value (random-float 1 < 0.5) ["F"] ["M"]
    set age 6 + random 43     ;; uniform 6..48 inclusive
    set status "intact"
    set shape "default"
    set color yellow
    set size 0.9
  ]
end

to setup-preys
  create-preys initial-prey-population [
    setxy random-xcor random-ycor
    set age 2 + random 35     ;; uniform 2..36
    set shape "circle"
    set color white
    set size 0.6
  ]
end

to setup
  clear-all
  setup-globals
  setup-patches
  setup-cats
  setup-preys
  reset-ticks
end
```

- [ ] **Step 5: Run the test; verify PASS**

```
test-agent-setup
```
Expected: `PASS: test-agent-setup`. View should show yellow cats and white dots scattered uniformly.

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: agent initialization and top-level setup procedure"
```

---

## Task 4: Cat movement + feeding (Phase 1)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `cats-move-and-feed`.

**Interfaces:**
- Consumes: `territory-radius` (global, default 3), `food-consumption` (global, default 1.0), patch `food-current` state.
- Produces: `cats-move-and-feed`. Postcondition: each cat is at the highest-`food-current` patch within `territory-radius` of its *starting* position this tick, and that patch has had `food-consumption` deducted from its `food-current` (clamped ≥ 0).

- [ ] **Step 1: Add globals**

Add `territory-radius` and `food-consumption` to the `globals` block. In `setup-globals`, add:
```netlogo
set territory-radius 3
set food-consumption 1.0
```

- [ ] **Step 2: Write the test**

```netlogo
to test-cats-move-and-feed
  setup
  ;; Place a known high-food patch and a cat beside it
  ask patch 0 0 [ set food-capacity 2.0 set food-current 2.0 ]
  ask patch 1 0 [ set food-capacity 0.3 set food-current 0.3 ]
  ask cats [ die ]
  create-cats 1 [
    setxy 1 0
    set home-patch patch 1 0
    set sex "F" set age 24 set status "intact"
    set color yellow set shape "default"
  ]
  let food-before [food-current] of patch 0 0
  cats-move-and-feed
  let the-cat one-of cats
  if [patch-here] of the-cat != patch 0 0 [
    error (word "FAIL: cat did not move to best-food patch. At: " [patch-here] of the-cat)
  ]
  if [food-current] of patch 0 0 >= food-before [
    error "FAIL: patch food did not decrease after feeding"
  ]
  print "PASS: test-cats-move-and-feed"
end
```

- [ ] **Step 3: Run; verify failure**

```
test-cats-move-and-feed
```
Expected: error "Nothing named `cats-move-and-feed` has been defined."

- [ ] **Step 4: Implement the procedure**

```netlogo
to cats-move-and-feed
  ;; Each cat moves to the highest-food cell within territory-radius, then feeds.
  ask cats [
    let candidates patches in-radius territory-radius
    let target max-one-of candidates [food-current]
    ;; break ties by shuffling (max-one-of returns a random one of the ties already,
    ;; but we also want cats to prefer their own patch on exact-tie-with-current)
    if target != nobody [ move-to target ]
    ask patch-here [
      set food-current max (list 0 (food-current - food-consumption))
    ]
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

```
test-cats-move-and-feed
```
Expected: `PASS: test-cats-move-and-feed`.

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: cat movement toward food with feeding depletion"
```

---

## Task 5: Food regeneration (Phase 3)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `regenerate-food`.

**Interfaces:**
- Consumes: `food-regen-rate` (global, default 0.5), patch `food-capacity`, `food-current`.
- Produces: `regenerate-food`. Postcondition: every patch has `food-current` ← `min(food-capacity, food-current + food-regen-rate × food-capacity)`.

- [ ] **Step 1: Add global**

Add `food-regen-rate` to `globals`; in `setup-globals`: `set food-regen-rate 0.5`.

- [ ] **Step 2: Write the test**

```netlogo
to test-regenerate-food
  setup
  ;; Deplete all patches to zero
  ask patches [ set food-current 0 ]
  regenerate-food
  ;; After one regen, every patch should be at food-regen-rate × food-capacity
  if any? patches with [abs (food-current - food-regen-rate * food-capacity) > 0.001] [
    error "FAIL: regen amount mismatch"
  ]
  ;; After two more regens, patches should cap at capacity
  regenerate-food
  regenerate-food
  if any? patches with [food-current > food-capacity + 0.001] [
    error "FAIL: regen exceeded capacity"
  ]
  if any? patches with [food-current < food-capacity - 0.001] [
    error "FAIL: regen did not reach capacity after 3 cycles"
  ]
  print "PASS: test-regenerate-food"
end
```

- [ ] **Step 3: Run; verify failure**

```
test-regenerate-food
```

- [ ] **Step 4: Implement**

```netlogo
to regenerate-food
  ask patches [
    set food-current min (list food-capacity (food-current + food-regen-rate * food-capacity))
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

```
test-regenerate-food
```

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: patch food regeneration toward capacity"
```

---

## Task 6: Immigration (Phase 2) — includes zero-food edge-case test (Review Focus item 2)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `immigrate`.

**Interfaces:**
- Consumes: `base-immigration` (global, default 6), total `food-current` and `food-capacity` across patches.
- Produces: `immigrate`. Postcondition: `current-immigration-rate` set to `base-immigration × (Σ food-current / Σ food-capacity)`; drops `Poisson(rate)` immigrant cats at random edge patches as intact adults.

- [ ] **Step 1: Add global**

Add `base-immigration` to `globals`; in `setup-globals`: `set base-immigration 6`.

- [ ] **Step 2: Write the test — includes zero-food edge**

```netlogo
to test-immigrate
  setup
  let n-before count cats

  ;; Normal case: patches at full capacity → rate ≈ base-immigration
  immigrate
  print (word "Immigration rate at full food: " current-immigration-rate)
  if abs (current-immigration-rate - base-immigration) > 0.01 [
    error "FAIL: rate at full food does not match base-immigration"
  ]

  ;; Zero-food edge: rate must be exactly 0, no error
  ask patches [ set food-current 0 ]
  immigrate
  if current-immigration-rate != 0 [
    error "FAIL: rate at zero food should be 0"
  ]

  ;; Partial depletion
  ask patches [ set food-current food-capacity / 2 ]
  immigrate
  if abs (current-immigration-rate - base-immigration / 2) > 0.01 [
    error "FAIL: rate at half food should be ~half of base"
  ]
  print "PASS: test-immigrate"
end
```

- [ ] **Step 3: Run; verify failure**

```
test-immigrate
```

- [ ] **Step 4: Implement**

```netlogo
to immigrate
  let total-cap sum [food-capacity] of patches
  let total-cur sum [food-current] of patches
  ifelse total-cap = 0 [
    set current-immigration-rate 0
  ] [
    set current-immigration-rate base-immigration * (total-cur / total-cap)
  ]
  ;; Poisson draw via NetLogo's `random-poisson`
  let n-new random-poisson current-immigration-rate
  set immigrants-this-month n-new
  create-cats n-new [
    ;; place at a random edge patch
    let edges patches with [pxcor = min-pxcor or pxcor = max-pxcor or pycor = min-pycor or pycor = max-pycor]
    move-to one-of edges
    set home-patch patch-here
    set sex ifelse-value (random-float 1 < 0.5) ["F"] ["M"]
    set age 12 + random 25   ;; uniform 12..36
    set status "intact"
    set shape "default"
    set color yellow
    set size 0.9
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

```
test-immigrate
```

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: food-driven Poisson immigration with zero-food guard"
```

---

## Task 7: Prey random walk (Phase 4)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `prey-move`.

**Interfaces:**
- Consumes: `prey-search-radius` (global, default 2).
- Produces: `prey-move`. Postcondition: each prey has moved to a uniformly-random patch within `prey-search-radius` of its previous position.

- [ ] **Step 1: Add global**

Add `prey-search-radius`; `set prey-search-radius 2`.

- [ ] **Step 2: Write the test**

```netlogo
to test-prey-move
  setup
  ask preys [ die ]
  create-preys 1 [
    setxy 25 25
    set age 10
    set shape "circle" set color white set size 0.6
  ]
  let the-prey one-of preys
  let before [patch-here] of the-prey
  prey-move
  let after [patch-here] of the-prey
  if [distance before] of the-prey > prey-search-radius + 0.01 [
    error "FAIL: prey moved too far"
  ]
  print "PASS: test-prey-move"
end
```

- [ ] **Step 3: Run; verify failure**

- [ ] **Step 4: Implement**

```netlogo
to prey-move
  ask preys [
    let candidates patches in-radius prey-search-radius
    move-to one-of candidates
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: prey random walk within search radius"
```

---

## Task 8: Predation (Phase 5)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `predate`.

**Interfaces:**
- Consumes: `predation-radius` (global, default 1), `p-predation` (global, default 0.1).
- Produces: `predate`. Postcondition: each prey with ≥1 adult cat (age ≥ 6) within `predation-radius` of its position has died with probability `p-predation`; `prey-deaths-this-month` counts the deaths this call.

- [ ] **Step 1: Add globals**

Add `predation-radius` (= 1) and `p-predation` (= 0.1).

- [ ] **Step 2: Write the test**

```netlogo
to test-predate
  setup
  ask cats [ die ]
  ask preys [ die ]

  ;; Scenario A: one prey, no cat nearby — should always survive
  create-preys 1 [
    setxy 10 10
    set age 10
    set shape "circle" set color white
  ]
  predate
  if count preys != 1 [ error "FAIL: prey died with no cat present" ]

  ;; Scenario B: adult cat right next to prey — statistical test
  create-cats 1 [
    setxy 10 10
    set age 24
    set status "intact"
    set sex "F"
    set home-patch patch-here
    set shape "default" set color yellow
  ]
  ;; Expected monthly death prob is 0.1; run many times with fresh prey each time
  let n-trials 1000
  let n-dead 0
  repeat n-trials [
    ask preys [ die ]
    create-preys 1 [ setxy 10 10 set age 10 set shape "circle" ]
    set prey-deaths-this-month 0
    predate
    set n-dead (n-dead + prey-deaths-this-month)
  ]
  let observed (n-dead / n-trials)
  print (word "Observed kill rate: " observed " (expected " p-predation ")")
  if abs (observed - p-predation) > 0.03 [
    error "FAIL: kill rate too far from p-predation (3σ bound)"
  ]

  ;; Scenario C: kitten (<6mo) nearby — must NOT trigger predation
  ask cats [ die ]
  create-cats 1 [
    setxy 10 10
    set age 3   ;; kitten
    set status "intact"
    set sex "F"
    set home-patch patch-here
    set shape "default" set color yellow
  ]
  set n-dead 0
  repeat 500 [
    ask preys [ die ]
    create-preys 1 [ setxy 10 10 set age 10 set shape "circle" ]
    set prey-deaths-this-month 0
    predate
    set n-dead (n-dead + prey-deaths-this-month)
  ]
  if n-dead > 20 [ error "FAIL: kittens should not kill prey" ]
  print "PASS: test-predate"
end
```

- [ ] **Step 3: Run; verify failure**

- [ ] **Step 4: Implement**

```netlogo
to predate
  set prey-deaths-this-month 0
  ask preys [
    let hunters cats-here  ;; same patch
    ;; include neighbors within predation-radius
    let nearby-cats cats in-radius predation-radius
    let adults-nearby nearby-cats with [age >= 6]
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

- [ ] **Step 5: Run; verify PASS**

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: binary presence predation with adult-only hunters"
```

---

## Task 9: Cat reproduction + mortality (Phase 6a) — includes age-boundary test (Review Focus item 3)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `cats-reproduce`, `cats-age-and-die`.

**Interfaces:**
- Consumes: `p-birth` (0.17), `litter-size` (4), `d-juvenile-cat` (0.35), `d-adult-cat` (0.025).
- Produces: `cats-reproduce`, `cats-age-and-die`. Postcondition for `cats-reproduce`: each intact female (age ≥ 6) draws Bernoulli(p-birth); on success, `litter-size` new kittens appear at her patch with age 0, intact, random sex, home set to mother's patch. Postcondition for `cats-age-and-die`: every cat has age incremented by 1; each cat dies with p-die appropriate to its new age bucket (juvenile <6, adult ≥6).

- [ ] **Step 1: Add globals**

Add `p-birth` (0.17), `litter-size` (4), `d-juvenile-cat` (0.35), `d-adult-cat` (0.025) to globals; set in `setup-globals`.

- [ ] **Step 2: Write the test (incl. age-boundary)**

```netlogo
to test-cats-reproduce
  setup
  ask cats [ die ]
  ;; 1000 intact adult females for statistical power
  create-cats 1000 [
    setxy random-xcor random-ycor
    set home-patch patch-here
    set sex "F" set age 24 set status "intact"
    set shape "default" set color yellow
  ]
  let before count cats
  cats-reproduce
  let kittens count cats with [age = 0]
  let expected 1000 * p-birth * litter-size
  print (word "Kittens born: " kittens " (expected ~" expected ")")
  if abs (kittens - expected) > 0.1 * expected [
    error "FAIL: kitten count outside 10% band of expected"
  ]
  ;; Males should not have reproduced
  ask cats [ die ]
  create-cats 500 [ set sex "M" set age 24 set status "intact" set shape "default" set color yellow set home-patch patch-here ]
  cats-reproduce
  if any? cats with [age = 0] [ error "FAIL: males produced offspring" ]
  print "PASS: test-cats-reproduce"
end

to test-cats-age-and-die
  setup
  ask cats [ die ]
  ;; Age-boundary scenario: 1000 cats at age 5 (juvenile) will become adults next tick
  create-cats 1000 [
    setxy random-xcor random-ycor
    set age 5 set status "intact" set sex "F"
    set home-patch patch-here
    set shape "default" set color yellow
  ]
  cats-age-and-die
  ;; After ageing + 1, these are now age 6 (adult). The mortality roll was juvenile
  ;; (because they were age 5 going in — but see implementation note below).
  ;; The ODD says: age by 1, THEN apply mortality. So mortality rate used must be
  ;; based on NEW age (6+). Verify:
  let survived count cats
  let expected-survived 1000 * (1 - d-adult-cat)
  print (word "Age-5→6 survived: " survived " (expected adult-rate ~" expected-survived ")")
  if abs (survived - expected-survived) > 0.1 * expected-survived [
    error "FAIL: age-boundary cats should use ADULT mortality (new age ≥ 6)"
  ]
  print "PASS: test-cats-age-and-die"
end
```

- [ ] **Step 3: Run both tests; verify both fail**

- [ ] **Step 4: Implement**

```netlogo
to cats-reproduce
  ask cats with [sex = "F" and age >= 6 and status = "intact"] [
    if random-float 1 < p-birth [
      hatch litter-size [
        set age 0
        set status "intact"
        set sex ifelse-value (random-float 1 < 0.5) ["F"] ["M"]
        set home-patch [patch-here] of myself
        set shape "default"
        set color yellow
        set size 0.5
      ]
    ]
  ]
end

to cats-age-and-die
  ask cats [
    set age age + 1
    ;; mortality rate uses new age
    let p-die ifelse-value (age < 6) [d-juvenile-cat] [d-adult-cat]
    if random-float 1 < p-die [ die ]
  ]
end
```

- [ ] **Step 5: Run both tests; verify PASS**

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: cat reproduction and age-boundary-correct mortality"
```

---

## Task 10: Prey reproduction + mortality (Phase 6b)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `preys-reproduce`, `preys-age-and-die`.

**Interfaces:**
- Consumes: `p-prey-birth` (0.25), `prey-litter-size` (2), `K-prey` (500), `d-juvenile-prey` (0.30), `d-adult-prey` (0.05).
- Produces: `preys-reproduce` (logistic), `preys-age-and-die` (age-class flat rates).

- [ ] **Step 1: Add globals and defaults**

Add `p-prey-birth` (0.25), `prey-litter-size` (2), `K-prey` (500), `d-juvenile-prey` (0.30), `d-adult-prey` (0.05).

- [ ] **Step 2: Write the test**

```netlogo
to test-preys-reproduce
  setup
  ask preys [ die ]
  ;; At N = K_prey, logistic factor is 0 — no births
  create-preys K-prey [ set age 10 set shape "circle" ]
  preys-reproduce
  if any? preys with [age = 0] [
    error "FAIL: births at N = K_prey should be zero"
  ]

  ;; At N = K_prey / 2, logistic factor is 0.5 — expected births = 0.5*p_birth*litter per adult female
  ask preys [ die ]
  let n-adult-females 500
  create-preys n-adult-females [ set age 10 set shape "circle" ]
  ;; All female for test clarity
  ;; Logistic reduction uses total count = 500 vs K = 500, factor = 0
  ;; Need N < K to see births. Reset K:
  set K-prey 1000
  let factor max (list 0 (1 - (count preys / K-prey)))   ;; = 0.5
  let expected (0.5 * n-adult-females * p-prey-birth * factor * prey-litter-size)
  preys-reproduce
  let births count preys with [age = 0]
  print (word "Prey births at N=K/2: " births " (expected ~" expected ")")
  if abs (births - expected) > 0.2 * expected [
    error "FAIL: birth rate off"
  ]
  set K-prey 500  ;; restore
  print "PASS: test-preys-reproduce"
end

to test-preys-age-and-die
  setup
  ask preys [ die ]
  create-preys 1000 [ set age 10 set shape "circle" ]
  preys-age-and-die
  let survived count preys
  let expected 1000 * (1 - d-adult-prey)
  print (word "Prey survived: " survived " (expected adult ~" expected ")")
  if abs (survived - expected) > 0.1 * expected [
    error "FAIL: prey adult mortality off"
  ]
  print "PASS: test-preys-age-and-die"
end
```

- [ ] **Step 3: Run; verify both fail**

- [ ] **Step 4: Implement**

```netlogo
to preys-reproduce
  let n-prey count preys
  let factor max (list 0 (1 - (n-prey / K-prey)))
  ;; Note: we don't track prey sex in V1. Treat half of adults as females.
  ask preys with [age >= 2] [
    if sex-is-female-roll? [
      if random-float 1 < (p-prey-birth * factor) [
        hatch prey-litter-size [
          set age 0
          set shape "circle"
          set color white
          set size 0.5
        ]
      ]
    ]
  ]
end

to-report sex-is-female-roll?
  report random-float 1 < 0.5
end

to preys-age-and-die
  ask preys [
    set age age + 1
    let p-die ifelse-value (age < 2) [d-juvenile-prey] [d-adult-prey]
    if random-float 1 < p-die [ die ]
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: logistic prey reproduction and age-class mortality"
```

---

## Task 11: Intervention (Phase 7) — includes zero-pool edge (Review Focus item 1) and hybrid-rounding (Review Focus item 5)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `intervene`.

**Interfaces:**
- Consumes: `strategy` (chooser value), `cats-processed-per-month` (slider), `hybrid-tnr-fraction` (slider).
- Produces: `intervene`. Postcondition: up to N intact adult cats are processed per strategy; `cumulative-tnr-count` and `cumulative-cull-count` incremented accordingly.

- [ ] **Step 1: Add globals**

Add `strategy` (will be a chooser; default "tnr"), `cats-processed-per-month` (default 0), `hybrid-tnr-fraction` (default 0.5).

In `setup-globals`:
```netlogo
set strategy "tnr"
set cats-processed-per-month 0
set hybrid-tnr-fraction 0.5
```

- [ ] **Step 2: Write the test (incl. edges)**

```netlogo
to test-intervene
  ;; TNR: selected intact adults should flip to sterilised
  setup
  ask cats [ die ]
  create-cats 10 [
    setxy random-xcor random-ycor
    set home-patch patch-here
    set sex "F" set age 24 set status "intact"
    set shape "default" set color yellow
  ]
  set strategy "tnr"
  set cats-processed-per-month 5
  intervene
  if count cats with [status = "sterilised"] != 5 [ error "FAIL: TNR count wrong" ]
  if count cats with [status = "intact"] != 5 [ error "FAIL: TNR left count wrong" ]

  ;; Culling: selected intact adults should die
  ask cats [ die ]
  create-cats 10 [ setxy 0 0 set home-patch patch 0 0 set sex "F" set age 24 set status "intact" set shape "default" set color yellow ]
  set strategy "cull"
  set cats-processed-per-month 5
  intervene
  if count cats != 5 [ error "FAIL: cull should remove 5 cats" ]

  ;; Hybrid rounding: 5 processed × 0.5 = floor 2 TNR, 3 cull
  ask cats [ die ]
  create-cats 10 [ setxy 0 0 set home-patch patch 0 0 set sex "F" set age 24 set status "intact" set shape "default" set color yellow ]
  set strategy "hybrid"
  set cats-processed-per-month 5
  set hybrid-tnr-fraction 0.5
  intervene
  if count cats with [status = "sterilised"] != 2 [ error "FAIL: hybrid should TNR 2 cats (floor of 2.5)" ]
  if count cats != 7 [ error "FAIL: hybrid should leave 10 - 3 culled = 7 cats total" ]

  ;; Zero-pool edge: with no intact adults, intervene must not error
  ask cats [ die ]
  set cats-processed-per-month 5
  set strategy "cull"
  intervene       ;; should not error
  if count cats != 0 [ error "FAIL: intervene on empty pool should do nothing" ]

  ;; Kittens must NOT be eligible
  ask cats [ die ]
  create-cats 5 [ set age 3 set status "intact" set sex "F" set shape "default" set color yellow set home-patch patch-here ]
  set strategy "cull"
  set cats-processed-per-month 5
  intervene
  if count cats != 5 [ error "FAIL: kittens should not be eligible for intervention" ]
  print "PASS: test-intervene"
end
```

- [ ] **Step 3: Run; verify failure**

- [ ] **Step 4: Implement**

```netlogo
to intervene
  let pool cats with [status = "intact" and age >= 6]
  if not any? pool [ stop ]
  let n-take min (list cats-processed-per-month count pool)
  let selected n-of n-take pool

  if strategy = "tnr" [
    ask selected [ set status "sterilised" set color blue ]
    set cumulative-tnr-count cumulative-tnr-count + n-take
  ]
  if strategy = "cull" [
    ask selected [ die ]
    set cumulative-cull-count cumulative-cull-count + n-take
  ]
  if strategy = "hybrid" [
    let n-tnr floor (n-take * hybrid-tnr-fraction)
    let selected-list sort selected   ;; deterministic ordering within selection
    let to-tnr sublist selected-list 0 n-tnr
    let to-cull sublist selected-list n-tnr n-take
    foreach to-tnr [ c -> ask c [ set status "sterilised" set color blue ] ]
    foreach to-cull [ c -> ask c [ die ] ]
    set cumulative-tnr-count cumulative-tnr-count + n-tnr
    set cumulative-cull-count cumulative-cull-count + (n-take - n-tnr)
  ]
end
```

- [ ] **Step 5: Run; verify PASS**

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: intervention with TNR/cull/hybrid routing and edge-case guards"
```

---

## Task 12: Go procedure (orchestrate all phases)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add `go` and `tally`.

**Interfaces:**
- Consumes: all phase procedures from Tasks 4–11.
- Produces: `go`. Postcondition: one tick advances all seven phases in ODD order, updates metrics, and stops at tick 120.

- [ ] **Step 1: Write the test**

```netlogo
to test-go-runs-without-error
  setup
  repeat 12 [ go ]      ;; 1 year of simulation
  print (word "After 12 ticks: cats=" count cats " preys=" count preys)
  if ticks != 12 [ error "FAIL: tick counter not advancing" ]
  print "PASS: test-go-runs-without-error"
end
```

- [ ] **Step 2: Run; verify failure**

- [ ] **Step 3: Add `burn-in-months` global**

Add `burn-in-months` to the `globals` block; in `setup-globals`:
```netlogo
set burn-in-months 12
```

Burn-in is per ODD §5 Initialisation: no intervention applied for the first 12 months to let the population settle away from the uniform-random initial distribution.

- [ ] **Step 4: Implement `go` and `tally`**

```netlogo
to go
  ;; Phase 1
  cats-move-and-feed
  ;; Phase 2 — immigration reads post-feeding, pre-regen food (ODD §3)
  immigrate
  ;; Phase 3
  regenerate-food
  ;; Phase 4
  prey-move
  ;; Phase 5
  predate
  ;; Phase 6
  cats-reproduce
  cats-age-and-die
  preys-reproduce
  preys-age-and-die
  ;; Phase 7 — intervention after burn-in only (ODD §5)
  if ticks >= burn-in-months [ intervene ]
  ;; Phase 8
  tally
  tick
  if ticks >= 120 [ stop ]
end

to tally
  ;; Prey-years-lost accumulates each tick: baseline minus actual
  let deficit max (list 0 (prey-baseline - count preys))
  set prey-years-lost prey-years-lost + deficit
end
```

- [ ] **Step 5: Run; verify PASS**

In the NetLogo Command Center:
```
test-go-runs-without-error
```
Expected: `PASS: test-go-runs-without-error`.

- [ ] **Step 6: Commit**

```bash
git add cat_management_mvp.nlogo
git commit -m "feat: go procedure with burn-in, phase orchestration, prey-years-lost metric"
```

---

## Task 13: Data collection, monitors, and plots

**Files:**
- Modify: `cat_management_mvp.nlogo` — add plot/monitor widgets via the NetLogo interface.

**Interfaces:**
- Consumes: globals and agent counts.
- Produces: three plots in the interface:
  - `Cat population` (adult intact, adult sterilised, kittens, total)
  - `Prey population` (total)
  - `Immigration rate` (current-immigration-rate)
- Monitors for key stats: adult-intact-count, adult-sterilised-count, kitten-count, prey-count, cumulative-prey-deaths, prey-years-lost, cumulative-tnr-count, cumulative-cull-count.

- [ ] **Step 1: Open NetLogo and switch to Interface tab**

Open `cat_management_mvp.nlogo` in NetLogo. Switch to the Interface tab.

- [ ] **Step 2: Add plots**

Right-click → Add → Plot. Create three plots:

Plot 1 — "Cat population":
- Pen 1: `count cats with [age >= 6 and status = "intact"]` (yellow)
- Pen 2: `count cats with [age >= 6 and status = "sterilised"]` (blue)
- Pen 3: `count cats with [age < 6]` (orange)
- Pen 4: `count cats` (grey, bold) — total

Plot 2 — "Prey population":
- Pen 1: `count preys` (white on dark BG, or black on light)

Plot 3 — "Immigration rate (monthly)":
- Pen 1: `current-immigration-rate` (green)

- [ ] **Step 3: Add monitors**

Right-click → Add → Monitor. Create one for each of:
- `count cats with [age >= 6 and status = "intact"]` → label "Adult intact"
- `count cats with [age >= 6 and status = "sterilised"]` → label "Adult sterilised"
- `count cats with [age < 6]` → label "Kittens"
- `count preys` → label "Prey"
- `cumulative-prey-deaths` → label "Cumulative prey deaths"
- `prey-years-lost` → label "Prey-years lost"
- `cumulative-tnr-count` → label "Cumulative TNR'd"
- `cumulative-cull-count` → label "Cumulative culled"
- `current-immigration-rate` → label "Current immigration/mo"

- [ ] **Step 4: Visual check**

Click `setup` button; then click `go` button repeatedly (or make `go` a forever button).
Expected: plots update tick-by-tick; monitors show live values.

- [ ] **Step 5: Save and commit**

File → Save. Then:
```bash
git add cat_management_mvp.nlogo
git commit -m "feat: interface plots and monitors for key model metrics"
```

---

## Task 14: Interface widgets (sliders, chooser, buttons)

**Files:**
- Modify: `cat_management_mvp.nlogo` — add interface widgets.

**Interfaces:**
- Consumes: all global variable names.
- Produces: `setup` button, `go` forever button, chooser for `strategy`, sliders for key parameters.

- [ ] **Step 1: Convert existing globals to interface widgets**

In the Interface tab, add:

**Buttons:**
- `setup` button (one-shot)
- `go` button (forever)

**Chooser:**
- `strategy` → values: "tnr", "cull", "hybrid"

**Sliders (replace corresponding globals; NetLogo auto-removes global declarations when a slider owns the name):**
- `initial-cat-population` (0 to 1000, step 50, default 300)
- `initial-prey-population` (0 to 2000, step 50, default 500)
- `cats-processed-per-month` (0 to 50, step 5, default 0)
- `hybrid-tnr-fraction` (0 to 1, step 0.1, default 0.5)
- `base-immigration` (0 to 20, step 1, default 6)
- `food-multiplier` (0.1 to 2.0, step 0.1, default 1.0)
- `food-regen-rate` (0 to 1, step 0.1, default 0.5)
- `p-predation` (0 to 0.5, step 0.01, default 0.1)
- `K-prey` (100 to 2000, step 100, default 500)

**Important:** when you convert a global to a slider, remove its name from the `globals [...]` block in the Code tab AND remove its `set NAME value` line in `setup-globals`. The slider becomes its own source of truth. The other globals (counters, state) remain in the `globals` block as before.

- [ ] **Step 2: Verify tests still pass**

In the Command Center, run each `test-*` procedure in order (test-patch-food-distribution, test-agent-setup, test-cats-move-and-feed, test-regenerate-food, test-immigrate, test-prey-move, test-predate, test-cats-reproduce, test-cats-age-and-die, test-preys-reproduce, test-preys-age-and-die, test-intervene, test-go-runs-without-error). Each should still print PASS.

- [ ] **Step 3: Save and commit**

File → Save. Then:
```bash
git add cat_management_mvp.nlogo
git commit -m "feat: interface widgets - buttons, chooser, sliders"
```

---

## Task 15: Validation run vs the deterministic projection

**Files:**
- Create: `validation_notes.md`

**Interfaces:**
- Consumes: the finished model.
- Produces: a short report comparing one 10-year run per strategy against the Python projection in the scratchpad.

- [ ] **Step 1: Run baseline unmanaged scenario**

In NetLogo:
1. Set `cats-processed-per-month = 0`.
2. Set `strategy = "tnr"` (doesn't matter when effort = 0).
3. Click `setup`, then `go`. Wait for 120 ticks.
4. Record final values: Adult intact, Prey, Prey-years lost, Immigration rate.

Expected (from projection, deterministic approx): adult cats grow to ~340; prey crash to ~20; prey-years-lost ~47,000.

- [ ] **Step 2: Run TNR @ 20/mo**

Set `cats-processed-per-month = 20`, `strategy = "tnr"`. setup + go.
Expected: adult cats decline to ~200; prey ~40; prey-years-lost ~46,000.

- [ ] **Step 3: Run cull @ 20/mo**

Set `strategy = "cull"`. setup + go.
Expected: adult cats → 0 by tick ~24; prey recover toward 200; prey-years-lost ~33,500.

- [ ] **Step 4: Run hybrid @ 20/mo (50/50)**

Set `strategy = "hybrid"`, `hybrid-tnr-fraction = 0.5`. setup + go.
Expected: adult cats ~85; prey ~100; prey-years-lost ~41,500.

- [ ] **Step 5: Record findings in `validation_notes.md`**

Create `validation_notes.md`:

```markdown
# V1 Model Validation — NetLogo vs Deterministic Projection

Date: 2026-10-07

Comparison of one 10-year NetLogo run per strategy vs Python deterministic projection.
Qualitative match expected (ordering of strategies, order-of-magnitude values).

| Strategy | Metric | Projection | NetLogo (1 run) | Match? |
|---|---|---|---|---|
| Unmanaged | Final adult cats | ~344 | [fill in] | |
| Unmanaged | Final prey | ~20 | [fill in] | |
| Unmanaged | Prey-years lost | ~47,700 | [fill in] | |
| TNR @ 20/mo | Final adult cats | ~204 | | |
| TNR @ 20/mo | Final prey | ~40 | | |
| TNR @ 20/mo | Prey-years lost | ~46,400 | | |
| Cull @ 20/mo | Final adult cats | 0 | | |
| Cull @ 20/mo | Final prey | ~190 | | |
| Cull @ 20/mo | Prey-years lost | ~33,500 | | |
| Hybrid @ 20/mo | Final adult cats | ~85 | | |
| Hybrid @ 20/mo | Final prey | ~100 | | |
| Hybrid @ 20/mo | Prey-years lost | ~41,700 | | |

## Required ordering

Prey-years-lost (lower = better for conservation):
cull < hybrid < TNR < unmanaged.

If NetLogo values preserve this ordering, V1 is behaving correctly. If not, debug
the mechanism that violates the ordering before proceeding.

## Issues found and fixes

[fill in as you go]
```

Fill in the actual NetLogo results in each row.

- [ ] **Step 6: Commit**

```bash
git add validation_notes.md cat_management_mvp.nlogo
git commit -m "docs: V1 validation against deterministic projection"
```

---

## Task 16: BehaviorSpace experiments — includes seed-determinism test (Review Focus item 4)

**Files:**
- Modify: `cat_management_mvp.nlogo` — set up BehaviorSpace experiments via Tools → BehaviorSpace.
- Create: `behaviorspace_notes.md`

**Interfaces:**
- Consumes: the finished model with widgets.
- Produces: three BehaviorSpace experiments and documentation on how to run them.

- [ ] **Step 1: Verify seed-determinism (Review Focus 4)**

In the NetLogo Command Center, run:

```
random-seed 42
setup
set cats-processed-per-month 20
set strategy "tnr"
repeat 120 [ go ]
show (word count cats " cats, " count preys " preys, " prey-years-lost " deficit")

;; Repeat with same seed
random-seed 42
setup
set cats-processed-per-month 20
set strategy "tnr"
repeat 120 [ go ]
show (word count cats " cats, " count preys " preys, " prey-years-lost " deficit")
```

Both lines must print identical output. If not, there is a hidden source of non-determinism — fix before proceeding. Likely culprits: `random-float` without seed-controlled sequence, agent order dependency without `n-of`/`shuffle`.

- [ ] **Step 2: Set up Experiment 1 — matched-effort sweep**

In NetLogo: Tools → BehaviorSpace → New.

Name: `Exp1_matched_effort`

Vary variables:
```
["strategy" "tnr" "cull" "hybrid"]
["cats-processed-per-month" 0 5 10 15 20 25 30 35 40]
["hybrid-tnr-fraction" 0.5]
```

Repetitions: 30
Measure runs using: `count cats with [status = "intact" and age >= 6]`, `count cats with [status = "sterilised" and age >= 6]`, `count preys`, `prey-years-lost`, `cumulative-prey-deaths`
Setup commands: `setup`
Go commands: `go`
Time limit: 120 ticks
Stop condition: (blank)

Total runs: 3 × 9 × 30 = 810.

- [ ] **Step 3: Set up Experiment 2 — immigration sensitivity**

Name: `Exp2_immigration_sensitivity`

Vary variables:
```
["strategy" "tnr" "cull" "hybrid"]
["cats-processed-per-month" 0 10 20 30 40]
["base-immigration" 2 6 15]
["hybrid-tnr-fraction" 0.5]
```
Repetitions: 30. Measures same as Exp1. 3 × 5 × 3 × 30 = 1350 runs.

- [ ] **Step 4: Set up Experiment 3 — feeding-ban sensitivity**

Name: `Exp3_feeding_ban`

Vary variables:
```
["strategy" "tnr" "cull" "hybrid"]
["cats-processed-per-month" 0 10 20 30 40]
["food-multiplier" 0.3 0.7 1.0]
["hybrid-tnr-fraction" 0.5]
```
Repetitions: 30. 3 × 5 × 3 × 30 = 1350 runs.

- [ ] **Step 5: Dry-run Experiment 1 at 2 reps to confirm it works**

Edit Exp1_matched_effort → change repetitions to 2 temporarily → Run Experiment → Save CSV. Verify CSV has 3 × 9 × 2 = 54 rows and columns match the Measure spec.

Restore repetitions to 30 (don't actually run 810 yet — that will be a separate exercise after further tuning).

- [ ] **Step 6: Create `behaviorspace_notes.md`**

```markdown
# BehaviorSpace Experiments — V1

## Experiments configured

- `Exp1_matched_effort` — 3 strategies × 9 effort levels × 30 reps = 810 runs
- `Exp2_immigration_sensitivity` — 3 × 5 × 3 × 30 = 1350 runs
- `Exp3_feeding_ban` — 3 × 5 × 3 × 30 = 1350 runs

Total: 3,510 runs. At ~5 seconds per run (120 ticks), ~5 hours wall-clock
on a single thread; faster with `-threads N` on the command line.

## Running headless

To run Experiment 1 from the command line:
```
cd <netlogo-install-dir>
./netlogo-headless.sh \
  --model /Users/tomcheng/.../cat_management_mvp.nlogo \
  --experiment Exp1_matched_effort \
  --table exp1_results.csv \
  --threads 4
```

## Outputs

Each experiment produces a CSV with one row per (parameter combo × repetition × tick).
Primary metric: `prey-years-lost` at tick 120.

## Analysis plan

Load into Python (pandas), group by strategy and effort level, compute median + IQR,
plot three curves per experiment with error bands.
```

- [ ] **Step 7: Commit**

```bash
git add cat_management_mvp.nlogo behaviorspace_notes.md
git commit -m "feat: BehaviorSpace experiments for RQ-A (Exp1, Exp2, Exp3)"
```

---

## Final checks before declaring MVP complete

- [ ] All `test-*` procedures still pass when run manually from Command Center.
- [ ] `validation_notes.md` shows the correct ordering (cull < hybrid < TNR < unmanaged) for prey-years-lost.
- [ ] A single run of 120 ticks completes in < 5 seconds on a typical laptop.
- [ ] All interface widgets (sliders, chooser, buttons, plots, monitors) are present and functional.
- [ ] Three BehaviorSpace experiments are saved in the .nlogo file and verified to produce CSV output in a 2-rep dry run.
- [ ] Code committed to git with meaningful messages.
- [ ] Scratchpad `v1_projection.py` is still available for future recalibration.
