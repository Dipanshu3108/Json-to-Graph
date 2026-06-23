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


def test_scatter_missing_y() -> None:
    raw = {
        "datasets": [
            {
                "label": "Samples",
                "data": [{"x": "1"}, {"x": "3"}],
            }
        ]
    }
    normalized = normalize(raw)
    assert normalized["datasets"][0]["data"] == [{"x": 1, "y": 0}, {"x": 3, "y": 0}]


def test_scatter_flat_array() -> None:
    raw = {"datasets": [{"data": [["1", "2"], ["3", "4"]]}]}
    normalized = normalize(raw)
    assert normalized["datasets"][0]["data"] == [{"x": 1, "y": 2}, {"x": 3, "y": 4}]


def test_regular_numeric_strings() -> None:
    raw = {"labels": ["A", "B"], "datasets": [{"label": "S1", "data": ["1", "2"]}]}
    normalized = normalize(raw)
    assert normalized["datasets"][0]["data"] == [1, 2]


def test_y_key_not_remapped_in_scatter_point() -> None:
    raw = {"datasets": [{"data": [{"x": 1, "y": 2}]}]}
    normalized = normalize(raw)
    assert normalized["datasets"][0]["data"] == [{"x": 1, "y": 2}]
