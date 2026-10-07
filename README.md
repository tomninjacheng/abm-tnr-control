# Agent-Based Model of TNR and Culling

COMP90083 Computational Modelling & Simulation — Assignment 2
Team: Tom Cheng (1923353) and Liu Qisheng (1835745)

Agent-based model comparing stray-cat management strategies — **trap-neuter-return (TNR)** vs **culling** — by their effect on a co-occurring native prey species over 10 years. Implemented in NetLogo 7.0.4.

> **Research question:** At equal monthly intervention effort (cats processed per month), which strategy — TNR or culling — produces the lowest cumulative *prey-years lost* compared to a no-cat baseline, over a 10-year horizon?

## Project status

**V1 MVP built and committed (7 October 2026).** Awaiting interactive validation in NetLogo against the pre-implementation deterministic projection, then full BehaviorSpace experiment runs.

Key dates:
- Demonstration and individual viva: **14 October 2026**
- Final report due: **25 October 2026, 23:59**

## Why this matters

Every existing simulation model of stray-cat management (McCarthy et al., 2013; Boone et al., 2019; Ireland & Neilan, 2016; Belsare & Vanak, 2020) measures success purely in terms of **predator population numbers**. None include a prey species. The core conservation objection to TNR is that sterilised cats continue to hunt wildlife for years after their reproductive capacity is removed — but whether TNR's slower population decline results in more or fewer cumulative wildlife deaths than culling's faster-but-immigration-vulnerable approach has never been quantified. This model is the first to do so.

## Running the model

1. Install [NetLogo 6.4+ or 7.x](https://ccl.northwestern.edu/netlogo/).
2. Open `cat_management_mvp.nlogox` in NetLogo.
3. Click **setup**, then **go**.
4. Default scenario: unmanaged (no intervention). Change the `strategy` chooser and raise `cats-processed-per-month` above 0 to test TNR or culling.

### Test suite

In the NetLogo Command Center:

```
run-all-tests
```

Expected: 13 `PASS: ...` lines.

### BehaviorSpace experiments

See `behaviorspace_notes.md` for Experiment 1 (matched-effort comparison), Experiment 2 (immigration sensitivity), and Experiment 3 (feeding-ban sensitivity).

## What's in this repo

| File | What it is |
|---|---|
| `cat_management_mvp.nlogox` | The NetLogo model (V1) |
| `ODD_protocol_final.md` | Formal ODD-protocol specification (Grimm et al. 2010) |
| `draft_handoff_final.md` | Design-decision handoff with full rationale |
| `validation_notes.md` | Validation checklist against the deterministic projection |
| `behaviorspace_notes.md` | How to run the three BehaviorSpace experiments |
| `docs/implementation-plan.md` | Phased NetLogo implementation plan with TDD steps |

### Internal collaboration documents

- [Proposal feedback and next steps](./PROPOSAL_FEEDBACK_AND_NEXT_STEPS.md)
- [Contribution and decision log](./CONTRIBUTION_LOG.md)

These are internal planning records rather than final-report prose. The team confirms all modelling decisions, writes the submitted report in their own words, and maintains an accurate AI-use declaration.

## V1 scope and simplifications

V1 is deliberately scoped tightly around the one research question. Mechanisms considered but deferred as future extensions:

- Catchability heterogeneity (trap-shy cats)
- Hybrid strategy (mixed TNR + culling)
- Food-driven cat mortality
- Breeding seasonality
- Density-dependent mating (Allee effect)
- Pregnancy / gestation state
- Prey habitat flag
- Spatial targeting of intervention

Each is documented in the handoff and ODD with its rationale. See `draft_handoff_final.md` §5 for the full future-extensions table.

## Key design choices

- **Prey-years lost** (integrated deficit vs no-cat baseline) is the primary outcome, chosen because cumulative-kills alone is non-monotone in harm (a strategy that drives prey extinct records fewer kills than one that lets prey rebound).
- **Food-driven immigration** operationalises the empirical "vacuum-effect" pattern: living cats (intact or sterilised) suppress immigration via food consumption; absent cats raise it. This is a mechanistically transparent alternative to the contested territorial-vacancy mechanism.
- **High juvenile mortality** absorbs density-dependent processes (disease, intraspecific pressure) that we don't explicitly model, keeping fecundity at literature-consistent values.
- **Sterilised cats hunt at intact rate by default** — the conservative assumption for TNR per Longcore et al. (2009). If sterilisation reduces hunting in reality, TNR's wildlife-impact advantage would be *larger* than this model reports.

## License

TBD.
