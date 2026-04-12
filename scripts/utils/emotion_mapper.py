import yaml
import os

def load_emotion_config():
    """
    Loads universal emotion mapping configurations.
    """
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'emotion_tag_map.yaml'))
    
    if not os.path.exists(config_path):
        return {
            "happy": "[laughter]",
            "sad": "[sigh]",
            "angry": "[dissatisfaction-hnn]",
            "surprised": "[surprise-ah]"
        }
        
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def apply_emotion_tag(text: str, detected_emotion: str) -> str:
    """
    Maps an NLP emotion string (like 'joy') dynamically onto the specific 
    acoustic tags the OmniVoice model dictates inside the YAML config to
    drastically impact the synthesized output realism.
    """
    mapping = load_emotion_config()
    
    # NLP translations mapping (HuggingFace tags to Config definitions)
    if detected_emotion in ['joy', 'happy']:
        prefix = mapping.get('happy', '')
    elif detected_emotion in ['sadness', 'sad']:
        prefix = mapping.get('sad', '')
    elif detected_emotion in ['anger', 'angry']:
        prefix = mapping.get('angry', '')
    elif detected_emotion in ['surprise', 'surprised']:
        prefix = mapping.get('surprised', '')
    else:
        prefix = mapping.get('neutral', '')
        
    return f"{prefix} {text}".strip()
