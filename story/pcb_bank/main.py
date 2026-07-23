"""PCB Bank CVM client — production run against the real parquet export.

Loads v_pcb_cvm_client.parquet, layers the Power BI TMDL-derived measures/
dimensions on top via Dataset.load_schema() (see etc/pbimodel_2_dataset.py
for how model_definition.json is generated), then renders every chart
registered under plot/ (one file per topic, e.g. plot/client.py) to
output/<topic>/<function_name>.png.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt

import plot  # noqa: E402 — runs @register_plot decorators, see plot/__init__.py
from plot.base import get_registered_plots  # noqa: E402
from src.dataset import Dataset  # noqa: E402

DATA_DIR = HERE / "data"
OUTPUT_DIR = HERE / "output"


def main() -> None:
    ds = Dataset(DATA_DIR / "v_pcb_cvm_client.parquet")
    ds.load_schema(DATA_DIR / "model_definition.json")

    for topic, funcs in get_registered_plots().items():
        topic_dir = OUTPUT_DIR / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        for name, func in funcs.items():
            fig = func(ds)
            out_path = topic_dir / f"{name}.png"
            fig.savefig(out_path, dpi=200)
            plt.close(fig)
            print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
