import numpy as np
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from transformers import DistilBertTokenizer, DistilBertModel
import torch

from classifier.utils import clean_text_conservative, sigmoid_transform

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load pre-trained DistilBERT tokenizer and model for embedding generation
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model_bert = DistilBertModel.from_pretrained('distilbert-base-uncased')
import os
model_path = os.path.join(os.path.dirname(__file__), 'scam_detector_distilbert_model.pkl')
scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
model_svm = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Function to get [CLS] embedding for a description
def get_cls_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model_bert(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return cls_embedding[0]


# Function to predict scam probability with custom normalization
def predict_scam_probability(text):
    # Preprocess the input description
    processed_text = clean_text_conservative(text)
    if not processed_text:
        return 0.0, False

    # Generate DistilBERT embedding
    text_vector = get_cls_embedding(processed_text)
    # If a scaler was used in training, apply it
    text_vector_scaled = scaler.transform([text_vector])

    # Get the score from the model
    decision_score = model_svm.decision_function(text_vector_scaled)[0]

    prob_like_score = sigmoid_transform(decision_score)
    is_scam = prob_like_score > 0.5

    return prob_like_score, is_scam


# Example usage (Note: X_train is not available here; this is a placeholder)
if __name__ == "__main__":
    test_description = "Claim your free prize now, just pay a small fee!"
    score = predict_scam_probability(test_description)
    print(f"Scam Probability: {score:.4f}")