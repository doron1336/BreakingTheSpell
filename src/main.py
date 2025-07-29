from typing import Tuple

import gradio as gr

from classifier.main import predict_scam_probability
from src.gpt import classify_scam_with_azure_config
from src.prompts import (
    INITIAL_GREETING_PROMPT,
    FOLLOW_UP_PROMPT,
    HIGH_RISK_RESPONSE_PROMPT,
    LOW_RISK_RESPONSE_PROMPT
)
from src.utils import sanitize_input, llm_settings


def classify_scam_type(description: str) -> Tuple[float, str]:
    """
    Classify the scam type and assign a confidence score based on keyword matches.
    Follows the logic defined in SCAM_DETECTION_PROMPT.
    Returns a tuple of (score, scam_type).
    """
    desc_lower = description.lower()
    max_score = 0.0
    detected_type = "unknown"

    # Additional heuristics from SCAM_DETECTION_PROMPT
    if len(description) < 50:  # Short descriptions are more suspicious
        max_score += 10.0
    if "!" in description or "..." in description:
        max_score += 10.0

    # Cap score at 100
    max_score = min(max_score, 100.0)
    return max_score, detected_type


def chatbot_response(message: str, history: list) -> str:
    """
    Process user message, predict scam probability, classify scam type, and respond using prompts from prompts.py.
    Follows SYSTEM_PROMPT (guiding implementation), INITIAL_GREETING_PROMPT,
    FOLLOW_UP_PROMPT, SCAM_DETECTION_PROMPT, HIGH_RISK_RESPONSE_PROMPT, and LOW_RISK_RESPONSE_PROMPT.
    """
    # Handle empty or vague input
    if not message.strip():
        return INITIAL_GREETING_PROMPT
    if len(message.strip()) < 20:  # Arbitrary threshold for vague input
        return FOLLOW_UP_PROMPT

    try:
        # Sanitize input to prevent prompt injection
        is_valid, result = sanitize_input(message)
        if not is_valid:
            return f"Error: {result}"

        # Predict scam probability
        prob_like_score, is_scam = predict_scam_probability(result)

        if is_scam:
            # Initialize LLM settings for Azure OpenAI
            # Classify scam type using Azure OpenAI
            try:
                classification_result = classify_scam_with_azure_config(
                    description=result,
                    api_key=llm_settings.AZURE_OPENAI_KEY,
                    endpoint=llm_settings.AZURE_OPENAI_ENDPOINT,
                    deployment_id=llm_settings.AZURE_MODEL_IMAGE_DEPLOYMENT_ID,
                    api_version=llm_settings.OPENAI_API_VERSION
                )

                # Extract scam type and additional info from classification
                scam_type = classification_result.get('scam_type', 'Other')
                confidence_score = classification_result.get('confidence_score', 0)
                reasoning = classification_result.get('reasoning', '')

                # Check if there was an error in classification
                if classification_result.get('error', False):
                    scam_type = 'Other'  # Fallback to 'Other' if classification failed

            except Exception as classification_error:
                # Fallback to original classification method if Azure call fails
                print(f"Azure classification failed: {str(classification_error)}")
                scam_type = classify_scam_type(result) if hasattr(globals(), 'classify_scam_type') else 'Other'
                confidence_score = 0
                reasoning = "Classification via backup method due to Azure API issue"

            # Format the high-risk response with enhanced information
            response = HIGH_RISK_RESPONSE_PROMPT.format(
                score=prob_like_score,  # Include probability score for user transparency
                scam_type=scam_type.replace('_', ' ').title(),
                explain_tactic_briefly=reasoning
            )

            # Optionally add confidence and reasoning info if available
            if confidence_score > 0:
                response += f"\n\n**Classification Confidence:** {confidence_score}%"
            if reasoning and len(reasoning) > 10:  # Only add if reasoning is substantial
                response += f"\n**Analysis:** {reasoning[:200]}{'...' if len(reasoning) > 200 else ''}"

        else:
            response = LOW_RISK_RESPONSE_PROMPT.format(score=prob_like_score)

        return response

    except Exception as e:
        # Handle unexpected errors (e.g., model failure)
        return f"Error: Unable to process your request due to an issue ({str(e)}). Please try again with a valid description."


# Gradio interface
def main():
    interface = gr.ChatInterface(
        fn=chatbot_response,
        title="Money Transfer Scam Detector",
        description=(
            "I'm a friendly bot designed to protect you from scams. Describe any money transfer request "
            "you've received, and I'll analyze it to identify potential risks and advise you."
        ),
        theme="soft",
        examples=[
            "Someone emailed me saying I won $1,000,000 and need to send $500 to claim it.",
            "My friend asked me to send $200 via PayPal for an emergency.",
            "A person claiming to be a prince needs my bank account to transfer millions."
        ]
    )
    interface.launch()


if __name__ == "__main__":
    main()
