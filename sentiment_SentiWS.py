import pandas as pd
import spacy

# Function to load SentiWS data
def load_sentiws(file_path):
    senti_dict = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            word_info, score = parts[0], parts[1]
            words = word_info.split('|')[0].split(',')
            words.extend(word_info.split('|')[-1].split(','))
            for word in words:
                senti_dict[word.strip()] = float(score)
    return senti_dict

# Load SentiWS positive and negative lexicons
positive_words = load_sentiws('./SentiWS_v2/SentiWS_v2.0_Positive.txt')
negative_words = load_sentiws('./SentiWS_v2/SentiWS_v2.0_Negative.txt')

# Load the German spaCy model
nlp = spacy.load('de_core_news_sm')

# Function to preprocess and tokenize text
def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc]
    return tokens

# Function to calculate sentiment score
def sentiment_score(text):
    tokens = preprocess_text(text)
    score = 0
    for token in tokens:
        score += positive_words.get(token, 0)
        score -= negative_words.get(token, 0)  # Subtracting negative scores
    return score

# Load your DataFrame
df = pd.read_csv('df_processed.csv')

# Apply the sentiment scoring function
df['Sentiment_Score'] = df['Subtitle'].apply(sentiment_score)

# Classify each statement as positive, negative, or neutral
df['Sentiment_Class'] = df['Sentiment_Score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

# Group by 'affiliation' and sum the sentiment scores
grouped_sum = df.groupby('affiliation')['Sentiment_Score'].sum()

# Count the number of contributions (text entries) per affiliation
grouped_count = df.groupby('affiliation')['Subtitle'].count()

# Normalize the sentiment scores
normalized_sentiment = grouped_sum / grouped_count



import pandas as pd
from nltk.tokenize import word_tokenize

# Load your DataFrame (assuming it's already loaded as df_cleaned)
# df_cleaned = pd.read_csv('your_dataframe.csv')




# Filter for negatively scored statements
negative_statements = df[df['Sentiment_Score'] < 0]

# Count the number of positive and negative statements by affiliation
sentiment_counts = df.groupby('affiliation')['Sentiment_Class'].value_counts().unstack(fill_value=0)

# Output the results
print("Normalized Sentiment Scores by Affiliation:\n", normalized_sentiment)
print("\nNegatively Scored Statements:\n", negative_statements[['Subtitle', 'Sentiment_Score']])
print("\nCount of Positive, Negative, and Neutral Statements by Affiliation:\n", sentiment_counts)

normalized_sentiment.to_csv('normalized_sentiment_ws.csv')

