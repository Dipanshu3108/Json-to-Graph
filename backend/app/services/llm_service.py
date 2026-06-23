import os
import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "1"))
RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "0.6"))

# Number of characters from prompts/responses to include in log lines.
LOG_PREVIEW_CHARS = int(os.getenv("LLM_LOG_PREVIEW_CHARS", "150"))

MODELS = {
    "anthropic": os.getenv("LLM_MODEL_ANTHROPIC", "claude-sonnet-4-6"),
    "openai": os.getenv("LLM_MODEL_OPENAI", "gpt-4o-mini"),
    "gemini": os.getenv("LLM_MODEL_GEMINI", "gemini-3.5-flash"),
    "ollama": os.getenv("LLM_MODEL_OLLAMA", "deepseek-coder:latest"),
}


class LLMServiceError(RuntimeError):
    """Raised when the configured LLM provider cannot return a usable response."""


def _trunc(text: str, limit: int = LOG_PREVIEW_CHARS) -> str:
    """Return a truncated preview of *text* for logging."""
    if len(text) <= limit:
        return text
    return text[:limit]


async def complete(system: str, user: str) -> str:
    """Send system + user prompt to the configured LLM provider."""
    model = MODELS.get(PROVIDER, PROVIDER)
    logger.info(
        "llm.complete.start provider=%s model=%s prompt_len=%d user_len=%d "
        "system_head=%s user_head=%s",
        PROVIDER,
        model,
        len(system),
        len(user),
        _trunc(system),
        _trunc(user),
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            if PROVIDER == "anthropic":
                result = await _call_anthropic(system, user)
            elif PROVIDER == "openai":
                result = await _call_openai(system, user)
            elif PROVIDER == "gemini":
                result = await _call_gemini(system, user)
            elif PROVIDER == "ollama":
                result = await _call_ollama(system, user)
            else:
                raise LLMServiceError(f"Unknown LLM_PROVIDER: {PROVIDER!r}")

            logger.info(
                "llm.complete.success provider=%s model=%s response_len=%d "
                "response_head=%s",
                PROVIDER,
                model,
                len(result),
                _trunc(result),
            )
            return result
        except KeyError as exc:
            logger.error("llm.complete.error provider=%s error=missing_env_key key=%s", PROVIDER, exc.args[0])
            raise LLMServiceError(f"Missing required environment variable: {exc.args[0]}") from exc
        except httpx.TimeoutException as exc:
            logger.warning("llm.complete.timeout provider=%s attempt=%d", PROVIDER, attempt)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError(
                f"LLM request timed out after {TIMEOUT:.0f}s (provider={PROVIDER})."
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "llm.complete.http_error provider=%s status=%s response=%s",
                PROVIDER,
                exc.response.status_code,
                exc.response.text[:200],
            )
            raise LLMServiceError(
                f"LLM provider returned HTTP {exc.response.status_code} (provider={PROVIDER})."
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("llm.complete.network_error provider=%s attempt=%d error=%s", PROVIDER, attempt, exc)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError(
                f"LLM network error while contacting provider={PROVIDER}."
            ) from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.error("llm.complete.parse_error provider=%s error=%s", PROVIDER, exc)
            raise LLMServiceError(
                f"LLM returned an unexpected response format (provider={PROVIDER})."
            ) from exc

    raise LLMServiceError(f"LLM request failed after {MAX_RETRIES + 1} attempts (provider={PROVIDER}).")


async def _call_anthropic(system: str, user: str) -> str:
    model = MODELS["anthropic"]
    logger.info("llm.anthropic.call model=%s", model)
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 2048,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]


async def _call_openai(system: str, user: str) -> str:
    model = MODELS["openai"]
    logger.info("llm.openai.call model=%s", model)
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 2048,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def _call_gemini(system: str, user: str) -> str:
    model = MODELS["gemini"]
    logger.info("llm.gemini.call model=%s", model)
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={os.environ['GEMINI_API_KEY']}"
    )
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            url,
            json={
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system}\n\n{user}"}]}
                ]
            },
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


async def _call_ollama(system: str, user: str) -> str:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = MODELS["ollama"]
    logger.info(
        "llm.ollama.call system_head=%s user_head=%s",
        _trunc(system),
        _trunc(user),
    )
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            f"{base}/api/chat",
            headers=headers,
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
