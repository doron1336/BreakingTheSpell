import nltk
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
import torch
from transformers import DistilBertTokenizer, DistilBertModel
import numpy as np
from classifier.parse_csv import load_and_prepare_data
from classifier.utils import clean_text_conservative, sigmoid_transform
import joblib


# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

CSV_PATH = '/data/scams_sample.csv'
description_column = "description"
descriptions, labels = load_and_prepare_data(CSV_PATH, description_column=description_column,
                                             num_synthetic_samples=1000)
#
# Load pre-trained DistilBERT tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# # Function to get [CLS] embedding for a description
def get_cls_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()  # Corrected to last_hidden_state
    return cls_embedding[0]  # Return the single vector
#
# # Preprocess all descriptions
processed_descriptions = [clean_text_conservative(desc) for desc in descriptions]

# # Preprocess and create embeddings
X = np.array([get_cls_embedding(desc) for desc in processed_descriptions])
print("X shape:", X.shape)
print("Sample X row:", X[0])


# Train-test split (80-20)
X_train, X_test, _, _ = train_test_split(X, range(len(X)), test_size=0.2, random_state=42)

# Scale the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# For binary classification, try smaller nu values
param_grid = {
    'nu': [0.01, 0.02, 0.05, 0.1, 0.15, 0.2],
    'gamma': [0.001, 0.01, 0.1, 1, 10, 'scale', 'auto']
}

best_score = -np.inf
best_params = None

for nu in param_grid['nu']:
    for gamma in param_grid['gamma']:
        model_svm = OneClassSVM(nu=nu, gamma=gamma, kernel='rbf')
        model_svm.fit(X_train_scaled)

        # Use decision function for better discrimination
        scores = model_svm.decision_function(X_test)
        score_range = scores.max() - scores.min()

        if score_range > best_score:
            best_score = score_range
            best_params = {'nu': nu, 'gamma': gamma}
            # Save model
            joblib.dump(model_svm, 'scam_detector_distilbert_model.pkl')
            joblib.dump(scaler, 'scaler.pkl')

print(f"Best params: {best_params}")


# Function to predict scam probability with custom normalization
def predict_scam_probability(text):
    # Load the saved model (assume it's pre-trained without PCA)
    model_svm = joblib.load('scam_detector_distilbert_model.pkl')
    scaler = joblib.load('scaler.pkl')  # Uncomment if scaler was used

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


# Get decision scores (signed distances)
decision_test_scores = model_svm.decision_function(X_test)

# Use 0 as threshold (this is what predict() uses internally)
threshold = 0

# Or if you want 0/1 labels instead of 1/-1:
predicted_labels = [1 if score >= threshold else 0 for score in decision_test_scores]

true_labels = [1] * len(X_test)
from sklearn.metrics import precision_recall_fscore_support
precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predicted_labels, average='binary')
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")

# Example usage
test_prompt = "Claim your free prize now, just pay a small fee!"
probability, is_scam = predict_scam_probability(test_prompt)
print(f"Scam Probability: {probability:.4f}, Is Scam: {is_scam}")
