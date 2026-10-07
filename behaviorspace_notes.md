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

## Primary analysis plan

Load the CSV into Python / R / Excel. Group by `(strategy, cats-processed-per-month)`:

- Compute **median** and **interquartile range (IQR)** of `prey-years-lost` across the 30 replicates.
- Plot two curves (one per strategy): x = effort, y = median prey-years-lost, with IQR shaded.
- For the headline answer to RQ-A: compare TNR vs cull at each effort level; non-parametric Mann-Whitney U for significance.

## File naming convention (suggested)

- `exp1_results.csv` — matched-effort comparison
- `exp2_results.csv` — immigration sensitivity
- `exp3_results.csv` — feeding-ban sensitivity

Keep these in a `results/` subdirectory alongside the .nlogo file. Analysis scripts (TBD) go in `analysis/`.
