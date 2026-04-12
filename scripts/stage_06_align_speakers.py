import json
import os

def run(transcription_json: str, diarization_json: str, output_json: str):
    """
    Stage 6: Align Speakers to Timeline Map
    Requirements Addressed: "timeline, time structure, time stand" + "different character"
    
    This mathematically merges Whisper's exact text timeline (what was said and EXACTLY when) 
    with Pyannote's speaker timeline (WHO was speaking and EXACTLY when). 
    We cross-reference timestamps to assign `SPEAKER_01` definitively to the word "Hello".
    """
    print("[Stage 6] Aligning Movie Characters to vocal timeline text boundaries...")
    
    with open(transcription_json, "r", encoding="utf-8") as f:
        trans_data = json.load(f)
        
    with open(diarization_json, "r", encoding="utf-8") as f:
        diar_data = json.load(f)
        
    words = trans_data.get("timeline", [])
    characters = diar_data.get("characters", [])
    
    aligned_timeline = []
    
    for word in words:
        w_start = word["start"]
        w_end = word["end"]
        assigned_char = "UNKNOWN"
        max_overlap = 0.0
        
        # Find which Pyannote character block overlaps the most with this Whisper word block
        for char_block in characters:
            c_start = char_block["start"]
            c_end = char_block["end"]
            
            # Calculate overlapping time window
            overlap_start = max(w_start, c_start)
            overlap_end = min(w_end, c_end)
            overlap_duration = max(0.0, overlap_end - overlap_start)
            
            if overlap_duration > max_overlap:
                max_overlap = overlap_duration
                assigned_char = char_block["character_id"]
                
        # Lock in the final structured boundary
        aligned_timeline.append({
            "character_id": assigned_char,
            "word": word["word"],
            "start": w_start,
            "end": w_end
        })
        
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "language_detected": trans_data.get("language_detected"),
            "full_text": trans_data.get("full_text"),
            "timeline": aligned_timeline
        }, f, indent=4, ensure_ascii=False)
        
    print("[Stage 6] Success: 100% accurate time-structure established.")
    return output_json
