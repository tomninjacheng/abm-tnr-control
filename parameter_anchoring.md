# Parameter anchoring — Australian context (Option B)

**Primary reference:** Denny EA and Dickman CR (2010) *Review of Cat Ecology and Management Strategies in Australia*. Invasive Animals Cooperative Research Centre, Canberra. ISBN 978-0-9806716-6-7.

This document maps every quantitative parameter in the model to a Denny & Dickman page/number, and flags the parameters that need a secondary source.

---

## 1. Cat demographic parameters

| Model parameter | Value | Denny & Dickman source | Page |
|---|---|---|---|
| Litters per year (per female) | 2 | Jones & Coman 1982a | §3.5, p.17 |
| Mean litter size (prenatal / embryos) | ~4 (range 4.1–4.7) | Jones & Coman 1982a: 4.35±1.27; Brothers 1985: 4.7; Read & Bowen 2001: 4.1±0.3 | §3.6, p.18 |
| Observed juvenile litter size (>1 mo) | 1.9–2.3 (Oberon, Tibooburra) | Denny 2005 | §3.6, p.18 |
| Kitten survival to 6 months, urban feral | 0.16 (= 7/43) | Mirmovitch 1995 (Jerusalem urban) | §3.7, p.18 |
| Kitten survival to 10 months, high-density | 0.095 | Izawa & Ono 1986 | §3.7, p.18 |
| Kitten survival at resource-rich tips | 0.60 | Denny 2005 | §3.7, p.18 |
| Lifespan, free-ranging | survival beyond 3–5 yr "rare"; 1% beyond 7 yr | Warner 1985 | §3.8, p.19 |
| Population doubling time (resource-rich, uncontrolled) | 8.5 months | Short & Turner 2005 (Heirisson Prong) | §3.8, p.19 |
| Sex ratio M:F (adults) | ~1 : 0.73 (slight male bias; approx 1:1) | Brothers 1985; Domm & Messersmith 1990 | §3.4, p.17 |

**Interpretation for our model:**

Urban feral cats in Australia are reasonably characterised as:
- Mean lifespan 3–4 years (free-living); juveniles suffer heavy mortality.
- 2 litters/yr × 4 kittens = ~8 births/female/yr, but only ~16% reach 6 months in urban conditions.
- Net recruitment per female per year = 2 × 4 × 0.16 ≈ **1.3 recruited kittens/female/yr**.

This matches the Set B rates currently in `cat_management_mvp.nlogox`:
- `p-birth = 0.17` (monthly per intact adult female) → 2.04 litters/yr ✓
- `litter-size = 4` ✓ (within 3.88–4.7 range)
- `d-juvenile-cat = 0.25` → (1−0.25)^6 = 0.178 survival to 6 months → **matches Mirmovitch's 0.16**
- `d-adult-cat = 0.025` → mean adult life 40 months = 3.3 years → **matches Warner's "beyond 3–5 yr rare"**

**Verdict: our Set B calibration is already defensible as a Denny & Dickman-anchored Australian urban feral parameterisation.** No major changes to the demographic rates are needed — we just now have the citations to back them up.

---

## 2. Density and spatial scale (§3.1, Table 1, p.13)

| Habitat type | Density (cats/km²) | Source |
|---|---|---|
| Canberra ACT, rubbish-tip sites (highly modified) | 19, 38, 90 | Wilson et al. 1994 |
| Camden NSW, farm (highly modified) | 425 | Hale 2003 |
| Oberon NSW tip | 700–750 | Denny et al. 2002 |
| Hattah-Kulkyne Vic (pastoral, non-urban) | 0.74–2.4 | Jones & Coman 1982a |

**Our model:** 300 cats on a 50×50 grid = 2.5 km × 2.5 km = 6.25 km² → **48 cats/km²**.
This sits in the Wilson et al. (1994) Canberra range (19–90 cats/km²), which is the most directly comparable Australian urban/peri-urban site reported in the review. ✓

---

## 3. Prey species anchor — Superb Fairy-wren (*Malurus cyaneus*)

**Chosen anchor:** Superb Fairy-wren. Rationale: (i) abundant Australian long-term demographic data from the ANU 30-year Canberra dataset and Rowley (1965) foundational life-history study; (ii) actually co-occurs with stray cats in urban Melbourne today (unlike mainland Eastern Barred Bandicoot, now confined to predator-proof fenced sanctuaries); (iii) scores "high" vulnerability under Dickman's (1996) Table 4 (Denny & Dickman p.25): ~10 g body size, terrestrial ground-forager, urban habitat, no defences.

### Life-history parameters

| Model parameter | Anchored value | Primary source |
|---|---|---|
| Clutch size | **3.2** eggs | Rowley 1965, *Emu* 64(4), "Life history of the Superb Blue Wren" (study site: Gungahlin, Canberra) |
| Max broods per year | **3** | Rowley 1965 |
| Max longevity | 10 yr 4 mo | Rowley 1965 |
| Adult annual survival (male) | ~0.70 | Russell & Rowley 1993 (Splendid Fairy-wren congener; closest demographic analogue) |
| Adult annual survival (female) | ~0.59 | Russell & Rowley 1993 |
| Juvenile first-year survival | ~0.31 (range 0.11–0.59) | Russell & Rowley 1993 |
| Normal-year adult winter loss | ~20% | ANU Canberra 30-yr long-term study (Cockburn group) |

