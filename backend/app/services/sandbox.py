"""
Light sanitisation for LLM-generated HTML before iframe injection.
This is not a full XSS defence. The iframe sandbox remains primary.
"""

import re

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
    for pattern in _BLOCKED_PATTERNS:
        html = re.sub(pattern, "/* blocked */", html, flags=re.IGNORECASE)
    return html
