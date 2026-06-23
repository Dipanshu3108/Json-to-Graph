import logging

from fastapi import APIRouter

from ..schemas.chart import ValidateRequest, ValidateResponse
from ..services import normalizer, validator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/validate", response_model=ValidateResponse)
async def validate_chart(request: ValidateRequest) -> ValidateResponse:
    logger.info("validate.request chart_type=%s", request.chartType)
    normalized_raw = normalizer.normalize(request.data)
    result = validator.validate(request.chartType, normalized_raw)

    if result["valid"]:
        logger.info(
            "validate.success chart_type=%s normalized_keys=%s",
            request.chartType,
            sorted(result.get("normalizedData", {}).keys()),
        )
    else:
        logger.info(
            "validate.invalid chart_type=%s errors=%d",
            request.chartType,
            len(result["errors"]),
        )

    return ValidateResponse(
        valid=result["valid"],
        errors=result["errors"],
        normalizedData=result.get("normalizedData"),
    )
