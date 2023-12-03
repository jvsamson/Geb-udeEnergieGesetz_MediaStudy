import pandas as pd

# Function to load SentiWS into a dictionary
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
sentiws_pos = load_sentiws('./SentiWS_v2/SentiWS_v2.0_Positive.txt')
sentiws_neg = load_sentiws('./SentiWS_v2/SentiWS_v2.0_Negative.txt')

# Load the processed DataFrame
df_processed = pd.read_csv('df_processed.csv')

# Function to calculate sentiment score
def sentiment_score(text):
    # Ensure that text is a string
    if not isinstance(text, str):
        return 0
    tokens = text.split()
    score = 0
    for token in tokens:
        if token in sentiws_pos:
            score += sentiws_pos[token]
        elif token in sentiws_neg:
            score += sentiws_neg[token]
    return score

# Apply the sentiment analysis
df_processed['Sentiment_Score'] = df_processed['Subtitle'].apply(sentiment_score)

# Save or analyze the results
df_processed.to_csv('df_sentiment_analysis.csv', index=False)

# Optionally, print the first few rows to check
print(df_processed.head())
