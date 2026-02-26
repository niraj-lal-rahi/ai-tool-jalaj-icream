from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

from .adaptive_learning import AdaptiveLearner
from .ocr_engine import OcrEngine
from .parser import extract_seller_name, parse_lines


def run_pipeline(image_path: str, output_path: str, db_path: str) -> List[Dict[str, float | str]]:
    ocr = OcrEngine()
    learner = AdaptiveLearner(db_path=db_path)

    try:
        lines = ocr.extract_lines(image_path)
        items = parse_lines(lines)
        seller_name = extract_seller_name(lines)

        for item in items:
            corrected = learner.suggest_correction(item.name)
            if corrected:
                item.name = corrected

        rows = [
            {
                "seller_name": seller_name or "",
                "item": i.name,
                "sold_qty": i.sold_qty,
                "returned_qty": i.returned_qty,
                "unit_price": i.unit_price,
                "net_qty": i.net_qty,
                "net_value": i.net_value,
            }
            for i in items
        ]

        rows = sorted(rows, key=lambda r: str(r["item"]))
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["seller_name", "item", "sold_qty", "returned_qty", "unit_price", "net_qty", "net_value"],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        return rows
    finally:
        learner.close()


def apply_feedback(db_path: str, observed: str, corrected: str, confidence: float = 1.0) -> None:
    learner = AdaptiveLearner(db_path=db_path)
    try:
        learner.remember_name_correction(observed_name=observed, corrected_name=corrected, confidence=confidence)
    finally:
        learner.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sales data from handwritten item sheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run OCR and generate sales report CSV")
    run_parser.add_argument("image", help="Path to handwritten sheet image")
    run_parser.add_argument("--output", default="output/report.csv", help="Output CSV path")
    run_parser.add_argument("--db", default="data/learning.db", help="Path to adaptive-learning DB")

    feedback_parser = subparsers.add_parser("feedback", help="Teach the tool from user correction")
    feedback_parser.add_argument("--observed", required=True, help="OCR-detected item name")
    feedback_parser.add_argument("--corrected", required=True, help="True corrected item name")
    feedback_parser.add_argument("--confidence", type=float, default=1.0, help="Correction confidence score")
    feedback_parser.add_argument("--db", default="data/learning.db", help="Path to adaptive-learning DB")

    args = parser.parse_args()

    if args.command == "run":
        rows = run_pipeline(args.image, args.output, args.db)
        if not rows:
            print("No valid rows detected. Please verify the image and line format.")
        else:
            for row in rows:
                print(row)
            print(f"\nReport saved to: {args.output}")
    elif args.command == "feedback":
        apply_feedback(args.db, args.observed, args.corrected, args.confidence)
        print("Feedback saved. Future runs will auto-correct similar item names.")


if __name__ == "__main__":
    main()
