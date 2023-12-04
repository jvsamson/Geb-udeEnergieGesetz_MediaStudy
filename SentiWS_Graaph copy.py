import pandas as pd
import spacy
import matplotlib.pyplot as plt


# Load your DataFrame
df = pd.read_csv('normalized_sentiment_ws.csv')

# Rename the second column to 'Average Sentiment Score' for clarity
df.columns = ['affiliation', 'Average Sentiment Score']

# Sort the DataFrame by 'Average Sentiment Score' in descending order
df = df.sort_values('Average Sentiment Score', ascending=False)


# Exclude 'Freie Wähler' affiliation
df = df[df['affiliation'] != 'Freie Wähler']

# Create a dictionary to map party names to distinct colors
party_colors = {
    'Die Grünen': 'green',
    'CDU/CSU': 'black',
    'SPD': 'red',
    'FDP': 'yellow',
    'Die Linke': 'purple',
    'AFD': 'blue',
    'Expert': '#30D5C8',
    'ARD': 'grey'  # Assuming ARD is another party, assign a color
}

# Plotting the horizontal bar chart
plt.figure(figsize=(10, 6))
for index, row in df.iterrows():
    plt.barh(row['affiliation'], row['Average Sentiment Score'], color=party_colors.get(row['affiliation'], 'gray'))

plt.xlabel('Average Sentiment Score')
plt.ylabel('Affiliation')
plt.title('Sentiment Analysis by Affiliation - SentiWS')
plt.tight_layout()  # Adjust layout to make room for y labels
plt.show()

# Save the plot as a PNG file
plt.savefig('SentiWS Bar Plot.PNG', bbox_inches='tight')

# Display the plot
plt.show()