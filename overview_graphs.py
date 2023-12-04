import pandas as pd
import matplotlib.pyplot as plt

# Load the DataFrame
df = pd.read_csv('df_processed.csv')

# Exclude 'Freie Wähler' and 'ARD' affiliations
df = df[(df['affiliation'] != 'Freie Wähler') & (df['affiliation'] != 'ARD')]

# Ensure 'Date' is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Calculate the total number of words for each 'Subtitle'
df['Word_Count'] = df['Subtitle'].str.split().str.len()

# Group by 'Date' and 'affiliation', then sum the word counts
daily_words_by_affiliation = df.groupby(['Date', 'affiliation']).agg({'Word_Count':'sum'}).reset_index()

# Define colors for each affiliation
party_colors = {
    'Die Grünen': 'green',
    'CDU/CSU': 'black',
    'SPD': 'red',
    'FDP': 'yellow',
    'Die Linke': 'purple',
    'AFD': 'blue',
    'Expert': '#30D5C8'
    # 'ARD': 'grey' (Excluded as per the updated requirement)
}

# Count the number of occurrences for each affiliation
affiliation_counts = daily_words_by_affiliation['affiliation'].value_counts()

# Plotting the contributions per day by affiliation as dots
plt.figure(figsize=(15, 7))
for affiliation, group_df in daily_words_by_affiliation.groupby('affiliation'):
    plt.scatter(group_df['Date'], group_df['Word_Count'], label=f"{affiliation} ({affiliation_counts[affiliation]})", color=party_colors.get(affiliation, 'grey'))

plt.xlabel('Date')
plt.ylabel('Total Words Spoken')
plt.title('Contributions by Affiliation')
plt.legend(title='Affiliation', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
