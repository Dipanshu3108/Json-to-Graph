"""
Light sanitisation for LLM-generated HTML before iframe injection.
This is not a full XSS defence. The iframe sandbox remains primary.
"""

import logging
import re

logger = logging.getLogger(__name__)

_BLOCKED_PATTERNS = [
    r"<iframe[^>]*src\s*=\s*['\"](?!https://cdnjs\.cloudflare\.com)[^'\"]+['\"][^>]*>",
    r"window\.parent",
    r"window\.top",
    r"document\.cookie",
    r"localStorage",
    r"sessionStorage",
    r"fetch\(",
    r"XMLHttpRequest",
]


def sanitise(html: str) -> str:
    logger.info("sandbox.sanitise.start len=%d", len(html))
    blocked_hits = 0
    for pattern in _BLOCKED_PATTERNS:
        matches = re.findall(pattern, html, flags=re.IGNORECASE)
        if matches:
            blocked_hits += len(matches)
            html = re.sub(pattern, "/* blocked */", html, flags=re.IGNORECASE)
    logger.info(
        "sandbox.sanitise.finish len_after=%d blocked_hits=%d",
        len(html),
        blocked_hits,
    )
    return html