**Derived model defaults for simplified parameterisation:**

| Simplified slider | Anchored default | Derivation |
|---|---|---|
| `prey-life-expectancy` (years) | **3.0** | Adult annual survival midpoint 0.65 → mean adult residual lifespan 1 / (1 − 0.65) = 2.86 yr. Rounded to 3. |
| `prey-annual-net-recruitment-per-female` | **2.0** | 3 broods × 3.2 eggs × ~0.55 fledging × ~0.4 post-fledging-to-breeding ≈ 2.1 per pair ≈ 1.0 per adult. Rounded to 2.0 per female (= per breeding female, since model tracks adults rather than pairs). |

### Density → `K-prey`

**Urban territory data (BirdLife Australia; Parsons et al. 2007; CSIRO Emu papers):**
- Male territory: 0.5–2 ha generally
- **Urban mean home range: 1.4 ha (half of bushland's 2.6 ha)**
- Pairs per hectare in good urban habitat: ~0.7

**Scale to model:** 50×50 grid = 2.5 km × 2.5 km = 625 ha total. If ~30–50% of cells are suitable (shrubby/parkland) and the rest are impervious / low-cover / food-desert, suitable area ≈ 190–310 ha × ~1.5 adults/ha ≈ **285–470 adult Fairy-wrens at K**.

**Current `K-prey = 500` is defensible** as the upper bound of this range (reflecting an urban district with reasonably good remnant vegetation). The sensitivity sweep across `food-multiplier` and future K perturbations covers the lower-density case.

### Vulnerability profile (Denny & Dickman Table 4, p.25)

| Attribute | Fairy-wren value | Score |
|---|---|---|
| Size | ~10 g | 3 (birds <200 g) |
| Habitat | Urban/open vegetation | 3 |
| Behaviour: diurnal | diurnal | 0 |
| Behaviour: terrestrial/scansorial | terrestrial ground-forager | 1 |
| Behaviour: no defences | no defences | 1 |
| **Cumulative** | | **5 → "low–high" boundary; interpreted "high"** |

Note: Dickman's scoring puts diurnal birds at 0, but Fairy-wren nests on or near ground are highly accessible to cats regardless. The predation signal in our model operates on *adults* (not nest predation), so this is a conservative assumption.

### Known limitation of the Fairy-wren framing

Cats take Superb Fairy-wrens primarily as nestlings/fledglings rather than as adults (adults are agile fliers). Our model applies predation uniformly to the prey population without distinguishing life stages — this is a V1 simplification that we flag in the handoff and viva limitations list. Field studies (e.g. Catterall 2004) show adult Fairy-wren mortality is more weather/disease-dominated than cat-dominated, while recruitment is strongly cat-sensitive via nest predation. Our `p-predation` therefore represents an *effective* per-prey-individual monthly loss rate attributable to cats, pooling direct adult kills and population-level recruitment suppression.

---

## 4. Parameters NOT fully anchored by primary sources (treated as sensitivity parameters)

| Model parameter | Status | Treatment |
|---|---|---|
| `p-predation` (monthly kill probability per prey when a cat is adjacent) | Partially anchored. Denny & Dickman §4.1-4.4 covers diet composition (frequency of occurrence), not kill rates. Legge et al. 2017 gives ~1067 kills/cat/yr in Australian natural environments; urban-fringe strays lower. Translating per-cat annual kills to per-prey adjacency probability depends on model geometry. | Keep current `p-predation = 0.1` as baseline; **sensitivity sweep ±50%**. Note in viva that the metric cost(20) is a *ratio* comparing TNR vs cull — absolute predation rate affects both strategies similarly and partly cancels. |
| `K-prey` | Anchored (above) at 500 for Fairy-wren urban upper bound. | Keep baseline; sensitivity sweep via `food-multiplier`. |
| `base-immigration` | Qualitatively supported (Denny & Dickman p.19-20: Wilson et al. 1994 "control in perpetuity would be needed to prevent re-establishment"). No numeric rate in Australian literature. | **Primary sensitivity parameter** (Exp2 in BehaviorSpace). Sweep {2, 6, 15}. |
| `food-multiplier` | Design parameter (not a biological rate). | **Primary sensitivity parameter** (Exp3). Sweep {0.3, 0.7, 1.0}. |

---

## 5. Simplified-model proposal (per prior conversation)

The user asked to simplify to just `life-expectancy` + `annual-reproduction-rate` sliders, removing the age / juvenile-adult distinction.

### Mapping to Denny & Dickman anchors

If we collapse to a single-stage ("adult") cat population:

| Simplified slider | Anchored default | Derivation |
|---|---|---|
| `cat-life-expectancy` (years) | **3.0** | Warner 1985: "survival beyond 3 to 5 years is rare" in free-ranging farm cats (p.19). Monthly mortality = 1 / (3×12) = 0.0278. |
| `cat-annual-net-recruitment-per-female` | **1.3** | Mirmovitch 1995 urban feral kitten survival (0.16) × litter size 4 × 2 litters/yr = 1.28. Rounded to 1.3. |
| `prey-life-expectancy` (years) | TBD per species | E.g. Eastern Barred Bandicoot ~3 yr; Fairy-wren ~5 yr. |
| `prey-annual-net-recruitment-per-female` | TBD per species | E.g. Eastern Barred Bandicoot ~4 young/yr (literature); Fairy-wren ~2–4 fledglings/yr. |

### Internal R₀ check
R₀ = recruitment × lifespan = 1.3 × 3 = **3.9 lifetime female→female** (if all recruits are female) — but half are male, so **R₀ ≈ 1.95 per female**.

Annualised: a population of 100 females will become 100 × (1.3/2) + 100 × (1 − 1/3) = 65 + 67 = 132 in year 1 → **~32% annual growth**.

That is substantially faster than our previous target of 20%, but much slower than Short & Turner's doubling-in-8.5-months (which is a special-case resource-rich pulse). ~30%/year is defensible for urban feral populations without controls.

### What we lose by removing age structure
- No kitten-only mortality (absorbed into shortened mean lifespan)
- No "adults only hunt / are trappable" rule — must either apply to all cats, or add a non-age boolean (e.g., `can-hunt?` = true for all)

### Decisions this proposal needs
1. **Confirm anchor prey species.** My recommendation: Eastern Barred Bandicoot (Melbourne, endangered, documented cat impact).
2. **Secondary source for `p-predation`.** My recommendation: anchor to Legge et al. 2017 Australian kill-rate estimates, then convert to monthly adjacency-based probability via our model's spatial scale (treat as approximate — the exact mapping is messy).
3. **Treat `base-immigration`, `K-prey`, `food-multiplier` as sensitivity parameters** rather than trying to anchor them from a single number. Explore via OAT sensitivity ±25% or ±50%.

---

## 6. Sensitivity-analysis plan under anchoring

With anchored values pinned, perform one-at-a-time (OAT) sensitivity on each parameter at ±25% of its anchored value, holding all others at the anchor. Report cost(20) at each perturbed value, plot as a tornado chart.

Priority parameters for sensitivity:
1. `cat-life-expectancy` (±25% → 2.25–3.75 yr) — tests sensitivity to the dominant demographic lever
2. `cat-annual-net-recruitment` (±25% → 1.0–1.6)
3. `p-predation` (±50% range, wider because it's weakest-anchored)
4. `base-immigration` (±50% range, same reason)
5. `K-prey` (±50% range)

Rate the result as:
- "robust" if cost(20) stays within ±30% of baseline across all ±25% perturbations
- "sensitive-but-ordered" if the sign and order (TNR > cull) is preserved
- "fragile" if sign or order flips — in which case flag loudly in discussion

---

## 7. Citations (BibTeX-ready)

```bibtex
@techreport{DennyDickman2010,
  title   = {Review of cat ecology and management strategies in {A}ustralia},
  author  = {Denny, Elizabeth A. and Dickman, Christopher R.},
  institution = {Invasive Animals Cooperative Research Centre},
  address = {Canberra},
  year    = {2010},
  month   = {February},
  isbn    = {978-0-9806716-6-7}
}

@article{Rowley1965,
  title   = {The life history of the Superb Blue Wren, {\em Malurus cyaneus}},
  author  = {Rowley, Ian C. R.},
  journal = {Emu},
  volume  = {64},
  number  = {4},
  pages   = {251--297},
  year    = {1965}
}

@article{RussellRowley1993,
  title   = {Demography of the cooperatively breeding splendid fairy-wren, {\em Malurus splendens} ({M}aluridae)},
  author  = {Russell, Eleanor M. and Rowley, Ian C. R.},
  journal = {Australian Journal of Zoology},
  volume  = {41},
  number  = {5},
  pages   = {475--505},
  year    = {1993}
}

@article{Legge2017,
  title   = {Enumerating a continental-scale threat: {H}ow many feral cats are in {A}ustralia?},
  author  = {Legge, S. and others},
  journal = {Biological Conservation},
  volume  = {206},
  pages   = {293--303},
  year    = {2017}
}

@article{Gunther2022,
  title   = {Reduction in free-roaming cat population after 12 years of a {T}rap-{N}euter-{R}eturn program in {R}ishon {L}eZion, {I}srael},
  author  = {G{\"u}nther, Idit and others},
  journal = {Preventive Veterinary Medicine},
  year    = {2022}
}

@article{McCarthy2013,
  title   = {Estimation of effectiveness of three methods of feral cat population control by use of a simulation model},
  author  = {McCarthy, Robert J. and Levine, Stephen H. and Reed, J. Michael},
  journal = {Journal of the American Veterinary Medical Association},
  volume  = {243},
  number  = {4},
  pages   = {502--511},
  year    = {2013}
}
```
