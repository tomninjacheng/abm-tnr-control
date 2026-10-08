# BehaviorSpace Experiments — V1

## Experiments configured in `cat_management_mvp.nlogo`

Open in NetLogo: Tools → BehaviorSpace. You should see three experiments pre-configured:

### Exp1_matched_effort (primary — answers RQ-A)

- `strategy` ∈ {tnr, cull}
- `cats-processed-per-month` ∈ {0, 5, 10, 15, 20, 25, 30, 35, 40}
- All other parameters at defaults
- Repetitions: 30
- Time limit: 120 ticks

Total runs: 2 × 9 × 30 = **540 runs**.

### Exp2_immigration_sensitivity

- `strategy` ∈ {tnr, cull}
- `cats-processed-per-month` ∈ {0, 10, 20, 30, 40}
- `base-immigration` ∈ {2, 6, 15}
- Repetitions: 30

Total: 2 × 5 × 3 × 30 = **900 runs**.

### Exp3_feeding_ban

- `strategy` ∈ {tnr, cull}
- `cats-processed-per-month` ∈ {0, 10, 20, 30, 40}
- `food-multiplier` ∈ {0.3, 0.7, 1.0}
- Repetitions: 30

Total: 2 × 5 × 3 × 30 = **900 runs**.

**Grand total: 2,340 runs.** At ~2-5 seconds per 120-tick run, expect 1-3 hours of wall-clock single-threaded; faster with headless multi-threading.

## How to run from the GUI (one experiment at a time)

1. Open `cat_management_mvp.nlogo` in NetLogo.
2. Tools → BehaviorSpace → select experiment → Run.
3. In the dialog that appears:
   - **Spreadsheet output:** check this box; it writes one row per run with final values.
   - **Table output:** optional — writes one row per tick per run (large files; useful for trajectory analysis).
   - **Parallel runs:** set to number of CPU cores (e.g. 8) to multithread.
4. Choose output filename. The CSV lands wherever NetLogo prompts.

## How to run from the command line (headless, recommended for long runs)

```bash
cd <netlogo-install-dir>    # path to NetLogo application bundle
./netlogo-headless.sh \
  --model /Users/tomcheng/Master/unimelb/S2/computational-modelling/ass2/cat_management_mvp.nlogo \
  --experiment Exp1_matched_effort \
  --spreadsheet exp1_results.csv \
  --threads 8
```

On macOS the headless script usually lives at:
`/Applications/NetLogo 6.3.0/netlogo-headless.sh`

## Dry-run first

Before committing to the full 3,510 runs, do a 2-rep dry run on Experiment 1:

1. In BehaviorSpace, duplicate `Exp1_matched_effort` and name it `Exp1_dryrun`.
2. In the duplicate, change repetitions from 30 to 2.
3. Run it. Should take ~5-10 minutes.
4. Verify the CSV has 2 × 9 × 2 = 36 rows and all metric columns are populated.

Only once the dry run looks right should you launch the full Exp1 (and then Exp2, Exp3).

## Seed-determinism check (do this BEFORE Exp 1 full run)

In the NetLogo Command Center, run twice:

```
random-seed 42
set strategy "tnr"
set cats-processed-per-month 20
setup
repeat 120 [ go ]
show (word count cats " cats, " count preys " preys, " prey-years-lost " deficit")
```

Both runs must produce bit-identical output. If not, there's a hidden source of non-determinism (unlikely with the current code, but worth confirming before running 810 replicates).

## Primary analysis plan — TNR effort multiplier

The headline finding is a single multiplier that quantifies "how much extra effort TNR needs to match culling's wildlife outcome."

**Reference effort is 20 cats/month = 80% annual coverage of initial population**, which matches Gunther et al. (2022)'s field benchmark. See ODD §1 Purpose for the full literature anchoring. McCarthy et al. (2013)'s 57% annual-capture minimum maps to 15 cats/month at our density.

**Procedure (post-hoc on Exp1 CSV):**

1. Reference target: `T = median(cumulative-prey-deaths | strategy=cull, effort=20, over 30 reps)`.
2. TNR trajectory: for each `N ∈ {5, 10, 15, 20, 25, 30, 35, 40}`, compute `K_N = median(cumulative-prey-deaths | strategy=tnr, effort=N)`.
3. Multiplier `M = N* / 20` where `N*` is the smallest `N` with `K_N ≤ T`.
4. Report `M`, or "no N* in sweep range" if TNR never catches up.

**Secondary analyses:**

- Plot two curves (TNR, cull): x = effort, y = median cumulative-prey-deaths, with IQR shaded. Visualise where the curves cross or whether TNR ever reaches culling's floor.
- Same plot for `prey-years-lost` as a sanity check (same ordering expected).
- Report median and IQR for cumulative-prey-deaths at each (strategy, effort) point.
- Non-parametric Mann-Whitney U at each effort level for formal TNR-vs-cull significance.

**Sensitivity across experiments:**

- Repeat the multiplier derivation separately for each `base_immigration ∈ {2, 6, 15}` level in Exp2.
- Repeat for each `food_multiplier ∈ {0.3, 0.7, 1.0}` in Exp3.
- Report the multiplier as a function of (base_immigration, food_multiplier) — this is the headline sensitivity story.

**Expected scaling patterns to look for:**

- Multiplier *shrinks* as `base_immigration` rises: culling's benefit is offset by immigrants, so TNR looks relatively more competitive.
- Multiplier *rises* as `food_multiplier` falls: fewer total cats mean each cat removal matters more, widening culling's lead.

If these patterns hold, the sensitivity story is coherent and defensible. If they're reversed, that's a signal to re-examine the mechanism (likely food-driven immigration not firing strongly enough).

## File naming convention (suggested)

- `exp1_results.csv` — matched-effort comparison
- `exp2_results.csv` — immigration sensitivity
- `exp3_results.csv` — feeding-ban sensitivity

Keep these in a `results/` subdirectory alongside the .nlogo file. Analysis scripts (TBD) go in `analysis/`.
