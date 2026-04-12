import os
import sys
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from omnivoice.models.omnivoice import OmniVoice

class ModelLoader:
    _omnivoice_model = None

    @classmethod
    def get_omnivoice(cls):
        if cls._omnivoice_model is None:
            print("[ModelLoader] Loading OmniVoice model globally into memory...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._omnivoice_model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=device, dtype=torch.float16)
        return cls._omnivoice_model

# Singleton exporter
get_omnivoice = ModelLoader.get_omnivoice
