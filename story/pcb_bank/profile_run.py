"""Timing breakdown for main.py's pipeline — which step actually takes long.

Plain script (like tests/gallery/*.py), not imported by anything, not
pytest-collected. Wraps Dataset._materialize/query on the *instance* only
(no changes to src/dataset.py needed) to time each call individually, then
prints a ranked report so a slow run doesn't need re-profiling by hand.

Does NOT write into output/ by default (keeps git status clean) — pass
--with-save to also time fig.savefig(), writing PNGs to a throwaway tempdir
instead of story/pcb_bank/output/.

Run: python story/pcb_bank/profile_run.py [--with-save]
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

_import_start = time.perf_counter()
import matplotlib.pyplot as plt

import plot  # noqa: E402 — runs @register_plot decorators, see plot/__init__.py
from plot.base import get_registered_plots  # noqa: E402
from src.dataset import Dataset  # noqa: E402
_import_seconds = time.perf_counter() - _import_start

DATA_DIR = HERE / "data"

WITH_SAVE = "--with-save" in sys.argv


def _timed(fn, label_fn):
    """Wrap a bound method so every call records (label, seconds) into `spans`.
    label_fn is evaluated BEFORE fn runs — needed for query()'s cache-hit
    label, since the in-process cache gets populated as a side effect of the
    very call being timed, so checking after would always read "hit"."""
    def wrapper(*args, **kwargs):
        label = label_fn(*args, **kwargs)
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        spans.append((label, time.perf_counter() - start))
        return result
    return wrapper


spans: list[tuple[str, float]] = []


def main() -> None:
    spans.append(("import (matplotlib, plot, src.dataset)", _import_seconds))

    t0 = time.perf_counter()
    ds = Dataset(
        DATA_DIR / "v_pcb_cvm_client.parquet",
        cache_path=DATA_DIR / ".cache" / "v_pcb_cvm_client.duckdb",
    )
    spans.append(("Dataset() init", time.perf_counter() - t0))

    # Wrap the instance's methods, not the class — zero risk to src/dataset.py,
    # and this only affects this one Dataset object for this one script run.
    original_materialize = ds._materialize
    ds._materialize = _timed(original_materialize, lambda: "_materialize()")

    original_query = ds.query
    query_cache_ref = ds._query_cache

    def _query_label(dim, measure, legend=None, filters=None, sort_by=None):
        key = (dim, measure, legend, filters, tuple((sort_by or {"dim": "asc"}).items()))
        hit = key in query_cache_ref
        return f"query(dim={dim}, measure={measure}, legend={legend}) [{'cache hit' if hit else 'new'}]"

    ds.query = _timed(original_query, _query_label)

    t0 = time.perf_counter()
    ds.read_schema(
        DATA_DIR / "model_definition.json",
        prune=True,
        extra_columns=("HAPPY_SAVINESS_GR", "PCB_XS_LENDER_GR", "HCVN_ACT_PROD_GR"),
    )
    spans.append(("read_schema()", time.perf_counter() - t0))

    save_dir = Path(tempfile.mkdtemp(prefix="pcb_bank_profile_")) if WITH_SAVE else None

    for topic, funcs in get_registered_plots().items():
        for name, func in funcs.items():
            t0 = time.perf_counter()
            fig = func(ds)
            spans.append((f"build {topic}/{name}", time.perf_counter() - t0))

            if WITH_SAVE:
                out_path = save_dir / f"{topic}__{name}.png"
                t0 = time.perf_counter()
                fig.savefig(out_path, dpi=200)
                spans.append((f"save {topic}/{name}", time.perf_counter() - t0))

            plt.close(fig)

    _print_report(save_dir)


def _print_report(save_dir: Path | None) -> None:
    total = sum(seconds for _, seconds in spans)

    materialize_total = sum(s for label, s in spans if label == "_materialize()")
    query_new_total = sum(s for label, s in spans if label.startswith("query(") and "[new]" in label)
    query_cached_total = sum(s for label, s in spans if label.startswith("query(") and "cache hit" in label)
    query_new_count = sum(1 for label, _ in spans if label.startswith("query(") and "[new]" in label)
    query_cached_count = sum(1 for label, _ in spans if label.startswith("query(") and "cache hit" in label)

    print()
    print(f"{'step':<70} {'seconds':>10} {'% total':>8}")
    print("-" * 90)
    for label, seconds in sorted(spans, key=lambda x: -x[1]):
        print(f"{label:<70} {seconds:>10.3f} {100 * seconds / total:>7.1f}%")
    print("-" * 90)
    print(f"{'TOTAL':<70} {total:>10.3f} {100.0:>7.1f}%")
    print()
    print(f"_materialize(): {materialize_total:.3f}s ({100 * materialize_total / total:.1f}% of total)")
    print(f"new queries:    {query_new_total:.3f}s across {query_new_count} calls")
    print(f"cached queries: {query_cached_total:.3f}s across {query_cached_count} calls (in-process cache)")
    if save_dir is not None:
        print()
        print(f"PNGs written to {save_dir} (not under version control, safe to delete)")


if __name__ == "__main__":
    main()
