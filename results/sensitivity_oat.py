"""
One-at-a-time (OAT) sensitivity analysis for the V1 cat-management ABM.

Perturbs each parameter around its anchored baseline value and records the
headline metric: cost(20) = (prey_kills_TNR − prey_kills_cull) / cats_culled
at matched effort N=20 cats/month over 10 years.

Produces:
  - CSV table of baseline + perturbed cost(20) values
  - Tornado chart PNG showing which parameters drive the metric most strongly

NOTE: This is the DETERMINISTIC non-spatial projection, not the NetLogo
spatial ABM. Use it as a quick-look sensitivity scan to prioritise which
parameters warrant full NetLogo BehaviorSpace sweeps. Directional and
rank-order conclusions should transfer to the spatial model; absolute
magnitudes will differ due to spatial clustering.
"""

import csv
import json
import os
from dataclasses import dataclass, field, replace

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Params:
    # ---- Cat demographics (Denny & Dickman 2010 anchored) ----
    p_birth: float = 0.17            # Jones & Coman 1982a: 2 litters/yr (p.17)
    litter: int = 4                  # Prenatal 4.1-4.7 (D&D p.18)
    d_juv_cat: float = 0.25          # Mirmovitch 1995: 16% urban survival to 6mo (p.18)
    d_adult_cat: float = 0.025       # Warner 1985: 3-5 yr lifespan (p.19)

    # ---- Prey demographics (Superb Fairy-wren anchored) ----
    p_prey_birth: float = 0.25       # Rowley 1965: ~3 broods/yr × 3.2 eggs
    prey_litter: int = 2
    d_prey_juv: float = 0.30
    d_prey_adult: float = 0.05       # Russell & Rowley 1993: adult surv 0.59-0.70
    K_prey: float = 500              # Parsons 2007 urban territory → 325-470 at K

    # ---- Food / immigration ----
    base_imm: float = 10
    food_cap_total: float = 1225
    food_cons: float = 1.0
    regen: float = 0.5

    # ---- Predation ----
    p_predation: float = 0.1


def prey_exposure(N_adult_cat):
    return N_adult_cat / (N_adult_cat + 500) if N_adult_cat > 0 else 0.0


def run(p: Params, strategy='none', processed=0, months=120):
    """Run one deterministic 120-month projection. Returns cumulative kills
    and cumulative culls."""
    cat_juv = [0.0] * 6
    cat_adult_intact = 300.0
    cat_adult_steri = 0.0
    prey_juv = [0.0] * 2
    prey_adult = 500.0
    food = p.food_cap_total

    cum_kills = 0.0
    cum_culled = 0.0

    for t in range(months):
        total_cats = sum(cat_juv) + cat_adult_intact + cat_adult_steri
        food = max(0.0, food - p.food_cons * total_cats)
        imm_rate = p.base_imm * (food / p.food_cap_total)
        cat_adult_intact += imm_rate
        food = min(p.food_cap_total, food + p.regen * p.food_cap_total)

        intact_adult_females = cat_adult_intact * 0.5
        new_kittens = intact_adult_females * p.p_birth * p.litter

        exposure = prey_exposure(cat_adult_intact + cat_adult_steri)
        prey_total = sum(prey_juv) + prey_adult
        kills = prey_total * exposure * p.p_predation
        if prey_total > 0:
            kill_frac = kills / prey_total
            for i in range(len(prey_juv)):
                prey_juv[i] *= (1 - kill_frac)
            prey_adult *= (1 - kill_frac)
        cum_kills += kills

        new_juv = [new_kittens * (1 - p.d_juv_cat)]
        for k in range(5):
            new_juv.append(cat_juv[k] * (1 - p.d_juv_cat))
        promoted = cat_juv[5] * (1 - p.d_juv_cat)
        cat_adult_intact += promoted
        cat_juv = new_juv
        cat_adult_intact *= (1 - p.d_adult_cat)
        cat_adult_steri *= (1 - p.d_adult_cat)

        new_prey_juv = []
        prey_adult_f = prey_adult * 0.5
        reduction = max(0, 1 - (sum(prey_juv) + prey_adult) / p.K_prey)
        new_prey = prey_adult_f * p.p_prey_birth * reduction * p.prey_litter
        new_prey_juv.append(new_prey * (1 - p.d_prey_juv))
        new_prey_juv.append(prey_juv[0] * (1 - p.d_prey_juv))
        prey_adult += prey_juv[1] * (1 - p.d_prey_juv)
        prey_juv = new_prey_juv
        prey_adult *= (1 - p.d_prey_adult)

        # No burn-in: intervention runs every tick from month 0.
        if strategy != 'none' and processed > 0:
            take = min(processed, cat_adult_intact)
            if strategy == 'tnr':
                cat_adult_intact -= take
                cat_adult_steri += take
            elif strategy == 'cull':
                cat_adult_intact -= take
                cum_culled += take

    return cum_kills, cum_culled


def cost20(p: Params):
    """Compute the headline exchange-rate metric at N=20 cats/month."""
    kills_tnr, _ = run(p, 'tnr', 20)
    kills_cull, culled = run(p, 'cull', 20)
    if culled <= 0:
        return float('nan')
    return (kills_tnr - kills_cull) / culled


# ---- Baseline ----
baseline = Params()
c_base = cost20(baseline)
print(f"\nBaseline cost(20) = {c_base:.4f} prey saved per cat culled\n")

