from src.adaptive_learning import AdaptiveLearner


def test_learner_remembers_and_suggests(tmp_path) -> None:
    db = tmp_path / "learning.db"
    learner = AdaptiveLearner(db_path=str(db))
    try:
        learner.remember_name_correction("milkk", "Milk", confidence=0.9)
        suggestion = learner.suggest_correction("milk")
        assert suggestion == "Milk"
    finally:
        learner.close()
