import re

import numpy as np


def sigmoid_transform(scores):
    return 1 / (1 + np.exp(-scores))


def clean_text_conservative(text):
    """
    Conservative text cleaning that preserves more content
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs but keep other content
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Keep numbers but remove standalone numeric strings longer than 4 digits
    text = re.sub(r'\b\d{5,}\b', '', text)  # Remove long numbers like phone numbers

    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove excessive punctuation but keep some structure
    text = re.sub(r'[^\w\s\.\!\?\,\-]', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)  # Multiple dots to single
    text = re.sub(r'\!{2,}', '!', text)  # Multiple exclamations to single

    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()

    return text
