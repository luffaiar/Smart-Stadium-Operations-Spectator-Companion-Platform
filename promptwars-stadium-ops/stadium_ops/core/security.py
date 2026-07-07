"""Security safeguards, inputs sanitization, and audit logging utilities.

This module provides tools to detect and log prompt injection attempts,
sanitize inputs against XSS scripts, enforce input length caps, and verify
session-based rate limits.
"""

import re
import datetime
import time
import logging
from typing import List
from stadium_ops.core.exceptions import SecurityValidationError

logger = logging.getLogger(__name__)

# Enforce maximum text limits to prevent prompt bloating or heavy payloads
def enforce_length_limit(text: str, max_len: int = 500) -> str:
    """Checks input length and raises an exception if it exceeds the limit.

    Args:
        text: The user-supplied raw text.
        max_len: The maximum character count allowed.

    Returns:
        The verified text.

    Raises:
        SecurityValidationError: If input length exceeds the maximum cap.
    """
    if text and len(text) > max_len:
        raise SecurityValidationError(
            f"Input size ({len(text)} characters) exceeds the security cap of {max_len} characters."
        )
    return text or ""


# Simple HTML sanitizer to prevent XSS script executions
def sanitize_input(text: str) -> str:
    """Removes HTML scripts, elements, and tags to sanitize raw user text.

    Args:
        text: The raw user-supplied query string.

    Returns:
        The sanitized string.
    """
    if not text:
        return ""
    # Strip script blocks and all enclosed contents completely
    text_no_scripts = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining HTML tags
    clean = re.compile('<.*?>')
    sanitized = re.sub(clean, '', text_no_scripts)
    return sanitized.strip()


# Audit logger to document security events
def log_security_violation(violation_type: str, raw_input: str, user_id: str = "Anonymous") -> None:
    """Logs details of a security violation into a local audit log file.

    Args:
        violation_type: Label of violation (e.g. PROMPT_INJECTION, XSS_ATTEMPT).
        raw_input: The blocked input text.
        user_id: Unique session identifier or IP tag.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] [WARNING] [SECURITY] Type: {violation_type} | "
        f"User: {user_id} | Input: '{raw_input}'\n"
    )
    try:
        with open("security_audit.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed writing security violation to audit log file: {e}")


# Check for typical prompt injection keywords or hijack attempts
def detect_prompt_injection(text: str, user_id: str = "Anonymous") -> bool:
    """Scans user input for prompt injection vectors.

    Logs a security violation block if any suspicious command hijack phrases are found.

    Args:
        text: The raw user input.
        user_id: Unique session identifier.

    Returns:
        True if prompt injection patterns are matched, False otherwise.
    """
    if not text:
        return False
        
    lower_text = text.lower()
    patterns = [
        r"ignore (all )?previous instructions",
        r"system prompt",
        r"jailbreak",
        r"you are now a(n)?",
        r"forget what you were told",
        r"bypass safety",
        r"dan mode",
        r"do anything now",
        r"act as",
        r"new rule:"
    ]
    
    for pattern in patterns:
        if re.search(pattern, lower_text):
            log_security_violation("PROMPT_INJECTION", text, user_id)
            return True
            
    return False


# Session-based request rate limiter check
def is_rate_limited(request_timestamps: List[float], limit: int = 15, period: float = 60.0) -> bool:
    """Checks if the rolling request count exceeds the limit.

    Args:
        request_timestamps: List of timestamps representing recent user requests.
        limit: Max requests allowed inside the period window.
        period: Window duration in seconds.

    Returns:
        True if the rate limit is exceeded, False otherwise.
    """
    now = time.time()
    # Filter out timestamps older than the evaluation window
    active_timestamps = [t for t in request_timestamps if now - t < period]
    
    if len(active_timestamps) >= limit:
        return True
    return False
