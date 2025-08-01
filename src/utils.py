import re
from typing import Tuple

from src.prompts import PROMPT_INJECTION_PATTERNS
from src.secret_manager import SecretManagerCaller
from html import escape

SecretManager = SecretManagerCaller()


class LLMSettings:
    AZURE_OPENAI_KEY: str = SecretManager('OPENAI_API_4O_SECRET_NAME', extra_arg_key='api-key')
    AZURE_OPENAI_ENDPOINT: str = "https://lqc-gpt-4o.openai.azure.com/"
    AZURE_MODEL_IMAGE_DEPLOYMENT_ID: str = "lqc-4o"
    OPENAI_API_VERSION: str = "2024-08-01-preview"
    OPENAI_MODEL: str = "gpt-4o"
    LIQUIDITY_ENDPOINT: str = "https://lqc-server-gateway.liquidity-capital.com/graphql"
    NEZILUT_JS_API_PATH: str = ''
    FETCH_GRAPHQL_EMAIL_ADDRESS: str = ""
    FETCH_GRAPHQL_PASSWORD: str = ""

llm_settings = LLMSettings()

def sanitize_input(description: str) -> Tuple[bool, str]:
    """
    Sanitize and validate user input to prevent prompt injection.
    Returns (is_valid, sanitized_description_or_error_message).
    """
    # Strip whitespace and limit input length
    description = description.strip()
    if len(description) > 1000:
        return False, "Input is too long. Please provide a description under 1000 characters."
    if not description:
        return False, "Please provide a non-empty description."

    # Escape HTML characters to prevent XSS or formatting issues
    sanitized = escape(description)

    # Check for prompt injection patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            return False, "Input contains suspicious content that could disrupt the system. Please provide a valid description of the money transfer request."

    return True, sanitized

