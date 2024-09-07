from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import argostranslate.package
import argostranslate.translate

# Set seed for consistent language detection
DetectorFactory.seed = 0

def detect_language(title):
    """Detect if the text is English or Polish; otherwise, return 'unknown'."""
    try:
        detected_language = detect(title)
        if detected_language == 'pl':
            return detected_language
        else:
            return 'en'
    except LangDetectException:
        return 'en'
    except Exception as e:
        print(f"Error detecting language for '{title}': {e}")
        return 'en'

def setup_translation_package(from_code, to_code):
    """Download and install the Argos Translate package."""
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code),
        None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
    else:
        raise ValueError(f"No translation package available for {from_code} to {to_code}")

def translate_title(title, target_language='en'):
    """Translate a title using Argos Translate with language detection."""
    try:
        # Detect the language of the title
        detected_language = detect_language(title)
        # Translate the title if it's not already in the target language
        if detected_language == 'pl' and target_language == 'en':
            setup_translation_package('pl', 'en')
            translated_text = argostranslate.translate.translate(title, 'pl', 'en')
            return translated_text
        else:
            return title  # Return the original if the detected language is the same as the target
        
    except Exception as e:
        print(f"Error translating title '{title}': {e}")
        return title  # Return the original title if translation fails
