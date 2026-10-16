"""Export merged historical debug cases from review queue + engineer feedback."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REVIEW_PATH = PROJECT_ROOT / "data" / "cache" / "review_queue.json"
FEEDBACK_PATH = PROJECT_ROOT / "data" / "cache" / "engineer_feedback.json"
OUT_DIR = PROJECT_ROOT / "output" / "historical_debug_cases"
OUT_FILE = OUT_DIR / "historical_debug_cases.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_historical_debug_cases() -> dict:
    queue = _load_json(REVIEW_PATH, {"items": []})
    feedback_rows = _load_json(FEEDBACK_PATH, [])
    if not isinstance(feedback_rows, list):
        feedback_rows = []

    items = queue.get("items", []) if isinstance(queue, dict) else []
    feedback_by_review: dict[str, list] = {}
    for row in feedback_rows:
        rid = row.get("review_item_id")
        if rid:
            feedback_by_review.setdefault(str(rid), []).append(row)

    cases: list[dict] = []
    for item in items:
        status = item.get("status")
        if status not in ("confirmed", "rejected"):
            continue
        case_id = str(item.get("id", ""))
        cases.append(
            {
                "case_id": case_id,
                "outcome": status,
                "decision": item.get("decision"),
                "kind": item.get("kind"),
                "chain": item.get("chain"),
                "cell_name": item.get("cell_name"),
                "fail_flop_id": item.get("fail_flop_id"),
                "confidence": item.get("confidence"),
                "confidence_pct": item.get("confidence_pct"),
                "predicted_root_cause": item.get("predicted_root_cause"),
                "observations": item.get("observations"),
                "lots_affected": item.get("lots_affected"),
                "evidence_score": item.get("evidence_score"),
                "ml_confidence": item.get("ml_confidence"),
                "offset_from_scan_in": item.get("offset_from_scan_in"),
                "chain_length": item.get("chain_length"),
                "priority_score": item.get("priority_score"),
                "reviewed_at": item.get("reviewed_at"),
                "created_at": item.get("created_at"),
                "reviewer_note": item.get("reviewer_note"),
                "data_fingerprint": item.get("data_fingerprint"),
                "review": item,
                "engineer_feedback": feedback_by_review.get(case_id, []),
            }
        )

    linked = {c["case_id"] for c in cases}
    for row in feedback_rows:
        rid = str(row.get("review_item_id", ""))
        if rid in linked:
            continue
        pc = row.get("pattern_consistency")
        cases.append(
            {
                "case_id": rid or None,
                "outcome": "confirmed" if row.get("pfa_confirmed") == 1 else "rejected",
                "decision": "confirm" if row.get("pfa_confirmed") == 1 else "reject",
                "kind": "cell",
                "chain": row.get("chain"),
                "cell_name": row.get("cell_name"),
                "fail_flop_id": None,
                "confidence": pc,
                "confidence_pct": round(float(pc) * 100, 1) if pc is not None else None,
                "predicted_root_cause": row.get("root_cause_type"),
                "observations": row.get("pattern_count"),
                "lots_affected": None,
                "evidence_score": pc,
                "ml_confidence": None,
                "offset_from_scan_in": row.get("offset_from_scan_in"),
                "chain_length": row.get("chain_length"),
                "priority_score": None,
                "reviewed_at": row.get("recorded_at"),
                "created_at": row.get("recorded_at"),
                "reviewer_note": None,
                "data_fingerprint": None,
                "review": None,
                "engineer_feedback": [row],
            }
        )

    confirmed = sum(1 for c in cases if c["outcome"] == "confirmed")
    rejected = sum(1 for c in cases if c["outcome"] == "rejected")
    return {
        "artifact": "historical_debug_cases",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "review_queue": "data/cache/review_queue.json",
            "engineer_feedback": "data/cache/engineer_feedback.json",
        },
        "summary": {
            "total_cases": len(cases),
            "confirmed": confirmed,
            "rejected": rejected,
            "review_queue_items_merged": sum(1 for c in cases if c.get("review") is not None),
            "engineer_feedback_rows": len(feedback_rows),
        },
        "cases": cases,
    }


def main() -> None:
    payload = build_historical_debug_cases()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = payload["summary"]
    print(
        f"Wrote {OUT_FILE} — {summary['total_cases']} cases "
        f"({summary['confirmed']} confirmed, {summary['rejected']} rejected)"
    )


if __name__ == "__main__":
    main()
