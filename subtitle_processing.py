import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import spacy
import os

# Get the directory of the current script
script_directory = os.path.dirname(__file__)

# Change the current working directory to the script directory
os.chdir(script_directory)

# Now the current working directory is set to where the script is located
# You can verify by printing the current working directory again
print("Current working directory:", os.getcwd())

# Load the dataframe from a file in the current working directory
df_cleaned = pd.read_csv('cleaned_data_final.csv')

# Check the updated DataFrame
print(df_cleaned.head())

df_cleaned.to_csv('df_cleaned_final_test.csv')



# Download stopwords from NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Load the spaCy language model for German
nlp = spacy.load("de_core_news_sm")

# Initialize the NLTK Porter Stemmer
stemmer = PorterStemmer()

# Function to preprocess text
def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove punctuation except for periods
    text = text.translate(str.maketrans('', '', string.punctuation.replace('.', '')))
    
    # Tokenize text using spaCy for lemmatization
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc]
    
    # Remove stopwords
    stop_words = set(stopwords.words('german'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Apply stemming using NLTK's Porter Stemmer (optional, since lemmatization is also used)
    stemmed_tokens = [stemmer.stem(token) for token in tokens]  # You can comment this out if needed
    
    # Rejoin tokens into a string, keeping periods as they are
    return ' '.join(stemmed_tokens)  # Use tokens instead of stemmed_tokens if stemming is not desired


# Apply the preprocessing to the 'subtitles' column and add a new column 'df_processed'
df_cleaned['Processed'] = df_cleaned['Subtitle'].apply(preprocess_text)

# Save the dataframe to a new CSV file if needed
df_cleaned.to_csv('df_processed.csv', index=False)

# Print the first few rows of the specified columns from df_cleaned
print(df_cleaned[['Content Type', 'Speaker Name', 'Subtitle', 'Processed']].head())

# Assuming df_cleaned has a 'Content Type' column after processing
df_o_tone = df_cleaned.loc[df_cleaned['Content Type'] == 'O-Ton'].copy()
df_o_tone = df_o_tone.drop(columns=['Segment Description'])
df_o_tone.to_csv('df_o_tones.csv')
# You can now work with df_o_tone which contains only the entries with Content Type as "O-Tone"
