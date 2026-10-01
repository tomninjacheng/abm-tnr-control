# Proposal Feedback and Next Steps

> Internal collaboration document. This is not final report prose. The research question, modelling decisions, code, and submitted writing must be confirmed and authored by the two team members.

**Last updated:** 1 October 2026  
**Team:** Tom Cheng and Liu Qisheng  
**Demonstration / individual viva:** 14 October 2026  
**Final report due:** 25 October 2026, 23:59

## 1. Teaching-team feedback

The teaching team considered the topic a good idea and suitable for an agent-based model. The proposal was also described as well structured. The main improvements requested were:

1. **Narrow the research question.**
   - The first half of the submitted question is somewhat predictable: if cats cause prey deaths, reducing the number of cats will almost certainly reduce prey mortality.
   - A more informative focus would be the rate, timing, or rebound pattern of prey-mortality reduction under culling versus TNR.

2. **Use one core research question rather than two.**
   - The proposal currently asks both which strategy performs better and what minimum intervention threshold is required.
   - Treating both as core questions expands the model and experimental scope.

3. **Simplify the first model iteration.**
   - The current design includes too many processes, variables, and behaviours.
   - Catchability classes were explicitly identified as something that could be abstracted away.
   - Multiple mortality mechanisms, including hunger/health, age-related mortality, and culling, could also be simplified.
   - Multiple processes are acceptable only when they directly support the model purpose and research question.

4. **Control the final word count.**
   - The proposal exceeded the 1,200-word limit.
   - The final report must remain within 3,000 words.

## 2. Draft single research-question direction

For team discussion only:

> At matched monthly intervention effort, how does food-driven immigration affect the rate at which culling and TNR reduce prey mortality?

This wording is a planning suggestion, not final submission text. Both team members must agree on and rewrite the final question.

Recommended primary outcome:

- months required for monthly prey deaths to fall to 50% of the pre-intervention average;
- record a run as "not achieved" when the threshold is never reached;
- use cat abundance, intact proportion, and immigrant count only as mechanism-explanation outputs.

The minimum intervention threshold should not remain a second core research question. Intervention effort may be examined later as a sensitivity analysis.

## 3. Recommended minimum model (v1)

### Retain

- cats and one representative prey population as individual agents;
- a spatial grid and food distribution;
- intact / sterilised cat status;
- TNR, culling, and a no-intervention baseline;
- food-driven immigration;
- simple reproduction;
- one background natural-mortality probability per species;
- local predation;
- matched monthly intervention effort;
- time-series recording and stochastic replicates.

### Remove or postpone

- easy / moderate / hard catchability classes;
- hybrid management;
- hunger and health states;
- juvenile, elderly, and starvation mortality mechanisms;
- pregnancy and nursing states;
- management cost;
- territorial competition;
- trap learning;
- adaptive or high-density targeting;
- vacancy-driven immigration;
- food-control policy;
- multiple parallel research questions and experiment families.

## 4. Decisions required before coding

- [ ] Agree on one final research question.
- [ ] Agree on one primary outcome.
- [ ] Freeze the mechanisms retained in v1.
- [ ] Define process order within each tick.
- [ ] Define baseline parameters and simulation duration.
- [ ] Allocate implementation, validation, and experiment responsibilities.
- [ ] Confirm that both members can explain every core mechanism.

## 5. Ordered action plan

### 1 October

1. Review the teaching-team feedback together.
2. Agree on the single research question.
3. Freeze the minimum v1 boundary.
4. Confirm Git workflow and responsibilities.
5. Begin maintaining the contribution and decision log.

### 2-4 October: runnable NetLogo v1

1. Set up the grid, food, cats, and prey.
2. Implement simple movement.
3. Implement simple reproduction and background mortality.
4. Implement local predation.
5. Implement food-driven immigration.
6. Implement TNR, culling, and no-intervention modes.
7. Add the required monitors, plots, and data recording.
8. Confirm that the model runs for 120 ticks without errors.

### 5-7 October: mechanism validation

Test each core mechanism independently. Save parameters, seeds, screenshots, and short conclusions.

### 8-10 October: pilot experiments

Run a small TNR/culling x low/medium/high immigration pilot at matched effort. Confirm that the outputs can answer the research question before committing to full experiments.

### 11-13 October: demonstration and viva preparation

Freeze a stable demonstration configuration. Both members must practise running the model, explaining the code, changing parameters, defending assumptions, and describing their personal contributions.

### 14 October: demonstration and individual viva

Record all teaching-team comments immediately after the session.

### 15-20 October: full experiments

Freeze the code, run the planned replicates, and conduct only one high-priority sensitivity analysis.

### 20-24 October: final report and submission checks

Rewrite the ODD and Methods from the implemented model, present only results that answer the core question, remain within 3,000 words, and verify DOI links, figures, AI declaration, report formatting, and code submission requirements.

## 6. Repository status

As of 1 October 2026:

- Tom confirmed that there is no unpushed local code.
- The repository contained only the 16 September initial commit.
- No NetLogo model, experiment configuration, or results existed.
- Implementation should therefore be treated as not yet started.
