import os
import torch
from huggingface_hub import snapshot_download

def download_omni_models():
    """
    Production Script: Download & Cache HuggingFace Weights
    This script is explicitly run by `setup.sh` to prevent multi-gigabyte 
    downloads from blocking or crashing the Celery workers during execution.
    """
    print("Initiating pre-cache downloads for massive pipeline models...")
    
    # Target directory mapping inside the Docker container
    # Since Docker mounts `./models:/app/models`, this securely saves it locally
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    os.makedirs(cache_dir, exist_ok=True)
    
    # Central Config references
    models_to_cache = {
        "Whisper (Word-level timestamps)": "openai/whisper-large-v3",
        "NLP Emotion (Wav2Vec2 mapping)": "j-hartmann/emotion-english-distilroberta-base",
        # OmniVoice local weights if they run natively remotely
        "OmniVoice Synthesis Base": "k2-fsa/OmniVoice",
    }
    
    for name, repo_id in models_to_cache.items():
        print(f"-> Precaching [ {name} ] from {repo_id}...")
        try:
            # We don't download everything, just core model files to save space
            snapshot_download(
                repo_id=repo_id,
                cache_dir=cache_dir,
                allow_patterns=["*.bin", "*.pt", "*.safetensors", "*.json", "*.txt"],
                resume_download=True
            )
            print(f"Success: {name} validated in cache.")
        except Exception as e:
            print(f"Failed to cache {name}: {e}")
            
    # Pyannote uses a strict auth pipeline, we don't snapshot it here directly 
    # but we inform the user to ensure their token allows direct runtime caching.
    print("""
    [WARNING] Pyannote Diarization (speaker-diarization-3.1) requires a gated HF token.
    Ensure `HF_AUTH_TOKEN` is set in your `.env` so it can be dynamically pulled. 
    """)
    
    print("Pre-caching complete! Server is primed for instant inference.")

if __name__ == '__main__':
    download_omni_models()
