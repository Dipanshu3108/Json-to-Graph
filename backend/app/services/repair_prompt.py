import json
import logging
from pathlib import Path

from ..schemas.chart import ChartTypeStr

logger = logging.getLogger(__name__)

_REPAIR_PROMPT_TEMPLATE = (
    Path(__file__).parent.parent / "prompts" / "repair_schema.txt"
).read_text(encoding="utf-8")


def _regular_schema() -> str:
    return json.dumps(
        {
            "labels": ["string", "..."],
            "datasets": [
                {
                    "label": "string",
                    "data": ["number", "..."],
                }
            ],
        },
        indent=2,
    ).replace('"..."', "...")


def _scatter_schema() -> str:
    return json.dumps(
        {
            "datasets": [
                {
                    "label": "string",
                    "data": [
                        {
                            "x": "number",
                            "y": "number",
                            "label": "string (optional)",
                        }
                    ],
                }
            ]
        },
        indent=2,
    )


_TARGET_SCHEMAS: dict[ChartTypeStr, str] = {
    "bar": _regular_schema(),
    "line": _regular_schema(),
    "area": _regular_schema(),
    "pie": _regular_schema(),
    "doughnut": _regular_schema(),
    "scatter": _scatter_schema(),
}

_EXTRA_RULES: dict[ChartTypeStr, str] = {
    "bar": (
        "- 'bar' charts share the regular schema.\n"
        "- Every dataset becomes a separate bar series."
    ),
    "line": (
        "- 'line' charts share the regular schema.\n"
        "- Every dataset becomes a separate line series."
    ),
    "area": (
        "- 'area' charts share the regular schema.\n"
        "- Every dataset becomes a filled area series."
    ),
    "pie": (
        "- 'pie' charts share the regular schema but support only ONE dataset.\n"
        "- If multiple datasets are present, keep only the first one."
    ),
    "doughnut": (
        "- 'doughnut' charts share the regular schema but support only ONE dataset.\n"
        "- If multiple datasets are present, keep only the first one."
    ),
    "scatter": (
        "- 'scatter' charts do NOT use a top-level 'labels' field.\n"
        "- Each point must be an object with numeric 'x' and 'y' keys.\n"
        "- Convert any flat [x, y] arrays or {x, y} objects into the required shape."
    ),
}


def build_repair_prompt(chart_type: ChartTypeStr, input_json_text: str) -> tuple[str, str]:
    """Return (system_prompt, user_message) for the repair endpoint."""
    logger.info("repair_prompt.build chart_type=%s input_len=%d", chart_type, len(input_json_text))

    system = (
        "You are a JSON formatter. Your entire response must be a single valid JSON object. "
        "Do not include any text, markdown, code fences, explanations, apologies, or summaries."
    )

    user = (
        _REPAIR_PROMPT_TEMPLATE.replace("{{CHART_TYPE}}", chart_type)
        .replace("{{TARGET_SCHEMA}}", _TARGET_SCHEMAS[chart_type])
        .replace("{{EXTRA_RULES}}", _EXTRA_RULES[chart_type])
        .replace("{{INPUT_JSON}}", input_json_text)
    )

    return system, user
