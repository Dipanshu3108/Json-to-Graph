import json
import logging
from pathlib import Path

from fastapi import APIRouter

from ..schemas.chart import RepairRequest, RepairResponse
from ..services import llm_service, validator

router = APIRouter()
logger = logging.getLogger(__name__)

REPAIR_PROMPT = (Path(__file__).parent.parent / "prompts" / "repair_schema.txt").read_text(
    encoding="utf-8"
)


@router.post("/api/repair", response_model=RepairResponse)
async def repair_chart(request: RepairRequest) -> RepairResponse:
    logger.info(
        "repair.request chart_type=%s payload_type=%s",
        request.chartType,
        type(request.data).__name__,
    )

    if isinstance(request.data, str):
        input_json_text = request.data
    else:
        input_json_text = json.dumps(request.data, indent=2)

    user_message = (
        f"CHART TYPE: {request.chartType}\n\n"
        f"INPUT JSON:\n{input_json_text}"
    )

    try:
        raw_response = await llm_service.complete(system=REPAIR_PROMPT, user=user_message)
    except llm_service.LLMServiceError as exc:
        logger.warning("repair.llm_unavailable chart_type=%s error=%s", request.chartType, exc)
        return RepairResponse(fixed=False, error=f"LLM unavailable: {exc}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("repair.llm_unexpected_error chart_type=%s", request.chartType)
        return RepairResponse(fixed=False, error=f"LLM unavailable: {exc}")

    changes: list[str] = []
    json_text = raw_response
    if "CHANGES:" in raw_response:
        parts = raw_response.split("CHANGES:", 1)
        json_text = parts[0].strip()
        changes = [item.strip() for item in parts[1].strip().split(",") if item.strip()]

    try:
        repaired_data = json.loads(json_text)
    except json.JSONDecodeError:
        logger.warning("repair.invalid_json chart_type=%s", request.chartType)
        return RepairResponse(fixed=False, error="LLM returned unparseable JSON.", changes=[])

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
    )
