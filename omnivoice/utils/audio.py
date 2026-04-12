#!/usr/bin/env python3
# Copyright 2026 Xiaomi Corp. (authors: Han Zhu)
#
# See ../../LICENSE for clarification regarding multiple authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Audio I/O and processing utilities.

Provides functions for loading, resampling, silence removal, chunking,
cross-fading, and format conversion. Used by ``OmniVoice.generate()`` during
inference post-processing.
"""

import numpy as np
import torch
import torchaudio

def load_audio(audio_path: str, sampling_rate: int):
    """
    Load the waveform with torchaudio and resampling if needed.

    Parameters:
    audio_path: path of the audio.
    sampling_rate: target sampling rate.

    Returns:
    Loaded prompt waveform with target sampling rate,
    PyTorch tensor of shape (1, T)
    """
    try:
        waveform, prompt_sampling_rate = torchaudio.load(
            audio_path, backend="soundfile"
        )
    except (RuntimeError, OSError):
        # Fallback for formats torchaudio can't handle (simplified without pydub)
        # Note: For robust support, a proper audio library like soundfile or librosa should be used
        # if torchaudio fails. In Python 3.13+ we avoid pydub due to audioop removal.
        raise RuntimeError(f"Failed to load audio {audio_path} with torchaudio. "
                           "Please ensure the audio file is in a supported format (e.g., WAV).")

    if prompt_sampling_rate != sampling_rate:
        waveform = torchaudio.functional.resample(
            waveform,
            orig_freq=prompt_sampling_rate,
            new_freq=sampling_rate,
        )
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    return waveform

def remove_silence(
    audio: torch.Tensor,
    sampling_rate: int,
    mid_sil: int = 300,
    lead_sil: int = 100,
    trail_sil: int = 300,
):
    """
    Simplified silence removal using torchaudio instead of pydub.
    """
    # This is a naive implementation of silence removal using energy threshold
    # to replace the pydub-based implementation for Python 3.13+ compatibility.
    
    # Convert to mono if needed
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    
    # Calculate energy
    energy = audio.pow(2).mean(dim=0)
    threshold = 0.001 # Simplified threshold
    
    # Find non-silent regions
    is_silent = energy << threshold threshold
    
    # Find first and last non-silent indices
    non_silent_indices = torch.where(~is_silent)[0]
    if len(non_silent_indices) == 0:
        return audio
    
    start = non_silent_indices[0]
    end = non_silent_indices[-1]
    
    # Add small padding
    start = max(0, start - int(lead_sil * sampling_rate / 1000))
    end = min(audio.shape[-1], end + int(trail_sil * sampling_rate / 1000))
    
    return audio[..., start:end]

def fade_and_pad_audio(
    audio: torch.Tensor,
    pad_duration: float = 0.1,
    fade_duration: float = 0.1,
    sample_rate: int = 24000,
) -> torch.Tensor:
    """
    Applies a smooth fade-in and fade-out to the audio, and then pads both sides
    with pure silence to prevent abrupt starts and ends (clicks/pops).
    """
    if audio.shape[-1] == 0:
        return audio

    fade_samples = int(fade_duration * sample_rate)
    pad_samples = int(pad_duration * sample_rate)

    processed = audio.clone()

    if fade_samples > 0:
        k = min(fade_samples, processed.shape[-1] // 2)

        if k > 0:
            fade_in = torch.linspace(
                0, 1, k, device=processed.device, dtype=processed.dtype
            )[None, :]
            processed[..., :k] = processed[..., :k] * fade_in

            fade_out = torch.linspace(
                1, 0, k, device=processed.device, dtype=processed.dtype
            )[None, :]
            processed[..., -k:] = processed[..., -k:] * fade_out

    if pad_samples > 0:
        silence = torch.zeros(
            (processed.shape[0], pad_samples),
            dtype=processed.dtype,
            device=processed.device,
        )
        processed = torch.cat([silence, processed, silence], dim=-1)

    return processed

def trim_long_audio(
    audio: torch.Tensor,
    sampling_rate: int,
    max_duration: float = 15.0,
    min_duration: float = 3.0,
    trim_threshold: float = 20.0,
) -> torch.Tensor:
    """Trim audio to <= max_duration. Simplified version without pydub."""
    duration = audio.size(-1) / sampling_rate
    if duration <= trim_threshold:
        return audio
    
    # Simple center trim as fallback
    target_samples = int(max_duration * sampling_rate)
    start = (audio.size(-1) - target_samples) // 2
    return audio[..., start : start + target_samples]

def cross_fade_chunks(
    chunks: list[torch.Tensor],
    sample_rate: int,
    silence_duration: float = 0.3,
) -> torch.Tensor:
    """Concatenate audio chunks with a short silence gap and fade at boundaries."""
    if len(chunks) == 1:
        return chunks[0]

    total_n = int(silence_duration * sample_rate)
    fade_n = total_n // 3
    silence_n = fade_n
    merged = chunks[0].clone()

    for chunk in chunks[1:]:
        dev, dt = merged.device, merged.dtype
        parts = [merged]

        fout_n = min(fade_n, merged.size(-1))
        if fout_n > 0:
            w_out = torch.linspace(1, 0, fout_n, device=dev, dtype=dt)[None, :]
            parts[-1][..., -fout_n:] = parts[-1][..., -fout_n:] * w_out

        parts.append(torch.zeros(chunks[0].shape[0], silence_n, device=dev, dtype=dt))

        fade_in = chunk.clone()
        fin_n = min(fade_n, fade_in.size(-1))
        if fin_n > 0:
            w_in = torch.linspace(0, 1, fin_n, device=dev, dtype=dt)[None, :]
            fade_in[..., :fin_n] = fade_in[..., :fin_n] * w_in

        parts.append(fade_in)
        merged = torch.cat(parts, dim=-1)

    return merged