# ---- OAT perturbations ----
# Format: (parameter_name, low_multiplier, high_multiplier, anchor_label)
PERTURBATIONS = [
    # Well-anchored cat demographics (D&D 2010): ±25%
    ('p_birth',       0.75, 1.25, 'Jones & Coman 1982a'),
    ('litter',        0.75, 1.25, 'Deag 2000; D&D p.18'),
    ('d_juv_cat',     0.75, 1.25, 'Mirmovitch 1995 D&D p.18'),
    ('d_adult_cat',   0.75, 1.25, 'Warner 1985; D&D p.19'),
    # Fairy-wren prey demographics (Rowley 1965 / Russell & Rowley 1993): ±25%
    ('p_prey_birth',  0.75, 1.25, 'Rowley 1965'),
    ('d_prey_adult',  0.75, 1.25, 'Russell & Rowley 1993'),
    ('K_prey',        0.75, 1.25, 'Parsons 2007 urban Fairy-wren'),
    # Weakly-anchored structural parameters: ±50%
    ('p_predation',   0.5,  1.5,  'free; sensitivity-tested'),
    ('base_imm',      0.5,  1.5,  'Wilson 1994 qualitative'),
    ('food_cap_total', 0.5, 1.5,  'design parameter'),
]

results = []
for name, low_mult, high_mult, anchor in PERTURBATIONS:
    base_val = getattr(baseline, name)
    low_val = type(base_val)(base_val * low_mult)
    high_val = type(base_val)(base_val * high_mult)

    p_low = replace(baseline, **{name: low_val})
    p_high = replace(baseline, **{name: high_val})

    c_low = cost20(p_low)
    c_high = cost20(p_high)

    delta_low = c_low - c_base
    delta_high = c_high - c_base
    span = max(abs(delta_low), abs(delta_high))

    results.append({
        'parameter': name,
        'anchor': anchor,
        'baseline_value': base_val,
        'low_value': low_val,
        'high_value': high_val,
        'low_mult': low_mult,
        'high_mult': high_mult,
        'cost_baseline': round(c_base, 4),
        'cost_low':  round(c_low,  4),
        'cost_high': round(c_high, 4),
        'delta_low':  round(delta_low,  4),
        'delta_high': round(delta_high, 4),
        'abs_span':   round(span,       4),
    })

results.sort(key=lambda r: r['abs_span'], reverse=True)

# ---- Print table ----
hdr = ('parameter', 'base', 'low', 'high', 'cost_lo', 'cost_hi', 'd_lo', 'd_hi', 'span')
widths = (16, 10, 10, 10, 9, 9, 9, 9, 9)
line = ''.join(f'{h:<{w}}' for h, w in zip(hdr, widths))
print(line)
print('-' * len(line))
for r in results:
    row = (
        r['parameter'],
        f"{r['baseline_value']:g}",
        f"{r['low_value']:g}",
        f"{r['high_value']:g}",
        f"{r['cost_low']:.3f}",
        f"{r['cost_high']:.3f}",
        f"{r['delta_low']:+.3f}",
        f"{r['delta_high']:+.3f}",
        f"{r['abs_span']:.3f}",
    )
    print(''.join(f'{c:<{w}}' for c, w in zip(row, widths)))

# ---- Write CSV ----
csv_path = os.path.join(OUT_DIR, 'sensitivity_oat_results.csv')
with open(csv_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)
print(f"\nCSV written: {csv_path}")

# ---- JSON for later tornado-chart generation ----
json_path = os.path.join(OUT_DIR, 'sensitivity_oat_results.json')
with open(json_path, 'w') as f:
    json.dump({
        'baseline_cost20': c_base,
        'perturbations': results,
    }, f, indent=2)
print(f"JSON written: {json_path}")

# ---- Try matplotlib tornado chart ----
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception as e:
    print(f"\nmatplotlib not available ({e}); tornado chart skipped.")
    raise SystemExit(0)

# Sort by abs_span (largest at top)
results_for_plot = sorted(results, key=lambda r: r['abs_span'], reverse=True)

fig, ax = plt.subplots(figsize=(10, 6))
y = list(range(len(results_for_plot)))
labels = [r['parameter'] for r in results_for_plot]

for i, r in enumerate(results_for_plot):
    # Horizontal bar from min(delta) to max(delta)
    lo = min(r['delta_low'], r['delta_high'])
    hi = max(r['delta_low'], r['delta_high'])
    # Low-perturbation side
    if r['delta_low'] < 0:
        ax.barh(i, r['delta_low'], color='#d64545', edgecolor='k', alpha=0.85,
                height=0.6, label='−% perturbation' if i == 0 else None)
    else:
        ax.barh(i, r['delta_low'], color='#d64545', edgecolor='k', alpha=0.85,
                height=0.6, label='−% perturbation' if i == 0 else None)
    if r['delta_high'] < 0:
        ax.barh(i, r['delta_high'], color='#4a90d9', edgecolor='k', alpha=0.85,
                height=0.6, label='+% perturbation' if i == 0 else None)
    else:
        ax.barh(i, r['delta_high'], color='#4a90d9', edgecolor='k', alpha=0.85,
                height=0.6, label='+% perturbation' if i == 0 else None)

ax.axvline(0, color='k', linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()  # largest span at top
ax.set_xlabel(f'Δ cost(20) [prey/cat spared], baseline = {c_base:.3f}')
ax.set_title('OAT sensitivity of wildlife-cost-per-cat-spared\n'
             '(deterministic non-spatial projection; ±25% / ±50% perturbations)')
ax.legend(loc='lower right')
ax.grid(axis='x', alpha=0.3)
fig.tight_layout()

png_path = os.path.join(OUT_DIR, 'sensitivity_tornado.png')
fig.savefig(png_path, dpi=140)
print(f"Tornado PNG: {png_path}")
