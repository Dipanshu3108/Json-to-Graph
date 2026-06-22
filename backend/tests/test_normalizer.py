from app.services.normalizer import normalize


def test_alias_remapping() -> None:
    raw = {"categories": ["A"], "series": [{"name": "S1", "values": [1]}]}
    normalized = normalize(raw)
    assert normalized["labels"] == ["A"]
    assert normalized["datasets"][0]["label"] == "S1"
    assert normalized["datasets"][0]["data"] == [1]


def test_data_to_dataset_coercion() -> None:
    raw = {"labels": ["A", "B"], "data": [1, 2]}
    normalized = normalize(raw)
    assert "data" not in normalized
    assert normalized["datasets"][0]["label"] == "Dataset 1"
