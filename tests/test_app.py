from src.app import run_pipeline


class FakeOcr:
    def extract_lines(self, _image_path: str):
        return [
            "किशोरी ट्रेडर्स",
            "चना, 10, 2, 40",
            "मूंग, 5, 1, 20",
        ]


def test_run_pipeline_includes_seller_name(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("src.app.OcrEngine", lambda: FakeOcr())

    output = tmp_path / "report.csv"
    db = tmp_path / "learning.db"

    rows = run_pipeline("dummy.jpg", str(output), str(db))

    assert len(rows) == 2
    assert rows[0]["seller_name"] == "किशोरी ट्रेडर्स"
    assert output.read_text(encoding="utf-8").splitlines()[0].startswith("seller_name,item")
