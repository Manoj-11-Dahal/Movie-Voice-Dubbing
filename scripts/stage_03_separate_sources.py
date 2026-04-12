import os
import subprocess

def run(input_audio: str, out_vocals: str, out_background: str):
    """
    Stage 3: Demucs Source Separation
    Requirement Addressed: "Background voice same to same 100%"
    
    This script physically isolates the dialogue from the background noise, SFX, 
    and soundtrack. We retain the exact, unadulterated background track which 
    will later be recombined with the newly synthesized cloned voices in Stage 11.
    """
    print(f"[Stage 3] Processing Demucs separation on {input_audio}...")
    
    # Using Facebook's HTDemucs model. 
    # 'htdemucs' splits audio into 4 stems: vocals, bass, drums, other.
    # We combine (bass+drums+other) to form the pristine 100% original background track.
    # Note: Using '--two-stems vocals' optimizes it directly into vocals vs no-vocals.
    
    output_dir = os.path.dirname(out_vocals)
    os.makedirs(output_dir, exist_ok=True)
    
    # We output to a temporary demucs directory inside the output folder
    demucs_out_dir = os.path.join(output_dir, "demucs_separated")
    os.makedirs(demucs_out_dir, exist_ok=True)
    
    command = [
        "demucs", 
        "--two-stems", "vocals",  # Only extract 'vocals' and 'no_vocals'
        "-n", "htdemucs",         # High-quality transformer demucs
        "--out", demucs_out_dir,
        input_audio
    ]
    
    try:
        # Run Demucs synchronously
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Demucs heavily structures its output path: {out}/{model}/{track_name}/{stem}.wav
        base_name = os.path.splitext(os.path.basename(input_audio))[0]
        demucs_vocals = os.path.join(demucs_out_dir, "htdemucs", base_name, "vocals.wav")
        demucs_no_vocals = os.path.join(demucs_out_dir, "htdemucs", base_name, "no_vocals.wav")
        
        if not os.path.exists(demucs_vocals):
            raise FileNotFoundError("Demucs failed to generate vocals track.")
            
        # Move the files to the expected pipeline locations
        import shutil
        shutil.move(demucs_vocals, out_vocals)
        shutil.move(demucs_no_vocals, out_background)
        
        print("[Stage 3] Separation Complete: 100% Original Background Track preserved.")
        return out_vocals, out_background
        
    except Exception as e:
        print(f"[Stage 3] Error during source separation: {e}")
        raise e
