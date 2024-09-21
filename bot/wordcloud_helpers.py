import re
import os
import matplotlib.pyplot as plt
from nltk.util import ngrams
from nltk.corpus import stopwords
import swifter
import string
from nltk.tokenize import word_tokenize
import matplotlib.colors as mcolors
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

def remove_urls(x):
    cleaned_string = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', str(x), flags=re.MULTILINE)
    return cleaned_string

def deEmojify(x):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'', x)

def remove_symbols(x):
    cleaned_string = re.sub(r"[^a-zA-Z0-9]+", ' ', x)
    return cleaned_string 

def unify_whitespaces(x):
    cleaned_string = re.sub(' +', ' ', x)
    return cleaned_string 

# Function to clean and tokenize text
def clean_and_tokenize(text):
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    words = word_tokenize(text.lower())
    return [word for word in words if word not in stop_words and len(word) > 3]

# Function to extract bigrams
def extract_bigrams(tokens):
    return [' '.join(gram) for gram in ngrams(tokens, 2) if gram[0] != gram[1]]

def generate_wordcloud_from_tfidf(tfidf_scores, title, mode='white'):
    # Set background and colormap based on the mode
    if mode == 'black':
        background_color = 'black'
        colormap = 'inferno'  # Use a vibrant colormap for black background
    else:
        background_color = 'white'
        colormap = 'viridis'  # Use a vivid colormap for white background

    # Create a word cloud with the desired background color and colormap
    wordcloud = WordCloud(
        width=1920, 
        height=1080, 
        background_color=background_color,
    ).generate_from_frequencies(tfidf_scores)

    # Pick a color from the colormap for the title
    cmap = plt.get_cmap(colormap)
    title_color = mcolors.rgb2hex(cmap(0.85))  # Pick a vibrant shade for title

    # Set up the figure with title
    fig, ax = plt.subplots(figsize=(16, 9), facecolor=background_color)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    # Add the title to the figure
    plt.title(title, fontsize=40, color=title_color, pad=20, backgroundcolor=background_color)

    # Return both the figure and the wordcloud object
    return fig, wordcloud

# Function to generate TF-IDF scores
def generate_tfidf_model(texts):
    # Explicitly set token_pattern to None to suppress the warning
    vectorizer = TfidfVectorizer(tokenizer=clean_and_tokenize, ngram_range=(2, 2), token_pattern=None)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Filter out duplicate-word n-grams after vectorization
    tfidf_scores = dict(zip(feature_names, tfidf_matrix.sum(axis=0).A1))
    filtered_tfidf_scores = {key: value for key, value in tfidf_scores.items() if not any(
        word1 == word2 for word1, word2 in zip(key.split(), key.split()[1:])
    )}
    
    return filtered_tfidf_scores


def generate_advanced_wordcloud(df, column, folder_path, ngram_type='bigram', mode='white'):
    texts = df[column].dropna().astype(str).tolist()
    
    if ngram_type == 'bigram':
        tokenized_texts = [' '.join(extract_bigrams(clean_and_tokenize(text))) for text in texts]
    else:
        raise ValueError("Invalid ngram_type. Use 'bigram' or 'trigram'.")

    # Generate TF-IDF scores
    tfidf_scores = generate_tfidf_model(tokenized_texts)

    # Generate word cloud with the specified mode, and retrieve both figure and wordcloud
    fig, _ = generate_wordcloud_from_tfidf(tfidf_scores, title=f"{column} WordCloud", mode=mode)
    
    # Save word cloud image
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create folder if it doesn't exist

    file_path = os.path.join(folder_path, f'{column.lower()}_wordcloud.png')

    # Save the figure (which contains both the wordcloud and the title)
    fig.savefig(file_path, dpi=100, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free memory

    print(f"Word cloud saved to {file_path}")


