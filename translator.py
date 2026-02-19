"""
Translation module using Rapid Translate Multi Traduction API
Translates article titles from Spanish to English
"""
import requests
from config import TRANSLATION_API_URL


class Translator:
    """Translation class using MyMemory API (free tier)"""
    
    def __init__(self):
        self.api_url = TRANSLATION_API_URL
        self.source_lang = "es"  # Spanish
        self.target_lang = "en"  # English
    
    def translate_text(self, text):
        """
        Translate text from Spanish to English
        
        Args:
            text: Text to translate
            
        Returns:
            str: Translated text
        """
        if not text:
            return ""
        
        try:
            params = {
                "q": text,
                "langpair": f"{self.source_lang}|{self.target_lang}"
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("responseStatus") == 200:
                    translated_text = data.get("responseData", {}).get("translatedText", "")
                    return translated_text
                else:
                    print(f"API error: {data.get('responseDetails', 'Unknown error')}")
            else:
                print(f"HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"Translation error: {e}")
        
        return text  # Return original text if translation fails
    
    def translate_titles(self, titles):
        """
        Translate a list of titles
        
        Args:
            titles: List of article titles in Spanish
            
        Returns:
            list: List of translated titles in English
        """
        print(f"\n{'='*60}")
        print("TRANSLATING ARTICLE TITLES")
        print(f"{'='*60}\n")
        
        translated_titles = []
        
        for i, title in enumerate(titles):
            print(f"Original (Spanish): {title}")
            
            translated = self.translate_text(title)
            
            print(f"Translated (English): {translated}")
            print("-" * 40)
            
            translated_titles.append(translated)
        
        return translated_titles


def translate_with_google_api(text, api_key):
    """
    Alternative: Translate using Google Translate API
    
    Args:
        text: Text to translate
        api_key: Google Translate API key
        
    Returns:
        str: Translated text
    """
    from google.cloud import translate_v2 as translate
    
    try:
        translate_client = translate.Client()
        
        result = translate_client.translate(
            text,
            source_language="es",
            target_language="en"
        )
        
        return result["translatedText"]
    except Exception as e:
        print(f"Google Translate API error: {e}")
        return text


if __name__ == "__main__":
    # Test the translator
    translator = Translator()
    
    test_titles = [
        "La economía española crece más de lo esperado",
        "El gobierno presenta nuevo plan de infraestructura",
        "Los expertos warn sobre el cambio climático",
        "Nueva tecnología revoluciona el mercado",
        "El turismo en España alcanza cifras récord"
    ]
    
    translated = translator.translate_titles(test_titles)
    
    print(f"\n{'='*60}")
    print("TRANSLATED TITLES")
    print(f"{'='*60}\n")
    
    for i, title in enumerate(translated):
        print(f"{i+1}. {title}")
