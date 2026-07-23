"""Small multiples demo: facet by dimensionA into a 2x3 grid, sharing one
y-axis across all facets. Each ax renders 2 measures as lines against
dimensionB. Mock data only — generated in-memory, no external files."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

from src.dataset import Dataset, Measure
from src.vizzy import Vizzy

DIM_A_VALS = [f"Segment {i}" for i in range(1, 7)]  # facet -> 2x3 grid
DIM_B_VALS = [f"Q{i}" for i in range(1, 5)]  # x-axis within each ax

rng = np.random.default_rng(42)
rows = []
for a in DIM_A_VALS:
    base = rng.uniform(50, 150)
    for b in DIM_B_VALS:
        rows.append({
            "dimensionA": a,
            "dimensionB": b,
            "measure_1": float(base + rng.normal(0, 10)),
            "measure_2": float(base * 0.6 + rng.normal(0, 8)),
        })

df = pl.DataFrame(rows)
data_path = Path(__file__).resolve().parent / "data" / "small_multiples_mock.parquet"
df.write_parquet(data_path)

ds = Dataset(data_path)
ds.set_measures([
    Measure("measure_1", "sum(measure_1)"),
    Measure("measure_2", "sum(measure_2)"),
])

# Pre-query every facet once to find one shared y-range before plotting.
facet_results = {
    a: ds.query(dim="dimensionB", measure="measure_1", filters=f"dimensionA = '{a}'").values.value
    for a in DIM_A_VALS
} | {
    (a, "m2"): ds.query(dim="dimensionB", measure="measure_2", filters=f"dimensionA = '{a}'").values.value
    for a in DIM_A_VALS
}
all_vals = np.concatenate(list(facet_results.values()))
shared_ylim = (float(all_vals.min()), float(all_vals.max()))

fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)

for a, ax in zip(DIM_A_VALS, axes.flat):
    line = Vizzy(fig, ax, ds).line(
        dim="dimensionB",
        measure=["measure_1", "measure_2"],
        filters=f"dimensionA = '{a}'",
    )
    line.set_theme()
    line.set_mes_scale(ylim=shared_ylim)
    ax.set_title(a, fontsize=10)

fig.tight_layout()
out_path = Path(__file__).resolve().parent / "small_multiples.png"
fig.savefig(out_path, dpi=150)
print(f"Wrote {out_path}")
