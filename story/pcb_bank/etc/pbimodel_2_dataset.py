"""
read powerbi data model tmdl

output:
    model_definition.json
        store in data
        defining calculated dimensions and measures from dax of powerbi (along with their number format)
        this json is ready to be read from DataSet to convert to usable dim/mes

Covers exactly the DAX grammar found in v_pcb_cvm_client.tmdl (verified against
the full file before writing this): DISTINCTCOUNT, SUM, CALCULATE(<measure ref>,
FILTER(table, <cond>)), DIVIDE, and IF (used by one calculated column). Any DAX
shape outside that set raises ValueError naming the offending measure/column
rather than silently emitting wrong SQL.

Usage: python pbimodel_2_dataset.py
(paths are resolved relative to this file — no arguments needed for this project)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ETC_DIR = Path(__file__).resolve().parent
PCB_BANK_DIR = ETC_DIR.parent
REPO_ROOT = PCB_BANK_DIR.parent.parent
TMDL_PATH = PCB_BANK_DIR / "data" / "v_pcb_cvm_client.tmdl"
PARQUET_PATH = PCB_BANK_DIR / "data" / "v_pcb_cvm_client.parquet"
OUTPUT_PATH = PCB_BANK_DIR / "data" / "model_definition.json"

sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# formatString -> viz fmt token mapping (explicit table, no guessing — see
# src/custom/formatting.py for the full DataLabelFormat/DimensionFormat sets)
# ---------------------------------------------------------------------------
MEASURE_FMT_MAP: dict[str, str] = {
    "#,0": "#,",
    "0": "#",
    "0.0%": "%.1",
    "0.0%;-0.0%;0.0%": "%.1",
    "0.00%;-0.00%;0.00%": "%.2",
}
DIMENSION_FMT_MAP: dict[str, str] = {
    "yy-mm": "yy-mm",
}


# ---------------------------------------------------------------------------
# Step 1 — TMDL block parser (table/column/measure), adapted from the
# dax-engineer skill's tmdl_parser.py reference: same tab-indent state
# machine and CRLF normalization, extended to also capture dataType/
# formatString/sourceColumn for columns.
# ---------------------------------------------------------------------------


@dataclass
class RawColumn:
    name: str
    data_type: str | None = None
    source_column: str | None = None
    format_string: str | None = None
    inline_dax: str | None = None  # `column NAME = <dax>` calculated columns


@dataclass
class RawMeasure:
    name: str
    dax: str
    format_string: str | None = None


def parse_tmdl(path: Path) -> tuple[str, list[RawColumn], list[RawMeasure]]:
    lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")

    table_name: str | None = None
    columns: list[RawColumn] = []
    measures: list[RawMeasure] = []

    current_col: RawColumn | None = None
    current_meas: RawMeasure | None = None
    reading_dax = False  # multi-line DAX continuation (3-tab indent) — not
    # hit by this file (every measure is single-line inline), kept for safety
    # if this parser is ever pointed at another TMDL export.
    in_partition = False

    for line in lines:
        if table_name is None:
            m = re.match(r"^table\s+'(.+)'$", line.strip()) or re.match(
                r"^table\s+(\S+)$", line.strip()
            )
            if m:
                table_name = m.group(1)
                continue

        if re.match(r"^\tpartition\b", line):
            in_partition = True
        if in_partition:
            continue

        m = re.match(r"^\tmeasure '(.+?)' =\s*(.*)$", line)
        if m:
            current_col = None
            name, dax = m.group(1), m.group(2).strip()
            current_meas = RawMeasure(name=name, dax=dax)
            measures.append(current_meas)
            reading_dax = not bool(dax)
            continue

        if reading_dax and current_meas is not None:
            if line.startswith("\t\t\t"):
                chunk = line.strip()
                if chunk:
                    current_meas.dax = (
                        f"{current_meas.dax} {chunk}".strip()
                        if current_meas.dax
                        else chunk
                    )
                continue
            reading_dax = False

        m = re.match(r"^\tcolumn\s+(\S+)(?:\s*=\s*(.*))?$", line)
        if m:
            current_meas = None
            name, inline_dax = m.group(1), m.group(2)
            current_col = RawColumn(
                name=name, inline_dax=(inline_dax.strip() if inline_dax else None)
            )
            columns.append(current_col)
            continue

        if current_meas is not None:
            fm = re.match(r"^\t\tformatString:\s*(.*)$", line)
            if fm:
                current_meas.format_string = fm.group(1).strip()
                continue

        if current_col is not None:
            fm = re.match(r"^\t\tdataType:\s*(.*)$", line)
            if fm:
                current_col.data_type = fm.group(1).strip()
                continue
            fm = re.match(r"^\t\tformatString:\s*(.*)$", line)
            if fm:
                current_col.format_string = fm.group(1).strip()
                continue
            fm = re.match(r"^\t\tsourceColumn:\s*(.*)$", line)
            if fm:
                current_col.source_column = fm.group(1).strip()
                continue

    if table_name is None:
        raise ValueError(f"Could not find `table` declaration in {path}")

    return table_name, columns, measures


# ---------------------------------------------------------------------------
# Step 2 — DAX tokenizer + recursive-descent parser + SQL emitter
# ---------------------------------------------------------------------------


@dataclass
class Token:
    kind: str
    value: str


@dataclass
class FuncCall:
    name: str
    args: list


@dataclass
class BinOp:
    op: str
    left: object
    right: object


@dataclass
class Ref:
    name: str  # bracket content, table-qualifier already stripped


@dataclass
class Ident:
    name: str  # bare identifier not followed by '(' — e.g. FILTER's table arg


@dataclass
class Literal:
    value: object


_TOKEN_RE = re.compile(
    r"""\s*(?:
        (?P<STRING>"[^"]*")
      | (?P<QREF>[A-Za-z_][A-Za-z0-9_]*\[[^\]]+\])
      | (?P<REF>\[[^\]]+\])
      | (?P<NUM>-?\d+(?:\.\d+)?)
      | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
      | (?P<NE><>)
      | (?P<GE>>=)
      | (?P<LE><=)
      | (?P<OR>\|\|)
      | (?P<AND>&&)
      | (?P<EQ>=)
      | (?P<GT>>)
      | (?P<LT><)
      | (?P<COMMA>,)
      | (?P<LPAREN>\()
      | (?P<RPAREN>\))
    )""",
    re.VERBOSE,
)

_CMP_KINDS = {"EQ": "=", "NE": "<>", "GE": ">=", "LE": "<=", "GT": ">", "LT": "<"}


def tokenize(dax: str) -> list[Token]:
    tokens: list[Token] = []
    pos, length = 0, len(dax)
    while pos < length:
        m = _TOKEN_RE.match(dax, pos)
        if not m or m.end() == pos:
            raise ValueError(f"Cannot tokenize DAX at position {pos}: {dax[pos:pos + 30]!r}")
        pos = m.end()
        if m.lastgroup is not None:
            tokens.append(Token(m.lastgroup, m.group(m.lastgroup)))
    return tokens


def _parse_or(tokens: list[Token], pos: int):
    left, pos = _parse_and(tokens, pos)
    while pos < len(tokens) and tokens[pos].kind == "OR":
        right, pos = _parse_and(tokens, pos + 1)
        left = BinOp("OR", left, right)
    return left, pos


def _parse_and(tokens: list[Token], pos: int):
    left, pos = _parse_cmp(tokens, pos)
    while pos < len(tokens) and tokens[pos].kind == "AND":
        right, pos = _parse_cmp(tokens, pos + 1)
        left = BinOp("AND", left, right)
    return left, pos


def _parse_cmp(tokens: list[Token], pos: int):
    left, pos = _parse_primary(tokens, pos)
    if pos < len(tokens) and tokens[pos].kind in _CMP_KINDS:
        op = _CMP_KINDS[tokens[pos].kind]
        right, pos = _parse_primary(tokens, pos + 1)
        return BinOp(op, left, right), pos
    return left, pos


def _parse_args(tokens: list[Token], pos: int):
    args = []
    if tokens[pos].kind == "RPAREN":
        return args, pos + 1
    while True:
        arg, pos = _parse_or(tokens, pos)
        args.append(arg)
        if tokens[pos].kind == "COMMA":
            pos += 1
            continue
        if tokens[pos].kind == "RPAREN":
            return args, pos + 1
        raise ValueError(f"Expected ',' or ')' in argument list, got {tokens[pos]}")


def _parse_primary(tokens: list[Token], pos: int):
    if pos >= len(tokens):
        raise ValueError("Unexpected end of DAX expression")
    tok = tokens[pos]

    if tok.kind == "STRING":
        return Literal(tok.value[1:-1]), pos + 1
    if tok.kind == "NUM":
        value = float(tok.value) if "." in tok.value else int(tok.value)
        return Literal(value), pos + 1
    if tok.kind == "QREF":
        name = tok.value[tok.value.index("[") + 1 : -1]
        return Ref(name), pos + 1
    if tok.kind == "REF":
        return Ref(tok.value[1:-1]), pos + 1
    if tok.kind == "LPAREN":
        inner, pos = _parse_or(tokens, pos + 1)
        if pos >= len(tokens) or tokens[pos].kind != "RPAREN":
            raise ValueError("Expected ')'")
        return inner, pos + 1
    if tok.kind == "IDENT":
        if pos + 1 < len(tokens) and tokens[pos + 1].kind == "LPAREN":
            args, pos = _parse_args(tokens, pos + 2)
            return FuncCall(tok.value, args), pos
        return Ident(tok.value), pos + 1

    raise ValueError(f"Unexpected token {tok.kind}:{tok.value!r} at position {pos}")


def parse_dax(dax: str):
    tokens = tokenize(dax)
    node, pos = _parse_or(tokens, 0)
    if pos != len(tokens):
        raise ValueError(f"Trailing tokens after parsing DAX {dax!r}: {tokens[pos:]}")
    return node


_BASE_AGG_FUNCS = {"DISTINCTCOUNT", "SUM"}


class Translator:
    """Emits SQL for a parsed DAX AST. `known_measures`/`raw_by_name` let a
    bracket ref resolve as a cross-measure `{name}` placeholder (Dataset's
    own recursive formula resolver, src/dataset.py::_resolve_formula, takes
    it from there) vs. a plain column reference.

    CALCULATE(<measure ref>, FILTER(table, cond)) is handled structurally,
    NOT via the generic `{ref}` placeholder: DuckDB rejects a FILTER clause
    on a parenthesized expression (`(agg(...)) FILTER (WHERE ...)` is a
    syntax error — confirmed directly against DuckDB before writing this),
    and Dataset's `{ref}` substitution always parenthesizes. So instead the
    referenced base measure's own DAX is re-parsed and its aggregate
    argument is wrapped in `CASE WHEN cond THEN col END`, producing one
    self-contained aggregate call with no placeholder involved. This only
    supports the referenced measure resolving to a bare DISTINCTCOUNT/SUM
    call (confirmed true for every CALCULATE in this file — all 30 reference
    the same base measure, `# Client`, not a chained/already-filtered one);
    a chained CALCULATE would raise here rather than silently mistranslate.
    """

    def __init__(self, known_measures: set[str], raw_by_name: dict[str, RawMeasure]):
        self.known_measures = known_measures
        self.raw_by_name = raw_by_name

    def emit(self, node, *, context: str) -> str:
        if isinstance(node, Literal):
            if isinstance(node.value, str):
                return "'{}'".format(node.value.replace("'", "''"))
            return str(node.value)

        if isinstance(node, Ref):
            if node.name in self.known_measures:
                return f"{{{node.name}}}"
            return f'"{node.name}"'

        if isinstance(node, Ident):
            raise ValueError(
                f"Unexpected bare identifier {node.name!r} in {context} "
                "(only valid as FILTER's table argument)"
            )

        if isinstance(node, BinOp):
            left = self.emit(node.left, context=context)
            right = self.emit(node.right, context=context)
            if node.op in ("OR", "AND"):
                return f"({left} {node.op} {right})"
            return f"{left} {node.op} {right}"

        if isinstance(node, FuncCall):
            return self._emit_func(node, context=context)

        raise ValueError(f"Unknown DAX AST node {node!r} in {context}")

    def _emit_func(self, node: FuncCall, *, context: str) -> str:
        fn = node.name.upper()

        if fn == "DISTINCTCOUNT":
            return f"count(distinct {self.emit(node.args[0], context=context)})"

        if fn == "SUM":
            return f"sum({self.emit(node.args[0], context=context)})"

        if fn == "DIVIDE":
            a = self.emit(node.args[0], context=context)
            b = self.emit(node.args[1], context=context)
            return f"({a}) / NULLIF({b}, 0)"

        if fn == "IF":
            cond = self.emit(node.args[0], context=context)
            t = self.emit(node.args[1], context=context)
            f_ = self.emit(node.args[2], context=context)
            return f"CASE WHEN {cond} THEN {t} ELSE {f_} END"

        if fn == "CALCULATE":
            return self._emit_calculate(node, context=context)

        raise ValueError(f"Unsupported DAX function {node.name!r} in {context}")

    def _emit_calculate(self, node: FuncCall, *, context: str) -> str:
        if len(node.args) != 2:
            raise ValueError(f"CALCULATE with {len(node.args)} args in {context} (expected 2)")
        inner, filter_call = node.args
        if not (isinstance(filter_call, FuncCall) and filter_call.name.upper() == "FILTER"):
            raise ValueError(f"CALCULATE's 2nd arg must be FILTER(...) in {context}")
        if len(filter_call.args) != 2:
            raise ValueError(f"FILTER with {len(filter_call.args)} args in {context} (expected 2)")
        cond_sql = self.emit(filter_call.args[1], context=context)

        if not isinstance(inner, Ref):
            raise ValueError(
                f"CALCULATE's 1st arg must be a measure reference in {context}, got {inner!r}"
            )
        if inner.name not in self.raw_by_name:
            raise ValueError(f"CALCULATE references unknown measure {inner.name!r} in {context}")

        base_raw = self.raw_by_name[inner.name]
        base_ast = parse_dax(base_raw.dax)
        if not (isinstance(base_ast, FuncCall) and base_ast.name.upper() in _BASE_AGG_FUNCS):
            raise ValueError(
                f"CALCULATE in {context} references measure {inner.name!r}, which must resolve "
                f"to a bare {sorted(_BASE_AGG_FUNCS)} call — chained/filtered CALCULATE refs "
                "aren't supported. Got: " + repr(base_ast)
            )
        col_sql = self.emit(base_ast.args[0], context=f"{context} (via {inner.name!r})")
        case_expr = f"CASE WHEN {cond_sql} THEN {col_sql} END"
        agg_fn = base_ast.name.upper()
        return f"count(distinct {case_expr})" if agg_fn == "DISTINCTCOUNT" else f"sum({case_expr})"


# ---------------------------------------------------------------------------
# Step 3 — assemble model_definition.json
# ---------------------------------------------------------------------------

_DUMMY_COLUMN_RE = re.compile(r'^""$')


def build_schema(
    table: str, columns: list[RawColumn], measures: list[RawMeasure]
) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    known_measures = {m.name for m in measures}
    raw_by_name = {m.name: m for m in measures}
    translator = Translator(known_measures, raw_by_name)

    dimensions = []
    for col in columns:
        if col.inline_dax is not None and _DUMMY_COLUMN_RE.match(col.inline_dax):
            continue  # `_dummy1..5` placeholders — no dataType/sourceColumn, not real data

        if col.inline_dax is not None:
            # the one real calculated column: APPL_F_SIGNNC_XS = IF(...)
            transform = translator.emit(parse_dax(col.inline_dax), context=f"column {col.name!r}")
            dimensions.append({"name": col.name, "transform": transform})
            continue

        if col.data_type == "dateTime" and col.format_string in DIMENSION_FMT_MAP:
            dimensions.append({"name": col.name, "fmt": DIMENSION_FMT_MAP[col.format_string]})
        elif col.data_type == "dateTime" and col.format_string:
            warnings.append(
                f"column {col.name!r}: no DimensionFormat mapping for formatString "
                f"{col.format_string!r} — left unformatted"
            )
        # plain non-date columns need no JSON entry — Dataset auto-discovers them.

    out_measures = []
    for meas in measures:
        formula = translator.emit(parse_dax(meas.dax), context=f"measure {meas.name!r}")
        fmt = MEASURE_FMT_MAP.get(meas.format_string) if meas.format_string else None
        if meas.format_string and fmt is None:
            warnings.append(
                f"measure {meas.name!r}: no DataLabelFormat mapping for formatString "
                f"{meas.format_string!r} — left unformatted"
            )
        out_measures.append(
            {"name": meas.name, "formula": formula, "fmt": fmt, "dax": meas.dax}
        )

    schema = {"table": table, "dimensions": dimensions, "measures": out_measures}
    return schema, warnings


# ---------------------------------------------------------------------------
# Step 4 — self-validate: run every translated measure against the real
# parquet through the actual Dataset/query() pipeline (not just a syntax
# check) — the strongest available proof the translation is correct.
# ---------------------------------------------------------------------------


def validate_against_parquet(schema: dict) -> list[str]:
    from src.dataset import Dataset

    failures: list[str] = []
    ds = Dataset(PARQUET_PATH)
    ds.load_schema(OUTPUT_PATH)
    for entry in schema["measures"]:
        name = entry["name"]
        try:
            ds.query(dim="DATE_REPORT_QUARTER", measure=name)
        except Exception as exc:  # noqa: BLE001 — collecting all failures, not stopping at first
            failures.append(f"{name!r}: {exc}")
    return failures


def main() -> None:
    table, columns, measures = parse_tmdl(TMDL_PATH)
    schema, warnings = build_schema(table, columns, measures)

    OUTPUT_PATH.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

    n_dummy = sum(
        1 for c in columns if c.inline_dax is not None and _DUMMY_COLUMN_RE.match(c.inline_dax)
    )
    print(f"Parsed table: {table}")
    print(
        f"Columns: {len(columns)} total "
        f"({n_dummy} dummy skipped, {len(schema['dimensions'])} written to JSON)"
    )
    print(f"Measures: {len(measures)} parsed, {len(schema['measures'])} translated")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    print(f"\nWrote {OUTPUT_PATH}")

    print(f"\nValidating all {len(schema['measures'])} measures against {PARQUET_PATH.name} ...")
    failures = validate_against_parquet(schema)
    ok_count = len(schema["measures"]) - len(failures)
    if failures:
        print(f"{ok_count}/{len(schema['measures'])} OK, {len(failures)} FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(f"{ok_count}/{len(schema['measures'])} OK — all measures query successfully.")


if __name__ == "__main__":
    main()
