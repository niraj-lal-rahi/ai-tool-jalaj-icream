from __future__ import annotations

import sqlite3
from difflib import SequenceMatcher
from pathlib import Path


class AdaptiveLearner:
    def __init__(self, db_path: str = "data/learning.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS name_corrections (
                observed_name TEXT NOT NULL,
                corrected_name TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 1,
                PRIMARY KEY (observed_name, corrected_name)
            )
            """
        )
        self.conn.commit()

    def remember_name_correction(self, observed_name: str, corrected_name: str, confidence: float = 1.0) -> None:
        self.conn.execute(
            """
            INSERT INTO name_corrections(observed_name, corrected_name, confidence, usage_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(observed_name, corrected_name)
            DO UPDATE SET
                confidence = (name_corrections.confidence + excluded.confidence) / 2.0,
                usage_count = name_corrections.usage_count + 1
            """,
            (observed_name.lower().strip(), corrected_name.title().strip(), confidence),
        )
        self.conn.commit()

    def suggest_correction(self, observed_name: str, min_score: int = 75) -> str | None:
        observed = observed_name.lower().strip()
        rows = self.conn.execute(
            "SELECT observed_name, corrected_name, confidence, usage_count FROM name_corrections"
        ).fetchall()

        if not rows:
            return None

        scored = []
        for row in rows:
            score = int(SequenceMatcher(None, observed, row[0]).ratio() * 100)
            scored.append((score, row))

        scored.sort(key=lambda x: (x[0], x[1][3], x[1][2]), reverse=True)
        best_score, best_row = scored[0]
        if best_score < min_score:
            return None

        return best_row[1]

    def close(self) -> None:
        self.conn.close()
