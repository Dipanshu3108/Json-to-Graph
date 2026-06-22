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
    logger.info(
        "validate.result chart_type=%s valid=%s errors=%d",
        request.chartType,
        result["valid"],
        len(result["errors"]),
    )
    return ValidateResponse(
        valid=result["valid"],
        errors=result["errors"],
        normalizedData=result.get("normalizedData"),
    )
