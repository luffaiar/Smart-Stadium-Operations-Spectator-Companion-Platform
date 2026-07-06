import re

# Simple HTML sanitizer to prevent XSS in text rendering
def sanitize_input(text: str) -> str:
    if not text:
        return ""
    # Remove script tags and their content completely to prevent XSS execution
    text_no_scripts = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining HTML tags
    clean = re.compile('<.*?>')
    sanitized = re.sub(clean, '', text_no_scripts)
    return sanitized.strip()

# Check for typical prompt injection keywords or hijack attempts
def detect_prompt_injection(text: str) -> bool:
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
            return True
            
    return False
