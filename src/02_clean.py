"""Clean raw review data into a normalized JSONL dataset."""

from __future__ import annotations

import pandas as pd
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from num2words import num2words


FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "had", "has", "have", "he", "her", "hers", "him", "his", "i",
    "if", "in", "into", "is", "it", "its", "me", "my", "of", "on", "or",
    "our", "ours", "she", "so", "that", "the", "their", "them", "they",
    "this", "to", "us", "was", "we", "were", "with", "you", "your", "yours",
}


def ensure_nltk_resource(resource_path, download_name):
    try:
        nltk.data.find(resource_path)
        return True
    except LookupError:
        return False


HAS_STOPWORDS = ensure_nltk_resource("corpora/stopwords", "stopwords")
HAS_WORDNET = ensure_nltk_resource("corpora/wordnet", "wordnet")
ensure_nltk_resource("corpora/omw-1.4", "omw-1.4")

STOP_WORDS = set(stopwords.words("english")) if HAS_STOPWORDS else FALLBACK_STOPWORDS
LEMMATIZER = WordNetLemmatizer() if HAS_WORDNET else None

def clean_text(text):
    if not text:
        return ""

    # 1. Convert to lowercase
    text = text.lower()

    # 2. Remove special characters, emojis, and punctuation
    # This regex keeps letters and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # 3. Convert numbers to text
    words = []
    for word in text.split():
        if word.isdigit():
            try:
                words.append(num2words(int(word)))
            except Exception:
                words.append(word)
        else:
            words.append(word)
    text = " ".join(words)

    # 4. Remove stop words and lemmatize when resources are available
    tokens = text.split()
    cleaned_tokens = []
    for token in tokens:
        if token in STOP_WORDS:
            continue
        cleaned_tokens.append(LEMMATIZER.lemmatize(token) if LEMMATIZER else token)

    # 5. Remove extra whitespace
    return " ".join(cleaned_tokens).strip()

def run_cleaning():
    # Load raw data
    reviews_list = []
    with open('data/reviews_raw.jsonl', 'r') as f:
        for line in f:
            reviews_list.append(json.loads(line))
    
    df = pd.DataFrame(reviews_list)
    
    # Remove duplicates based on review content
    df = df.drop_duplicates(subset=['content'])
    
    # Apply cleaning
    df['cleaned_content'] = df['content'].apply(clean_text)
    
    # Remove empty entries and extremely short reviews (less than 3 words)
    df = df[df['cleaned_content'].str.strip() != ""]
    df = df[df['cleaned_content'].str.split().str.len() > 2]
    
    # Save cleaned data
    df.to_json('data/reviews_clean.jsonl', orient='records', lines=True)
    print(f"Cleaning complete. {len(df)} records remaining.")
    if not HAS_STOPWORDS or not HAS_WORDNET:
        print("[clean] Used fallback NLP resources because NLTK downloads were unavailable.")
    return len(df)

if __name__ == "__main__":
    run_cleaning()
