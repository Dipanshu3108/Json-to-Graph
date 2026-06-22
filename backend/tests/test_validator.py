from app.services.validator import validate


def test_valid_bar_chart() -> None:
    data = {"labels": ["A", "B"], "datasets": [{"label": "S1", "data": [1, 2]}]}
    result = validate("bar", data)
    assert result["valid"] is True


def test_label_length_mismatch() -> None:
    data = {"labels": ["A"], "datasets": [{"label": "S1", "data": [1, 2]}]}
    result = validate("bar", data)
    assert result["valid"] is False
    assert any(
        "labels" in e["message"].lower() or "dataset" in e["message"].lower()
        for e in result["errors"]
    )


def test_pie_rejects_multiple_datasets() -> None:
    data = {
        "labels": ["A", "B"],
        "datasets": [
            {"label": "S1", "data": [1, 2]},
            {"label": "S2", "data": [3, 4]},
        ],
    }
    result = validate("pie", data)
    assert result["valid"] is False


def test_scatter_does_not_require_labels() -> None:
    data = {"datasets": [{"label": "S1", "data": [{"x": 1, "y": 2}]}]}
    result = validate("scatter", data)
    assert result["valid"] is True
