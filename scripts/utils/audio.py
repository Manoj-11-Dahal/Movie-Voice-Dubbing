import subprocess
import librosa
import os

def convert_to_24k_mono(input_path: str, output_path: str):
    """
    Strict Conversion utility ensuring audio streams conform
    to the exact 24000 Hz OmniVoice acoustic parameters.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", input_path, 
        "-vn", "-acodec", "pcm_s16le", 
        "-ar", "24000", "-ac", "1", output_path
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def validate_duration_identical(original_path: str, new_path: str) -> bool:
    """
    Mathematical fallback check verifying that the generated audio node's 
    time structure specifically matches the original bounds to a 0.05s tolerance.
    """
    dur_orig = librosa.get_duration(path=original_path)
    dur_new = librosa.get_duration(path=new_path)
    
    if abs(dur_orig - dur_new) < 0.05:
        return True
    return False
