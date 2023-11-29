import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import spacy


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
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize text using spaCy for lemmatization
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc]
    
    # Remove stopwords
    stop_words = set(stopwords.words('german'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Apply stemming using NLTK's Porter Stemmer
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    return ' '.join(stemmed_tokens)


# load dataframe with all texts
df_cleaned = pd.read_csv(file_path)