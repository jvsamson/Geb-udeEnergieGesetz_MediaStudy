import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Get the directory of the current script
script_directory = os.path.dirname(__file__)

# Change the current working directory to the script directory
os.chdir(script_directory)

# Loading the dataframe
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
    certainty, sentiment = torch.max(predictions, dim=-1)
    sentiment_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
    return sentiment_mapping[sentiment.item()], certainty.item()

# Apply sentiment analysis to the 'Subtitle' column and extract sentiment and certainty
df_processed[['Sentiment', 'Certainty']] = df_processed['Subtitle'].apply(
    lambda x: pd.Series(sentiment_score(x))
)

# Filter out rows with less than 7 words in 'Subtitle'
df_filtered = df_processed[df_processed['Subtitle'].str.split().str.len() > 6]

# Group by 'Affiliation' and 'Sentiment' and calculate the percentage of each sentiment
sentiment_counts = df_processed.groupby(['affiliation', 'Sentiment']).size()
sentiment_distribution = sentiment_counts.to_frame(name='Counts').reset_index()

# Calculate the percentage of each sentiment within each affiliation
sentiment_distribution['Percent of Texts'] = sentiment_distribution.groupby('affiliation')['Counts'] \
    .transform(lambda x: 100 * x / float(x.sum()))

# Drop the 'Counts' column as it's no longer needed
sentiment_distribution = sentiment_distribution.drop(columns='Counts')

# Save this to a CSV file
sentiment_distribution.to_csv('sentiment_distribution_by_affiliation.csv', index=False)

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

# First, exclude the 'Freie Wähler' affiliation
sentiment_distribution = sentiment_distribution[sentiment_distribution['affiliation'] != 'Freie Wähler']

# Pivot the DataFrame for plotting
df_pivot = sentiment_distribution.pivot(index='affiliation', columns='Sentiment', values='Percent of Texts')

# Sort the DataFrame to ensure that the bars are in a meaningful order (optional)
df_pivot = df_pivot.sort_index()

# Plot a stacked bar chart
ax = df_pivot.plot(kind='bar', stacked=True, color={'positive': 'green', 'neutral': 'grey', 'negative': 'red'}, figsize=(10, 8))

plt.title('Sentiment Distribution by Affiliation')
plt.xlabel('Percent of Texts')
plt.ylabel('Affiliation')

# Add labels inside the bars
for bars in ax.containers:
    ax.bar_label(bars, fmt='%.2f%%', label_type='center')

# Invert the y-axis to have the first party at the top
plt.gca().invert_yaxis()

plt.legend(title='Sentiment')

# Save the plot as a PNG file
plt.savefig('stacked_barplot_sentiment_by_affiliation.png', bbox_inches='tight')

# Display the plot
plt.show()