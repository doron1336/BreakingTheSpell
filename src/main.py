from typing import Tuple

import gradio as gr

from classifier.main import predict_scam_probability
from src.prompts import (
    INITIAL_GREETING_PROMPT,
    FOLLOW_UP_PROMPT,
    HIGH_RISK_RESPONSE_PROMPT,
    LOW_RISK_RESPONSE_PROMPT
)

# Predefined set of scam types (aligned with SCAM_DETECTION_PROMPT)
SCAM_TYPES = ['Employment', 'Online Purchase', 'Sweepstakes/Lottery/Prizes', 'Investment', 'Other', 'Phishing',
              'Travel/Vacation/Timeshare', 'Advance Fee Loan', 'Counterfeit Product', 'CryptoCurrency', 'Charity',
              'Debt Collections', 'Home Improvement', 'Worthless Problem-solving Service', 'Tech Support',
              'Impersonation Scam', 'Retail Business', 'Tax Collection', 'Retail/Brand Impersonation',
              'Fake Invoice/Supplier Bill', 'Bank/Credit Card Company Imposter', 'Identity Theft',
              'Credit Repair/Debt Relief', 'Credit Cards', 'Government Agency Imposter', 'Healthcare/Medicaid/Medicare',
              'Romance', 'Yellow Pages/Directories', 'Fake Check/Money Order', 'Advance-Fee/419 Scams', 'Utility',
              'Government Impersonation', 'Government Grant', 'Financial Scam', 'Rental', 'Family/Friend Emergency',
              'Foreign Money Exchange']


def classify_scam_type(description: str) -> Tuple[float, str]:
    """
    Classify the scam type and assign a confidence score based on keyword matches.
    Follows the logic defined in SCAM_DETECTION_PROMPT.
    Returns a tuple of (score, scam_type).
    """
    desc_lower = description.lower()
    max_score = 0.0
    detected_type = "unknown"

    # Calculate score for each scam type based on keyword matches
    for scam_type, keywords in SCAM_TYPES.items():
        matches = sum(1 for keyword in keywords if keyword in desc_lower)
        score = (matches / len(keywords)) * 100  # Percentage of matched keywords
        if score > max_score:
            max_score = score
            detected_type = scam_type

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
    Process user message, predict scam probability, and respond using prompts from prompts.py.
    Follows SYSTEM_PROMPT (guiding implementation), INITIAL_GREETING_PROMPT,
    FOLLOW_UP_PROMPT, HIGH_RISK_RESPONSE_PROMPT, and LOW_RISK_RESPONSE_PROMPT.
    """
    # Handle empty or vague input
    if not message.strip():
        return INITIAL_GREETING_PROMPT
    if len(message.strip()) < 20:  # Arbitrary threshold for vague input
        return FOLLOW_UP_PROMPT

    # Predict scam probability and type using the trained model
    is_scam, scam_type = predict_scam_probability(message)

    if is_scam:
        # Format HIGH_RISK_RESPONSE_PROMPT with specific scam type
        scam_explanation = f"{scam_type.replace('_', ' ')} scams often trick people into sending money or sharing personal details under false pretenses"
        response = HIGH_RISK_RESPONSE_PROMPT.format(
            score=0,  # Score not used, kept for prompt compatibility
            scam_type=scam_type.replace('_', ' ').title(),
            explain_tactic_briefly=scam_explanation
        )
    else:
        # Format LOW_RISK_RESPONSE_PROMPT
        response = LOW_RISK_RESPONSE_PROMPT.format(score=0)

    return response


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
