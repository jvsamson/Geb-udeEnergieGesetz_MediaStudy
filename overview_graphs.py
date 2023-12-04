from fuzzywuzzy import process
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# Read the CSV file
df = pd.read_csv('df_processed.csv')

# Function to replace names based on fuzzy matching
def unify_names(name, choices, threshold=90):
    # Check if the name is a string
    if not isinstance(name, str):
        return name  # Return the original value if it's not a string

    highest = process.extractOne(name, choices)
    if highest[1] >= threshold:
        return highest[0]
    return name


# Unique names as the choices for matching
unique_names = df['Speaker Name'].unique()

# Applying the function to each name
df['Unified Name'] = df['Speaker Name'].apply(lambda x: unify_names(x, unique_names))

# Calculate word count in 'Segment Description'
df['Word Count'] = df['Segment Description'].apply(lambda x: len(str(x).split()))

# Convert 'Date' to datetime and sort
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)

# Group data by speaker, date, and affiliation, and sum the word counts
grouped_df = df.groupby(['Unified Name', 'Date', 'affiliation']).agg({'Word Count': 'sum'}).reset_index()

# Group data by week
grouped_df['Week'] = grouped_df['Date'].dt.isocalendar().week

# Map party names to distinct colors
party_colors = {
    'green': 'green',
    'cdu': 'black',
    'spd': 'red',
    'fdp': 'yellow',
    'linke': 'purple',
    'afd': 'blue'
}

# Filter DataFrame for speakers who belong to one of the listed parties
grouped_df = grouped_df[grouped_df['affiliation'].isin(party_colors.keys())]

# Plotting
plt.figure(figsize=(12, 6))

# Loop through each party and plot
for party, color in party_colors.items():
    party_data = grouped_df[grouped_df['affiliation'] == party]
    plt.scatter(party_data['Week'], party_data['Word Count'], label=party, color=color, alpha=0.7)

plt.xlabel('Week')
plt.ylabel('Total Word Count')
plt.title('Total Word Count by Speaker, Week, and Party')
plt.legend()
plt.show()
