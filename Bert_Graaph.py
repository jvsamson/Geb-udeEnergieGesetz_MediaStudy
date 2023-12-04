import pandas as pd
import matplotlib.pyplot as plt

# Load the sentiment analysis results
df = pd.read_csv('sentiment_distribution_by_affiliation.csv')

# Exclude 'Freie Wähler'
df = df[df['affiliation'] != 'Freie Wähler']

# Round the 'Percent of Texts' to whole numbers
df['Percent of Texts'] = df['Percent of Texts'].round(0).astype(int)

# Pivot the DataFrame for plotting
df_pivot = df.pivot(index='affiliation', columns='Sentiment', values='Percent of Texts')

# Create a stacked bar chart
ax = df_pivot.plot(kind='barh', stacked=True, color={'positive': 'green', 'neutral': 'grey', 'negative': 'red'}, figsize=(10, 8))

plt.title('Sentiment Distribution by Affiliation - BERT-based')
plt.xlabel('Percent of Texts')
plt.ylabel('Affiliation')

# Label the bars with white text and nudge the text to the right
for bars in ax.containers:
    labels = [f'{v}%' if v != 0 else '' for v in bars.datavalues]
    ax.bar_label(bars, labels=labels, label_type='center', color='white', padding=3)

# Invert the y-axis to have the first party at the top
plt.gca().invert_yaxis()

plt.legend(title='Sentiment')

# Save the plot as a PNG file
plt.savefig('stacked_barplot_sentiment_by_affiliation.png', bbox_inches='tight')

# Display the plot
plt.show()
