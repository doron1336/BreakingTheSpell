import json
import re
from typing import Dict, Any

import openai

from src.utils import llm_settings

# Your scam types list
SCAM_TYPES = [
    'Employment', 'Online Purchase', 'Sweepstakes/Lottery/Prizes', 'Investment', 'Other', 'Phishing',
    'Travel/Vacation/Timeshare', 'Advance Fee Loan', 'Counterfeit Product', 'CryptoCurrency', 'Charity',
    'Debt Collections', 'Home Improvement', 'Worthless Problem-solving Service', 'Tech Support',
    'Impersonation Scam', 'Retail Business', 'Tax Collection', 'Retail/Brand Impersonation',
    'Fake Invoice/Supplier Bill', 'Bank/Credit Card Company Imposter', 'Identity Theft',
    'Credit Repair/Debt Relief', 'Credit Cards', 'Government Agency Imposter', 'Healthcare/Medicaid/Medicare',
    'Romance', 'Yellow Pages/Directories', 'Fake Check/Money Order', 'Advance-Fee/419 Scams', 'Utility',
    'Government Impersonation', 'Government Grant', 'Financial Scam', 'Rental', 'Family/Friend Emergency',
    'Foreign Money Exchange'
]


def classify_scam_with_azure_config(
        description: str,
        api_key: str,
        endpoint: str,
        deployment_id: str,
        api_version: str = "2024-08-01-preview",
        temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Alternative function that accepts Azure OpenAI settings directly.

    Args:
        description (str): The scam description to classify
        api_key (str): Azure OpenAI API key
        endpoint (str): Azure OpenAI endpoint
        deployment_id (str): Azure model deployment ID
        api_version (str): API version
        temperature (float): Temperature for GPT response

    Returns:
        Dict containing:
        - scam_type: The classified scam type
        - confidence_score: Score from 0-100
        - reasoning: Explanation of the classification
        - risk_level: Low/Medium/High based on confidence
        - key_indicators: List of key words/phrases that led to classification
        - error: Boolean indicating if an error occurred
    """
    # Initialize Azure OpenAI client
    client = openai.AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

    # Create the prompt
    scam_types_str = ", ".join(SCAM_TYPES)

    prompt = f"""
    You are a scam detection expert. Analyze the following description and classify it into one of these scam types:

    SCAM TYPES: {scam_types_str}

    Your task:
    1. Read the description carefully
    2. Identify key indicators that match specific scam types
    3. Choose the MOST APPROPRIATE scam type from the list above
    4. Provide a confidence score (0-100) where:
       - 0-30: Low confidence/unclear
       - 31-70: Medium confidence  
       - 71-100: High confidence
    5. Explain your reasoning

    IMPORTANT RULES:
    - You MUST choose from the provided scam types list only
    - If uncertain between multiple types, choose the most specific/relevant one
    - If it doesn't clearly fit any category, use "Other"
    - Be conservative with high confidence scores (80+) - only use for very clear cases

    Description to analyze: "{description}"

    Respond in this exact JSON format:
    {{
        "scam_type": "[chosen scam type from the list]",
        "confidence_score": [number 0-100],
        "reasoning": "[detailed explanation of why you chose this classification]",
        "key_indicators": ["list", "of", "key", "words", "or", "phrases", "that", "led", "to", "classification"]
    }}
    """

    try:
        # Make API call to Azure OpenAI
        response = client.chat.completions.create(
            model=deployment_id,
            messages=[
                {"role": "system",
                 "content": "You are an expert scam detection system. Always respond with valid JSON in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=500
        )

        # Parse the response
        response_text = response.choices[0].message.content.strip()

        try:
            # Remove any markdown formatting if present
            json_text = re.sub(r'```json\n?|```\n?', '', response_text)
            result = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: try to find JSON within the text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from GPT response")

        # Validate the response
        if not all(key in result for key in ["scam_type", "confidence_score", "reasoning"]):
            raise ValueError("Missing required fields in GPT response")

        # Ensure scam_type is in our list
        if result["scam_type"] not in SCAM_TYPES:
            result["scam_type"] = "Other"

        # Ensure confidence score is in valid range
        result["confidence_score"] = max(0, min(100, int(result["confidence_score"])))

        # Add risk level based on confidence
        if result["confidence_score"] >= 71:
            risk_level = "High"
        elif result["confidence_score"] >= 31:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        result["risk_level"] = risk_level
        result["error"] = False

        return result

    except Exception as e:
        # Return error response
        return {
            "scam_type": "Other",
            "confidence_score": 0,
            "reasoning": f"Error occurred during classification: {str(e)}",
            "risk_level": "Low",
            "key_indicators": [],
            "error": True
        }


# Example usage
def example_usage():
    """
    Example of how to use the function with your LLMSettings
    """
    # Your Azure OpenAI settings (replace with actual values)

    description = "Someone called claiming to be from the bank asking for my account password to verify my identity"

    result = classify_scam_with_azure_config(
        description=description,
        api_key=llm_settings.AZURE_OPENAI_KEY,
        endpoint=llm_settings.AZURE_OPENAI_ENDPOINT,
        deployment_id=llm_settings.AZURE_MODEL_IMAGE_DEPLOYMENT_ID,
        api_version=llm_settings.OPENAI_API_VERSION
    )

    print("Classification Results:")
    print(f"Scam Type: {result['scam_type']}")
    print(f"Confidence: {result['confidence_score']}%")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Key Indicators: {result.get('key_indicators', [])}")
    print(f"Error: {result['error']}")

    return result
