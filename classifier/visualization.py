import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re

# Download NLTK resources (run once)
nltk.download('punkt')
nltk.download('stopwords')

# Load the dataset
df = pd.read_csv('/data/scams_sample.csv')  # Replace with your CSV file path
df['is_scam'] = df['scam_type'].apply(lambda x: 'not_scam' if x == 'not_scam' else 'scam')

# 2. Distribution of Scam Types (Multiclass Perspective)
plt.figure(figsize=(10, 6))
sns.countplot(y='scam_type', data=df, order=df['scam_type'].value_counts().index)
plt.title('Distribution of Scam Types')
plt.xlabel('Count')
plt.ylabel('Scam Type')
plt.savefig('scam_type_distribution.png')
plt.close()

# 3. Description Length Analysis
df['desc_length'] = df['description'].apply(lambda x: len(str(x).split()))
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='desc_length', hue='is_scam', bins=50, kde=True)
plt.title('Distribution of Description Lengths by Scam/Non-Scam')
plt.xlabel('Number of Words')
plt.ylabel('Frequency')
plt.savefig('desc_length_distribution.png')
plt.close()

# 4. Word Cloud for Scam and Non-Scam Descriptions
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Separate scam and non-scam descriptions
scam_texts = ' '.join(df[df['is_scam'] == 'scam']['description'].apply(clean_text))
non_scam_texts = ' '.join(df[df['is_scam'] == 'not_scam']['description'].apply(clean_text))


# 5. N-gram Analysis (Top 10 bigrams for scam and non-scam)
def get_ngrams(text, n=2):
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [' '.join(ngram) for ngram in ngrams]

scam_ngrams = get_ngrams(scam_texts, n=2)

scam_ngram_counts = Counter(scam_ngrams).most_common(10)

# Plot top bigrams
plt.figure(figsize=(10, 6))
sns.barplot(x=[count for _, count in scam_ngram_counts], y=[ngram for ngram, _ in scam_ngram_counts])
plt.title('Top 10 Bigrams in Scam Descriptions')
plt.xlabel('Frequency')
plt.ylabel('Bigram')
plt.savefig('scam_bigrams.png')
plt.close()


# Print summary statistics
print("Dataset Summary:")
print(f"Total samples: {len(df)}")
print(f"Scam samples: {len(df[df['is_scam'] == 'scam'])}")
print(f"Non-scam samples: {len(df[df['is_scam'] == 'not_scam'])}")
print("\nScam Type Distribution:")
print(df['scam_type'].value_counts())
print("\nAverage Description Length (words):")
print(df.groupby('is_scam')['desc_length'].mean())