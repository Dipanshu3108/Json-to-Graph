import logging
from typing import Any

logger = logging.getLogger(__name__)

KEY_ALIASES = {
    "categories": "labels",
    "xAxis": "labels",
    "x_axis": "labels",
    "keys": "labels",
    "names": "labels",
    "series": "datasets",
    "data_sets": "datasets",
    "dataset": "datasets",
    "name": "label",
    "title": "label",
    "id": "label",
    "values": "data",
    "yAxis": "data",
    "counts": "data",
    "numbers": "data",
}


def normalize(raw: dict) -> dict:
    """
    Best-effort structural normalization.
    Does NOT do LLM repair.
    """
    logger.info("normalizer.start top_keys=%s", sorted(raw.keys()))
    remapped = _remap_keys(raw)
    coerced = _coerce_datasets(remapped)
    result = _coerce_data_values(coerced)
    logger.info("normalizer.success top_keys=%s", sorted(result.keys()))
    return result


def _remap_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {KEY_ALIASES.get(k, k): _remap_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_remap_keys(item) for item in obj]
    return obj


def _coerce_datasets(raw: dict) -> dict:
    if "data" in raw and "datasets" not in raw:
        logger.info("normalizer.coerce flat 'data' -> 'datasets'")
        raw["datasets"] = [{"label": "Dataset 1", "data": raw.pop("data")}]
    return raw


def _to_number(value: Any, default: float = 0.0) -> float | int:
    """Convert strings/numbers to a numeric value; fall back to *default*."""
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return default
    return default


def _coerce_data_values(raw: dict) -> dict:
    """Fix common data-type issues inside datasets (numeric strings, missing x/y)."""
    datasets = raw.get("datasets")
    if not isinstance(datasets, list):
        return raw

    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue

        if not dataset.get("label"):
            logger.info("normalizer.add_default_label")
            dataset["label"] = "Dataset 1"

        data = dataset.get("data")
        if not isinstance(data, list):
            continue

        coerced: list[Any] = []
        for item in data:
            if isinstance(item, dict):
                # Scatter point or similar object.
                if "x" in item or "y" in item:
                    point = dict(item)
                    if "x" not in point:
                        point["x"] = 0
                    if "y" not in point:
                        point["y"] = 0
                    point["x"] = _to_number(point["x"], 0)
                    point["y"] = _to_number(point["y"], 0)
                    coerced.append(point)
                else:
                    coerced.append(item)
            elif isinstance(item, list) and len(item) == 2:
                # Flat [x, y] array for scatter.
                coerced.append({"x": _to_number(item[0], 0), "y": _to_number(item[1], 0)})
            else:
                coerced.append(_to_number(item, 0))

        dataset["data"] = coerced

    return raw
