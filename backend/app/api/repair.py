import json
import logging
import re

from fastapi import APIRouter

from ..schemas.chart import RepairRequest, RepairResponse
from ..services import llm_service, normalizer, validator
from ..services.repair_prompt import build_repair_prompt

router = APIRouter()
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str | None:
    """Best-effort extraction of a JSON object/array from model output.

    Strips markdown fences, trims surrounding prose, and returns the first
    JSON-looking substring. Returns ``None`` if no candidate is found.
    """
    # Remove markdown code fences (with or without language tag).
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    # Find the first { or [ and the matching last } or ].
    start_obj = cleaned.find("{")
    start_arr = cleaned.find("[")
    if start_obj == -1 and start_arr == -1:
        return None

    start = min(x for x in (start_obj, start_arr) if x != -1)

    end_obj = cleaned.rfind("}")
    end_arr = cleaned.rfind("]")
    end = max(end_obj, end_arr)

    if end == -1 or end < start:
        return None

    return cleaned[start : end + 1]



@router.post("/api/repair", response_model=RepairResponse)
async def repair_chart(request: RepairRequest) -> RepairResponse:
    logger.info(
        "repair.request chart_type=%s payload_type=%s",
        request.chartType,
        type(request.data).__name__,
    )

    if isinstance(request.data, str):
        input_json_text = request.data
        try:
            parsed_input = json.loads(request.data)
        except json.JSONDecodeError:
            parsed_input = None
    else:
        input_json_text = json.dumps(request.data, indent=2)
        parsed_input = request.data

    # Try rule-based normalization first; if it validates, skip the LLM entirely.
    if isinstance(parsed_input, dict):
        normalized = normalizer.normalize(parsed_input)
        rule_based_result = validator.validate(request.chartType, normalized)
        if rule_based_result["valid"]:
            logger.info(
                "repair.rule_based chart_type=%s changes=%d",
                request.chartType,
                len(rule_based_result.get("changes", [])),
            )
            return RepairResponse(
                fixed=True,
                normalizedData=rule_based_result["normalizedData"],
                changes=["normalized input to target schema"],
            )

    system_prompt, user_message = build_repair_prompt(request.chartType, input_json_text)

    try:
        raw_response = await llm_service.complete(system=system_prompt, user=user_message)
    except llm_service.LLMServiceError as exc:
        logger.warning("repair.llm_unavailable chart_type=%s error=%s", request.chartType, exc)
        return RepairResponse(fixed=False, error=f"LLM unavailable: {exc}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("repair.llm_unexpected_error chart_type=%s", request.chartType)
        return RepairResponse(fixed=False, error=f"LLM unavailable: {exc}")

    # Parse optional trailing sections. JSON should come first, then GENERATED:, then CHANGES:.
    changes_text = ""
    generated_text = ""
    remaining_text = raw_response

    if "CHANGES:" in remaining_text:
        parts = remaining_text.split("CHANGES:", 1)
        remaining_text = parts[0]
        changes_text = parts[1].strip()

    if "GENERATED:" in remaining_text:
        parts = remaining_text.split("GENERATED:", 1)
        remaining_text = parts[0]
        generated_text = parts[1].strip()

    extracted = _extract_json(remaining_text)
    if extracted is None:
        extracted = _extract_json(raw_response)

    if extracted is None:
        logger.warning(
            "repair.invalid_json chart_type=%s raw_head=%s",
            request.chartType,
            raw_response[:500],
        )
        return RepairResponse(fixed=False, error="LLM returned unparseable JSON.", changes=[])

    try:
        repaired_data = json.loads(extracted)
    except json.JSONDecodeError:
        logger.warning(
            "repair.invalid_json chart_type=%s extracted_head=%s raw_head=%s",
            request.chartType,
            extracted[:500],
            raw_response[:500],
        )
        return RepairResponse(fixed=False, error="LLM returned unparseable JSON.", changes=[])

    generated_data_points: list[str] = []
    if generated_text:
        for line in generated_text.splitlines():
            line = line.strip().lstrip("-").strip()
            if line:
                generated_data_points.append(line)

    changes: list[str] = []
    if changes_text:
        changes = [item.strip() for item in changes_text.split(",") if item.strip()]

    result = validator.validate(request.chartType, repaired_data)
    if not result["valid"]:
        logger.warning(
            "repair.validation_failed chart_type=%s errors=%d",
            request.chartType,
            len(result["errors"]),
        )
        return RepairResponse(
            fixed=False,
            error="Repaired JSON still failed validation.",
            changes=changes,
        )

    logger.info("repair.result chart_type=%s fixed=true changes=%d", request.chartType, len(changes))

    return RepairResponse(
        fixed=True,
        normalizedData=result["normalizedData"],
        changes=changes,
        generatedDataPoints=generated_data_points,
    )
