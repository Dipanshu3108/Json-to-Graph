import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

API_KEY = os.getenv("KIMI_API_KEY", "")
BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
MODEL = os.getenv("LLM_MODEL_KIMI", "kimi-k2.6")
TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "1"))
RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "0.6"))

# Number of characters from prompts/responses to include in log lines.
LOG_PREVIEW_CHARS = int(os.getenv("LLM_LOG_PREVIEW_CHARS", "150"))


class LLMServiceError(RuntimeError):
    """Raised when the Kimi LLM cannot return a usable response."""


def _trunc(text: str, limit: int = LOG_PREVIEW_CHARS) -> str:
    """Return a truncated preview of *text* for logging."""
    if len(text) <= limit:
        return text
    return text[:limit]


async def complete(system: str, user: str) -> str:
    """Send system + user prompt to the Kimi LLM."""
    if not API_KEY:
        raise LLMServiceError("KIMI_API_KEY environment variable is not set.")

    logger.info(
        "llm.complete.start model=%s prompt_len=%d user_len=%d "
        "system_head=%s user_head=%s",
        MODEL,
        len(system),
        len(user),
        _trunc(system),
        _trunc(user),
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
                response = await client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                    },
                )
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"]

            logger.info(
                "llm.complete.success model=%s response_len=%d response_head=%s",
                MODEL,
                len(result),
                _trunc(result),
            )
            return result
        except KeyError as exc:
            logger.error("llm.complete.error error=missing_key key=%s", exc.args[0])
            raise LLMServiceError(f"Missing expected response key: {exc.args[0]}") from exc
        except httpx.TimeoutException as exc:
            logger.warning("llm.complete.timeout attempt=%d", attempt)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError(
                f"Kimi request timed out after {TIMEOUT:.0f}s."
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "llm.complete.http_error status=%s response=%s",
                exc.response.status_code,
                exc.response.text[:200],
            )
            raise LLMServiceError(
                f"Kimi returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("llm.complete.network_error attempt=%d error=%s", attempt, exc)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError("Kimi network error.") from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.error("llm.complete.parse_error error=%s", exc)
            raise LLMServiceError("Kimi returned an unexpected response format.") from exc

    raise LLMServiceError(f"Kimi request failed after {MAX_RETRIES + 1} attempts.")
