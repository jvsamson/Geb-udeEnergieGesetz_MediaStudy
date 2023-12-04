import pandas as pd
from nltk.tokenize import word_tokenize
# Load your DataFrame
df = pd.read_csv('df_processed.csv')

# Load your DataFrame (assuming it's already loaded as df_cleaned)
# df_cleaned = pd.read_csv('your_dataframe.csv')

# Filter the DataFrame for rows with Content Type as "O-Tone"
o_tone_df = df[df['Content Type'] == 'O-Ton']



# Initialize an empty set to store unique words that start with "Heiz"
heiz_words = set()

# Iterate through the filtered DataFrame
for text in o_tone_df['Subtitle']:
    # Tokenize the text
    tokens = word_tokenize(text)
    # Add words that start with "Heiz" to the set
    for word in tokens:
        if word.startswith('Heiz') or word.startswith('heiz'):
            heiz_words.add(word)


relevant_words = set()
# Iterate through the filtered DataFrame
for text in o_tone_df['Subtitle']:
    # Tokenize the text
    tokens = word_tokenize(text)
    # Add words that contain "verbot" or "chaos" to the set
    for word in tokens:
        if 'verbot' in word.lower() or 'chaos' in word.lower() or 'streit' in word.lower() or 'konflikt' in word.lower() or 'krise' in word.lower():
            relevant_words.add(word)



import pandas as pd

# Load the dataset
df = pd.read_csv('df_processed.csv')

# Filter rows where Content Type is 'O-ton'
filtered_df = df[df['Content Type'] == 'O-Ton']

# Define your words to count
words_to_count = ['Verbotsgesetz', 'Koalitionskonflikt', 'Dauerstreit', 'Heizungsverbotsgesetz',
                  'Chaoswende', 'Ampel-Streit', 'Heizungsstreit', 'Verbotspartei', 'Heizungshammer']

# Function to count occurrences of a specific word
def count_specific_word(text, word):
    return text.lower().count(word.lower())

# Initialize an empty dictionary to hold the word counts
word_count_by_affiliation = {word: [] for word in words_to_count}

# Count each word separately by affiliation
for word in words_to_count:
    word_count_by_affiliation[word] = filtered_df.groupby('affiliation')['Subtitle'].apply(
        lambda x: sum(x.apply(lambda y: count_specific_word(y, word)))
    )

# Create a DataFrame for the word counts
word_count_df = pd.DataFrame(word_count_by_affiliation)

# Print the word counts by affiliation
print("Individual Word Counts by Affiliation:")
print(word_count_df)

# Calculate normalized counts
total_words = filtered_df.groupby('affiliation')['Subtitle'].apply(
    lambda x: sum(len(y.split()) for y in x)
)
normalized_counts = word_count_df.sum(axis=1) / total_words

# Count the number of unique speakers by affiliation
speaker_counts = filtered_df.groupby('affiliation')['Speaker Name'].nunique()

# Combine all counts into a single DataFrame
result_df = pd.DataFrame({
    'Normalized Count': normalized_counts,
    'Total Word Count': total_words,
    'Speaker Count': speaker_counts
})

# Print the final result DataFrame with overall counts
print("\nFinal Result DataFrame with Overall Counts:")
print(result_df)

