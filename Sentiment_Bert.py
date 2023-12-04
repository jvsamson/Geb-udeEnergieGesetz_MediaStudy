import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os

# Get the directory of the current script
script_directory = os.path.dirname(__file__)

# Change the current working directory to the script directory
os.chdir(script_directory)

# Loading the data.frame
df_processed = pd.read_csv('df_processed.csv')

# Load tokenizer and model from Hugging Face
model_name = "oliverguhr/german-sentiment-bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def sentiment_score(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    # Sentiments are ordered as [negative, neutral, positive]
    certainty, sentiment = torch.max(predictions, dim=-1)
    # Mapping numerical results to sentiment labels
    sentiment_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
    return sentiment_mapping[sentiment.item()], certainty.item()

# Apply sentiment analysis to the 'Subtitle' column and extract sentiment and certainty
df_processed[['Sentiment', 'Certainty']] = df_processed['Subtitle'].apply(
    lambda x: pd.Series(sentiment_score(x))
)

# ...

# Filter out rows with less than 7 words in 'Subtitle'
df_filtered = df_processed[df_processed['Subtitle'].str.split().str.len() > 6]

# Selecting top 15 entries with the highest certainty for each sentiment within each affiliation
top_entries = pd.DataFrame()
for affiliation in df_filtered['affiliation'].unique():
    for sentiment in ['negative', 'neutral', 'positive']:
        is_affiliation = df_filtered['affiliation'] == affiliation
        is_sentiment = df_filtered['Sentiment'] == sentiment
        filtered = df_filtered[is_affiliation & is_sentiment]
        top_entries = pd.concat([
            top_entries,
            filtered.nlargest(15, 'Certainty')
        ])

# Save to CSV
top_entries.to_csv('top_certainty_by_affiliation.csv', index=False)