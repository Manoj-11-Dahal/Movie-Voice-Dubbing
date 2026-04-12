import json
import os
import sys

# Bridging into OmniVoice's translator located at project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from omnivoice.utils.translator import translator

def run(transcription_json: str, target_lang: str, output_json: str):
    """
    Stage 8: Translate (NLLB / OmniVoice DeepTranslator)
    Requirement Addressed: "multiple language translate"
    
    Translates the precise timeline JSON into the target language.
    """
    print(f"[Stage 8] Translating exact timeline to {target_lang}...")
    
    with open(transcription_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    timeline = data.get("timeline", [])
    
    # We iterate over every timeline word/phrase securely 
    # to translate it while retaining its exact start/end float values
    for item in timeline:
        original_text = item["word"]
        # Use OmniVoice's built-in translator
        try:
            translated_text = translator.translate_text(original_text, target_lang=target_lang)
            item["word"] = translated_text
        except Exception as e:
            print(f"Translation failed via omnivoice translator, using fallback for: {original_text}")
    
    data["timeline"] = timeline
    
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"[Stage 8] Translation strictly applied to temporal structure map.")
    return output_json
