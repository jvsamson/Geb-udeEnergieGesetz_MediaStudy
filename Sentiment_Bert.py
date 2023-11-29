import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Loading the data.frame
df_processed = pd.read_csv('data/data_processed.csv')

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
    sentiment = predictions.argmax(dim=-1).item()
    # Mapping numerical results to sentiment labels
    sentiment_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
    return sentiment_mapping[sentiment]

# Apply sentiment analysis to the 'Text' column
df['Sentiment'] = df['Text'].apply(sentiment_score)

# Group by 'Speaker Type' and calculate sentiment distribution
speaker_type_sentiment = df.groupby('Speaker Type')['Sentiment'].value_counts(normalize=True)

# Group by 'Speaker Affiliation' and calculate sentiment distribution
speaker_affiliation_sentiment = df.groupby('Speaker Affiliation')['Sentiment'].value_counts(normalize=True)

print("Sentiment Distribution by Speaker Type:\n", speaker_type_sentiment)
print("\nSentiment Distribution by Speaker Affiliation:\n", speaker_affiliation_sentiment)
