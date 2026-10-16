"""Export wafer fail bitmaps from ATE log headers under data/logs/."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "data" / "logs"
OUT_DIR = PROJECT_ROOT / "output" / "failing_bitmaps"
OUT_FILE = OUT_DIR / "failing_bitmaps.json"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from parser import discover_logs  # noqa: E402
from topology_analysis import parse_log_metadata  # noqa: E402


def _die_status(source_file: str) -> str:
    name = source_file.lower()
    if name.startswith("fail_die"):
        return "fail"
    if name.startswith("good_die"):
        return "pass"
    return "unknown"


def _as_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _die_entry(meta: dict) -> dict:
    source = meta.get("source_file", "")
    return {
        "die_label": meta.get("die_label"),
        "source_file": source,
        "lot_folder": meta.get("lot_folder"),
        "status": _die_status(source),
        "die_row": _as_int(meta.get("die_row")),
        "die_col": _as_int(meta.get("die_col")),
        "wafer_x": _as_float(meta.get("wafer_x")),
        "wafer_y": _as_float(meta.get("wafer_y")),
        "x1": _as_float(meta.get("x1")),
        "y1": _as_float(meta.get("y1")),
        "x2": _as_float(meta.get("x2")),
        "y2": _as_float(meta.get("y2")),
        "defect_type": meta.get("defect_type"),
        "lot_id": meta.get("lot_id"),
        "device_name": meta.get("device_name"),
        "test_program": meta.get("test_program"),
    }


def _bitmap_grid(dies: list[dict]) -> dict[str, str]:
    grid: dict[str, str] = {}
    for die in dies:
        row, col = die.get("die_row"), die.get("die_col")
        if row is None or col is None:
            continue
        grid[f"{row},{col}"] = die.get("status", "unknown")
    return grid


def build_failing_bitmaps(log_dir: Path | None = None) -> dict:
    log_dir = log_dir or LOG_DIR
    paths = discover_logs(log_dir)
    metas = [parse_log_metadata(p) for p in paths]

    by_lot: dict[str, list[dict]] = {}
    for meta in metas:
        lot_key = meta.get("lot_id") or meta.get("lot_folder") or "UNKNOWN"
        by_lot.setdefault(str(lot_key), []).append(_die_entry(meta))

    lots: list[dict] = []
    total_fail = total_pass = 0

    for lot_id in sorted(by_lot):
        dies = sorted(
            by_lot[lot_id],
            key=lambda d: (d.get("die_row") or 0, d.get("die_col") or 0, d.get("source_file") or ""),
        )
        fail_count = sum(1 for d in dies if d["status"] == "fail")
        pass_count = sum(1 for d in dies if d["status"] == "pass")
        total_fail += fail_count
        total_pass += pass_count

        rows = [d["die_row"] for d in dies if d["die_row"] is not None]
        cols = [d["die_col"] for d in dies if d["die_col"] is not None]
        lot_folder = dies[0].get("lot_folder") if dies else None
        defect_type = dies[0].get("defect_type") if dies else None

        lots.append(
            {
                "lot_id": lot_id,
                "lot_folder": lot_folder,
                "defect_type": defect_type,
                "die_count": len(dies),
                "fail_count": fail_count,
                "pass_count": pass_count,
                "die_row_range": [min(rows), max(rows)] if rows else None,
                "die_col_range": [min(cols), max(cols)] if cols else None,
                "bitmap_grid": _bitmap_grid(dies),
                "dies": dies,
            }
        )

    return {
        "artifact": "failing_bitmaps",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "data/logs/",
        "description": (
            "Wafer die pass/fail map derived from ATE log headers. "
            "status=fail for fail_die_*.log, status=pass for good_die_*.log. "
            "bitmap_grid keys are 'die_row,die_col' -> pass|fail."
        ),
        "summary": {
            "total_logs": len(metas),
            "lot_count": len(lots),
            "fail_dies": total_fail,
            "pass_dies": total_pass,
        },
        "lots": lots,
    }


def main() -> None:
    payload = build_failing_bitmaps()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = payload["summary"]
    print(
        f"Wrote {OUT_FILE} — {summary['total_logs']} dies across "
        f"{summary['lot_count']} lots ({summary['fail_dies']} fail, {summary['pass_dies']} pass)"
    )


if __name__ == "__main__":
    main()
