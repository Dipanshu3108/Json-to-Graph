import json
import logging
from pathlib import Path

from fastapi import APIRouter

from ..schemas.chart import GenerateCodeRequest, GenerateCodeResponse
from ..services import llm_service, sandbox

router = APIRouter()
logger = logging.getLogger(__name__)

GENERATE_PROMPT_TEMPLATE = (
    Path(__file__).parent.parent / "prompts" / "generate_chart_code.txt"
).read_text(encoding="utf-8")


def _error_html(message: str) -> str:
    safe_message = message.replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<!doctype html><html><head><meta charset='utf-8'/>"
        "<title>Generation Failed</title>"
        "<style>body{font-family:Segoe UI,sans-serif;padding:24px;background:#fff7ed;color:#9a3412;}"
        "h2{margin:0 0 8px 0;}pre{white-space:pre-wrap;background:#fff;border:1px solid #fdba74;"
        "padding:12px;border-radius:8px;}</style></head><body>"
        "<h2>Could not generate chart HTML</h2><pre>"
        f"{safe_message}"
        "</pre></body></html>"
    )


@router.post("/api/generate-code", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest) -> GenerateCodeResponse:
    logger.info(
        "generate_code.request chart_type=%s theme=%s payload_type=%s",
        request.chartType,
        request.theme or "default",
        type(request.data).__name__,
    )

    if isinstance(request.data, str):
        data_for_prompt = request.data
    else:
        data_for_prompt = json.dumps(request.data, indent=2)

    prompt = (
        GENERATE_PROMPT_TEMPLATE.replace("{{CHART_TYPE}}", request.chartType)
        .replace("{{THEME}}", request.theme or "default")
        .replace("{{DATA_JSON}}", data_for_prompt)
    )

    try:
        raw_html = await llm_service.complete(system=prompt, user="Generate the chart now.")
    except llm_service.LLMServiceError as exc:
        message = f"LLM unavailable: {exc}"
        logger.warning(
            "generate_code.llm_unavailable chart_type=%s error=%s",
            request.chartType,
            exc,
        )
        return GenerateCodeResponse(code=_error_html(message), error=message)
    except Exception as exc:  # noqa: BLE001
        message = f"LLM unavailable: {exc}"
        logger.exception("generate_code.llm_unexpected_error chart_type=%s", request.chartType)
        return GenerateCodeResponse(code=_error_html(message), error=message)

    clean_html = raw_html.strip()
    if clean_html.startswith("```"):
        clean_html = "\n".join(clean_html.split("\n")[1:])
    if clean_html.endswith("```"):
        clean_html = "\n".join(clean_html.split("\n")[:-1])
    clean_html = clean_html.strip()

    if not clean_html:
        message = "LLM returned empty content."
        logger.warning("generate_code.empty_output chart_type=%s", request.chartType)
        return GenerateCodeResponse(code=_error_html(message), error=message)

    sanitised = sandbox.sanitise(clean_html)
    if not sanitised.strip():
        message = "Generated HTML was blocked or became empty after sanitization."
        logger.warning("generate_code.sanitized_empty chart_type=%s", request.chartType)
        return GenerateCodeResponse(code=_error_html(message), error=message)

    logger.info(
        "generate_code.result chart_type=%s html_len=%d sanitized_len=%d",
        request.chartType,
        len(clean_html),
        len(sanitised),
    )

    return GenerateCodeResponse(code=sanitised)
