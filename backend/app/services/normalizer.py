from typing import Any

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
    "y": "data",
    "yAxis": "data",
    "counts": "data",
    "numbers": "data",
}


def normalize(raw: dict) -> dict:
    """
    Best-effort structural normalization.
    Does NOT do LLM repair.
    """
    remapped = _remap_keys(raw)
    return _coerce_datasets(remapped)


def _remap_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {KEY_ALIASES.get(k, k): _remap_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_remap_keys(item) for item in obj]
    return obj


def _coerce_datasets(raw: dict) -> dict:
    if "data" in raw and "datasets" not in raw:
        raw["datasets"] = [{"label": "Dataset 1", "data": raw.pop("data")}]
    return raw
