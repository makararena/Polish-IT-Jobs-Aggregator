from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re
from transformers import MarianMTModel, MarianTokenizer
import torch

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Initialize the translation model and tokenizer for pl-en
model_name = 'Helsinki-NLP/opus-mt-pl-en'
device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU if available
model = MarianMTModel.from_pretrained(model_name).to(device)
tokenizer = MarianTokenizer.from_pretrained(model_name)

def detect_language(title):
    """Detect if the text is in Polish; otherwise, return 'en'."""
    try:
        # Check for Polish-specific characters
        polish_letters = re.search(r'[ąćęłńóśźż]', title)
        if polish_letters:
            return 'pl'
        detected_language = detect(title)
        return detected_language if detected_language == 'pl' else 'en'
    except LangDetectException:
        return 'en'
    except Exception as e:
        print(f"Error detecting language for '{title}': {e}")
        return 'en'

def translate_title(title, target_language='en'):
    """Translate a title from Polish to English using Helsinki-NLP/opus-mt-pl-en."""
    try:
        detected_language = detect_language(title)
        if detected_language == 'pl' and target_language == 'en':
            inputs = tokenizer(title, return_tensors="pt", padding=True).to(device)
            translated = model.generate(**inputs)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            return translated_text
        else:
            return title  # No translation needed if text is not in Polish
    except Exception as e:
        print(f"Error translating title '{title}': {e}")
        return title