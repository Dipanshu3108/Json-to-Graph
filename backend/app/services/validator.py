import logging

from pydantic import ValidationError

from ..schemas.chart import ChartInput, ScatterInput

logger = logging.getLogger(__name__)

CHART_TYPES_REQUIRING_LABELS = {"bar", "line", "pie", "doughnut", "area"}
SCATTER_TYPES = {"scatter"}
SINGLE_DATASET_TYPES = {"pie", "doughnut"}


def validate(chart_type: str, raw_data: dict) -> dict:
    """
    Returns:
        {
            "valid": bool,
            "errors": list[dict],
            "normalizedData": dict | None
        }
    """
    logger.info("validator.start chart_type=%s top_keys=%s", chart_type, sorted(raw_data.keys()))
    errors: list[dict] = []

    try:
        if chart_type in CHART_TYPES_REQUIRING_LABELS:
            model = ChartInput.model_validate(raw_data)

            if chart_type in SINGLE_DATASET_TYPES and len(model.datasets) > 1:
                errors.append(
                    {
                        "field": "datasets",
                        "message": f"'{chart_type}' charts support only one dataset; "
                        f"{len(model.datasets)} were provided.",
                        "suggestion": "Keep only the first dataset, or switch to a 'bar' chart.",
                    }
                )
                logger.warning("validator.failed chart_type=%s reason=too_many_datasets", chart_type)
                return {"valid": False, "errors": errors, "normalizedData": None}

            logger.info("validator.success chart_type=%s datasets=%d", chart_type, len(model.datasets))
            return {"valid": True, "errors": [], "normalizedData": model.model_dump()}

        if chart_type in SCATTER_TYPES:
            model = ScatterInput.model_validate(raw_data)
            logger.info(
                "validator.success chart_type=%s datasets=%d",
                chart_type,
                len(model.datasets),
            )
            return {"valid": True, "errors": [], "normalizedData": model.model_dump()}

        logger.warning("validator.failed chart_type=%s reason=unknown_chart_type", chart_type)
        return {
            "valid": False,
            "errors": [{"field": "chartType", "message": f"Unknown chart type: '{chart_type}'"}],
            "normalizedData": None,
        }

    except ValidationError as exc:
        for err in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "suggestion": _suggest(err),
                }
            )
        logger.warning(
            "validator.failed chart_type=%s error_count=%d errors=%s",
            chart_type,
            len(errors),
            errors,
        )
        return {"valid": False, "errors": errors, "normalizedData": None}


def _suggest(err: dict) -> str:
    """Map common Pydantic error types to actionable hints."""
    error_type = err.get("type")
    if error_type == "missing":
        return f"Add the missing field: '{err['loc'][-1]}'"
    if error_type == "list_type":
        return "This field must be an array."
    if error_type == "float_parsing":
        return "All values in 'data' must be numbers."
    if error_type == "value_error":
        return err.get("msg", "")
    return ""
