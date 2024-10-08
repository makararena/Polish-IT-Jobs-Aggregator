from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re
from transformers import MarianMTModel, MarianTokenizer
import torch

torch.cuda.empty_cache()
DetectorFactory.seed = 0

model_name = 'Helsinki-NLP/opus-mt-pl-en'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = MarianMTModel.from_pretrained(model_name).to(device)
tokenizer = MarianTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)

def detect_language(title):
    """Detect if the text is in Polish; otherwise, return 'en'."""
    try:
        if re.search(r'[ąćęłńóśźż]', title):
            return 'pl'
        detected_language = detect(title)
        return detected_language if detected_language == 'pl' else 'en'
    except LangDetectException:
        return 'en'
    except Exception as e:
        print(f"Error detecting language for '{title}': {e}")
        return 'en'

def translate_title(title):
    """Translate a single title from Polish to English if necessary."""
    try:
        detected_language = detect_language(title)
        if detected_language == 'pl':
            inputs = tokenizer(title, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            return translated_text
        else:
            return title
    except Exception as e:
        print(f"Error translating title '{title}': {e}")
        return title