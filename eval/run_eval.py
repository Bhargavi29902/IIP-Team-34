"""Measure extraction accuracy on the labelled fictional emails.
Usage: python eval/run_eval.py   (exit code 1 if accuracy is below the threshold)"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.config import Config, TestConfig  # noqa: E402
from app.services.extraction import extract_tasks  # noqa: E402

CLIENTS = ["Harbourview Logistics Pte Ltd", "Lotus Bay Hotels", "Meridian Foods Pte Ltd"]
THRESHOLD = 0.9


def evaluate() -> dict:
    cases = json.loads(Config.EVAL_FILE.read_text(encoding="utf-8"))
    totals = {"count": [0, 0], "owner": [0, 0], "due_date": [0, 0], "client": [0, 0]}
    for case in cases:
        sent = date.fromisoformat(case["sent_on"])
        got = extract_tasks(case["body"], sent, CLIENTS).tasks
        exp = case["expected"]
        totals["count"][1] += 1
        totals["count"][0] += int(len(got) == len(exp))
        for g, e in zip(got, exp):
            for field in ("owner", "client"):
                totals[field][1] += 1
                totals[field][0] += int(getattr(g, field) == e[field])
            totals["due_date"][1] += 1
            totals["due_date"][0] += int((g.due_date.isoformat() if g.due_date else None) == e["due_date"])
    report = {k: (v[0] / v[1] if v[1] else 1.0) for k, v in totals.items()}
    report["overall"] = sum(report.values()) / len(report)
    return report


if __name__ == "__main__":
    app = create_app(TestConfig if "--mock" in sys.argv else Config)
    with app.app_context():
        r = evaluate()
    for k, v in r.items():
        print(f"{k:10s} {v:6.1%}")
    sys.exit(0 if r["overall"] >= THRESHOLD else 1)
