#!/usr/bin/env python3
import logging
from typing import Optional
from google.cloud import translate_v2 as translate

logger = logging.getLogger(__name__)

class DeepTranslator:
    """
    High-fidelity translation wrapper using Google Cloud Translation.
    Designed to provide '100% real original' deeply translated text.
    """
    def __init__(self, api_key: Optional[str] = None):
        # If api_key is provided, it uses it; otherwise relies on GOOGLE_APPLICATION_CREDENTIALS
        if api_key:
            import os
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key
        
        try:
            self.client = translate.Client()
        except Exception as e:
            logger.error(f"Failed to initialize Google Translate Client: {e}")
            self.client = None

    def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """
        Translates text to the target language.
        
        Args:
            text: The text to translate.
            target_lang: ISO 639-1 language code (e.g., 'en', 'zh').
            source_lang: Optional source language code.
            
        Returns:
            The translated text string.
        """
        if not self.client:
            logger.warning("Translate client not initialized. Returning original text.")
            return text
        
        if not text or not text.strip():
            return text

        try:
            result = self.client.translate(
                text, 
                target_language=target_lang, 
                source_language=source_lang
            )
            return result['translatedText']
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

# Singleton instance for easy access across the project
translator = DeepTranslator()
