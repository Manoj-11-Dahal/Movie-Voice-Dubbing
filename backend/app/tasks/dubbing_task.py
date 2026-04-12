import os
from .celery_app import celery_app
import sys

# Append scripts directory to path to allow importing the stages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scripts import (
    stage_01_extract_audio,
    stage_03_separate_sources,
    stage_04_diarization,
    stage_05_transcribe_wordlevel,
    stage_06_align_speakers,
    stage_08_translate_nllb,
    stage_09_extract_references,
    stage_10_generate_omnivoice,
    stage_11_reassemble_audio,
    stage_12_mux_video
)

@celery_app.task(bind=True)
def process_video(self, job_id: str, file_path: str, target_lang: str, voice_to_voice: bool):
    print(f"Starting dubbing mapping for job {job_id} using {file_path}")
    
    # ─── FILE MAPPING ALL ───
    # Define the precise file path sequence based on the job ID
    base_dir = os.path.dirname(file_path)
    audio_wav = os.path.join(base_dir, f"{job_id}_raw.wav")
    
    vocals_wav = os.path.join(base_dir, f"{job_id}_vocals.wav")
    bg_wav = os.path.join(base_dir, f"{job_id}_bg.wav")
    
    diarization_json = os.path.join(base_dir, f"{job_id}_diarize.json")
    transcribe_json = os.path.join(base_dir, f"{job_id}_transcribe.json")
    aligned_json = os.path.join(base_dir, f"{job_id}_aligned.json")
    translated_json = os.path.join(base_dir, f"{job_id}_translated.json")
    
    references_dir = os.path.join(base_dir, f"{job_id}_references")
    generated_audio_dir = os.path.join(base_dir, f"{job_id}_generated")
    
    final_audio = os.path.join(base_dir, f"{job_id}_final_audio.wav")
    
    output_dir = os.getenv("OUTPUT_DIR", "storage/output")
    os.makedirs(output_dir, exist_ok=True)
    out_video = os.path.join(output_dir, f"{job_id}_dubbed.mp4")

    try:
        # Stage 1: Extract Audio
        self.update_state(state="EXTRACT_AUDIO", meta={"progress": 0.05})
        stage_01_extract_audio.run(file_path, audio_wav)
        
        # Stage 3: Separate Background
        self.update_state(state="SEPARATE_SOURCES", meta={"progress": 0.15})
        stage_03_separate_sources.run(audio_wav, vocals_wav, bg_wav)
        
        # Stage 4: Diarize Characters
        self.update_state(state="DIARIZATION", meta={"progress": 0.25})
        stage_04_diarization.run(vocals_wav, diarization_json)
        
        # Stage 5: Time Stand / Whisper Timestamping
        self.update_state(state="TRANSCRIBING", meta={"progress": 0.40})
        stage_05_transcribe_wordlevel.run(vocals_wav, diarization_json, transcribe_json, "base")
        
        # Stage 6: Align Speakers to Timeline
        self.update_state(state="ALIGN_TIMELINE", meta={"progress": 0.50})
        stage_06_align_speakers.run(transcribe_json, diarization_json, aligned_json)
        
        # Stage 8: Translate text constraints
        self.update_state(state="TRANSLATING", meta={"progress": 0.60})
        stage_08_translate_nllb.run(aligned_json, target_lang, translated_json)
        
        # Stage 9: Extract 100% same-to-same Original Voice References
        self.update_state(state="EXTRACT_VOICES", meta={"progress": 0.70})
        stage_09_extract_references.run(vocals_wav, aligned_json, references_dir)
        
        # Stage 10: OmniVoice Clone Generation
        self.update_state(state="GENERATING_VOICE", meta={"progress": 0.85})
        stage_10_generate_omnivoice.run(translated_json, references_dir, generated_audio_dir, target_lang)
        
        # Stage 11: Reassemble Audio seamlessly
        self.update_state(state="REASSEMBLING_AUDIO", meta={"progress": 0.90})
        stage_11_reassemble_audio.run(generated_audio_dir, bg_wav, final_audio)
        
        # Stage 12: Mux Video maintaining timeline exactly
        self.update_state(state="MUXING", meta={"progress": 0.95})
        stage_12_mux_video.run(file_path, final_audio, out_video)
        
        return {"status": "SUCCESS", "output_path": out_video}
        
    except Exception as e:
        self.update_state(state="FAILED", meta={"error": str(e)})
        raise e
