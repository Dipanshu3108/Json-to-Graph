import os
import asyncio

import httpx

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "1"))
RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "0.6"))

MODELS = {
    "anthropic": os.getenv("LLM_MODEL_ANTHROPIC", "claude-sonnet-4-6"),
    "openai": os.getenv("LLM_MODEL_OPENAI", "gpt-4o-mini"),
    "gemini": os.getenv("LLM_MODEL_GEMINI", "gemini-3.5-flash"),
    "ollama": os.getenv("LLM_MODEL_OLLAMA", "kimi-k2.7-code:cloud"),
}


class LLMServiceError(RuntimeError):
    """Raised when the configured LLM provider cannot return a usable response."""


async def complete(system: str, user: str) -> str:
    """Send system + user prompt to the configured LLM provider."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            if PROVIDER == "anthropic":
                return await _call_anthropic(system, user)
            if PROVIDER == "openai":
                return await _call_openai(system, user)
            if PROVIDER == "gemini":
                return await _call_gemini(system, user)
            if PROVIDER == "ollama":
                return await _call_ollama(system, user)
            raise LLMServiceError(f"Unknown LLM_PROVIDER: {PROVIDER!r}")
        except KeyError as exc:
            raise LLMServiceError(f"Missing required environment variable: {exc.args[0]}") from exc
        except httpx.TimeoutException as exc:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError(
                f"LLM request timed out after {TIMEOUT:.0f}s (provider={PROVIDER})."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMServiceError(
                f"LLM provider returned HTTP {exc.response.status_code} (provider={PROVIDER})."
            ) from exc
        except httpx.RequestError as exc:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise LLMServiceError(
                f"LLM network error while contacting provider={PROVIDER}."
            ) from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMServiceError(
                f"LLM returned an unexpected response format (provider={PROVIDER})."
            ) from exc


async def _call_anthropic(system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODELS["anthropic"],
                "max_tokens": 2048,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]


async def _call_openai(system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODELS["openai"],
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
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        response = await client.post(   
            f"{base}/api/chat",
            headers=headers,
            json={
                "model": MODELS["ollama"],
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
