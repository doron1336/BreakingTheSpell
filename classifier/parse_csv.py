import pandas as pd

from classifier.process import generate_synthetic_not_scam


# Load and parse CSV, combine with synthetic data
def load_and_prepare_data(file_path, description_column='description', num_synthetic_samples=None):
    # Load CSV
    df = pd.read_csv(file_path)
    if description_column not in df.columns:
        raise ValueError(f"Column '{description_column}' not found in CSV. Available columns: {df.columns}")

    # Extract scam descriptions and assign label 1
    scam_descriptions = df[description_column]

    scam_labels = [1] * len(scam_descriptions)

    # Print sample data for clarity
    print("Sample Data Structure:")
    for desc, label in list(zip(scam_descriptions, scam_labels))[:3]:
        print(f"Description: {desc[:50]}... | Label: {'Scam' if label == 1 else 'Not Scam'}")

    return scam_descriptions, scam_labels


if __name__ == "__main__":
    CSV_PATH = '/Users/doron/Desktop/personal/BreakingTheSpell/classifier/data/scams_sample.csv'
    description_column = "description"
    load_and_prepare_data(CSV_PATH, description_column=description_column, num_synthetic_samples=1000)
