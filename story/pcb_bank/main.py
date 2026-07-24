"""PCB Bank CVM client — production run against the real parquet export.

Loads v_pcb_cvm_client.parquet, layers the Power BI TMDL-derived measures/
dimensions on top via Dataset.read_schema() (see etc/pbimodel_2_dataset.py
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
from src.report.combine import vstack_images  # noqa: E402

DATA_DIR = HERE / "data"
OUTPUT_DIR = HERE / "output"
F_COMBINE_OUTPUT = False

def main(combine_output: bool = False) -> None:
    """Render every registered chart. If combine_output is True, also vertically
    stack all rendered PNGs (in registration order) into one review image at
    output/_combined_review.png."""
    ds = Dataset(
        DATA_DIR / "v_pcb_cvm_client.parquet",
        cache_path=DATA_DIR / ".cache" / "v_pcb_cvm_client.duckdb",
    )
    # extra_columns: raw dims queried directly by plot/*.py (dim=/legend=/
    # facet_dim=) that aren't declared in model_definition.json itself — add
    # a new entry here whenever a chart starts querying another one.
    ds.read_schema(
        DATA_DIR / "model_definition.json",
        prune=True,
        extra_columns=(
            "HAPPY_SAVINESS_GR",
            "PCB_XS_LENDER_GR",
            "HCVN_ACT_PROD_GR",
            "SCOR_FST_BOD0_CHANNEL",
            "F_ACT_PCB_XS",
            "APPL_CLX_APL_CHANNEL",
            "STAGE_F_PRIME_DIGITAL_BOP",
            "PCB_ACT_PROD_GR",
            "HIST_PROD_GR",
            'HIST_PROD_XS_GR',
            "PCB_ACT_CASH_BANK_MAX_TICKET_GR",
            "PCB_ACT_CASH_FI_MAX_TICKET_GR",
            "PCB_ACT_CASH_BANK_MAX_TENOR_GR",
            "PCB_ACT_CASH_FI_MAX_TENOR_GR",
        ),
    )

    rendered_paths = []
    for topic, funcs in get_registered_plots().items():
        topic_dir = OUTPUT_DIR / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        for name, func in funcs.items():
            fig = func(ds)
            out_path = topic_dir / f"{name}.png"
            fig.savefig(out_path, dpi=500,bbox_inches='tight')
            plt.close(fig)
            rendered_paths.append(out_path)
            print(f"Wrote {out_path}")

    if combine_output:
        combined_path = OUTPUT_DIR / "_combined_review.png"
        vstack_images(rendered_paths, combined_path)
        print(f"Wrote {combined_path}")


if __name__ == "__main__":
    main(F_COMBINE_OUTPUT)
