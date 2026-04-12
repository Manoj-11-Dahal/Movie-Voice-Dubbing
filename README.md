# 🎬 Local Dubbing Platform – Complete A-Z Guide

A **fully offline, production-ready** dubbing platform that preserves original speaker voices (voice-to-voice translation), background music, and sound effects. Uses OmniVoice, Whisper, NLLB-200, Demucs, pyannote, and more – **no external APIs**.

---

## 📋 Table of Contents

1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Quick Start](#quick-start)
4. [Project Structure](#project-structure)
5. [How It Works – Pipeline Overview](#how-it-works--pipeline-overview)
6. [Configuration](#configuration)
7. [Running the Platform](#running-the-platform)
8. [API Reference](#api-reference)
9. [Frontend (Gradio) Usage](#frontend-gradio-usage)
10. [Voice-to-Voice Translation](#voice-to-voice-translation)
11. [Troubleshooting](#troubleshooting)
12. [Performance Tuning](#performance-tuning)
13. [Extending the Platform](#extending-the-platform)
14. [Credits & License](#credits--license)

---

## ✨ Features

- **100% local** – no data leaves your server
- **Voice-to-voice translation** – original speaker timbre preserved
- **Multilingual** – 200+ languages (NLLB-200)
- **Music & effects preservation** – Demucs source separation
- **Emotion-aware synthesis** – adds `[laughter]`, `[sigh]`, etc.
- **Frame-accurate sync** – uses original segment durations
- **Web UI** (Gradio) + REST API (FastAPI)
- **Asynchronous job queue** (Celery + Redis)
- **Scalable** – multiple GPU workers
- **Dockerized** – easy deployment

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | 16 GB VRAM (e.g., RTX 4080) | 24+ GB (RTX 4090, A5000) |
| **RAM** | 16 GB | 64 GB |
| **CPU** | 8 cores | 16+ cores |
| **Storage** | 200 GB (models + temp files) | 1 TB SSD |
| **OS** | Windows / Linux (Ubuntu 20.04+) | Linux (Ubuntu 22.04) |

**Software prerequisites**:
- Docker & Docker Compose
- NVIDIA Container Toolkit (for GPU)
- Python 3.10+ (for local development)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/dubbing-platform.git
cd dubbing-platform

# 2. Copy environment file
cp .env.example .env
# Edit .env if needed (GPU, etc.)

# 3. Start all services
docker-compose up --build

# 4. Open browser → http://localhost:7860
```

First startup downloads ~15 GB of models (once). Subsequent starts are instant.

---

## 📁 Project Structure

```
dubbing_platform/
│
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
├── requirements.txt
├── setup.py
│
├── backend/                     # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── tasks/               # Celery tasks
│       ├── models/              # Model loaders
│       └── utils/
│
├── worker/                      # Celery worker configuration
│   ├── Dockerfile
│   ├── requirements.txt
│   └── start_worker.sh
│
├── frontend/                    # Gradio Web UI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── gradio_app.py
│
├── OmniVoice-0.1.3/             # Local OmniVoice installation
│   └── ...                      # Model inference library
│
├── scripts/                     # 12-Stage Pipeline scripts
│   ├── stage_01_extract_audio.py
│   ├── stage_02_denoise.py
│   ├── stage_03_separate_sources.py
│   ├── stage_04_diarization.py
│   ├── stage_05_transcribe_wordlevel.py
│   ├── stage_06_align_speakers.py
│   ├── stage_07_emotion_detection.py
│   ├── stage_08_translate_nllb.py
│   ├── stage_09_extract_references.py
│   ├── stage_10_generate_omnivoice.py
│   ├── stage_11_reassemble_audio.py
│   ├── stage_12_mux_video.py
│   └── utils/
│
├── config/                      # Configuration files
│   ├── pipeline_config.yaml
│   └── emotion_tag_map.yaml
│
└── storage/                     # Runtime data (created at runtime)
    ├── uploads/
    ├── jobs/
    └── output/
```

---

## ⚙️ How It Works – Pipeline Overview

| Stage | Script | Description |
|-------|--------|-------------|
| 1 | `extract_audio` | Extract 24 kHz mono WAV from video |
| 2 | `denoise` | Remove background noise (Sidon) |
| 3 | `separate_sources` | Demucs → dialogue, music+effects (M&E) |
| 4 | `diarization` | pyannote → speaker segments |
| 5 | `transcribe_wordlevel` | Whisper large-v3 with word timestamps |
| 6 | `align_speakers` | Assign speaker labels to each word |
| 7 | `emotion_detection` | Wav2Vec2-emotion per word |
| 8 | `translate_nllb` | Translate text to target language (NLLB-200) |
| 9 | `extract_references` | Build clean reference clips per speaker |
| 10 | `generate_omnivoice` | Synthesise translated speech (original timbre) |
| 11 | `reassemble_audio` | Mix new dialogue with original M&E (crossfade) |
| 12 | `mux_video` | Replace audio track in video (FFmpeg) |

All stages are orchestrated by Celery and can be re-run independently.

---

## 🛠️ Configuration

Main configuration file: `config/pipeline_config.yaml`

```yaml
models:
  omnivoice: "./OmniVoice-0.1.3"  # Local model
  whisper: "large-v3"
  pyannote: "pyannote/speaker-diarization-3.1"
  emotion: "facebook/wav2vec2-base-ravens"
  nllb: "facebook/nllb-200-distilled-1.3B"
  demucs: "demucs"

generation:
  num_step: 16               # diffusion steps (16 fast, 32 quality)
  guidance_scale: 2.0
  preprocess_prompt: true
  postprocess_output: true
  crossfade_duration: 0.01   # seconds

voice_to_voice:
  enabled: true
  fallback_to_design: true
  similarity_threshold: 0.75

audio:
  sample_rate: 24000
  channels: 1
```

Emotion mapping: `config/emotion_tag_map.yaml`

```yaml
happy: "[laughter]"
sad: "[sigh]"
angry: "[dissatisfaction-hnn]"
surprised: "[surprise-ah]"
neutral: ""
```

---

## 🏃 Running the Platform

### Start all services

```bash
docker-compose up --build
```

### Stop

```bash
docker-compose down
```

### Scale workers (more GPUs)

```bash
docker-compose up --scale worker=4
```

### View logs

```bash
docker-compose logs -f backend
docker-compose logs -f worker
```

### Reset all data

```bash
docker-compose down -v
rm -rf storage/*
```

---

## 📡 API Reference

The backend exposes a REST API on port `8000`.

### `POST /upload`
Upload a video and start dubbing.
**Request** (multipart/form-data):
- `file`: video file (MP4, MOV)
- `target_lang`: NLLB language code (default `fra_Latn`)
- `voice_to_voice`: boolean (default `true`)

**Response**:
```json
{
  "job_id": "uuid",
  "task_id": "celery-task-id"
}
```

### `GET /status/{job_id}`
Get job progress.

**Response**:
```json
{
  "state": "GENERATING",
  "progress": 0.75
}
```

### `GET /download/{job_id}`
Download the final dubbed video.
**Response**: MP4 file.

### `GET /health`
Health check.

---

## 🖥️ Frontend (Gradio) Usage

Open `http://localhost:7860`.

1. **Upload** a video file.
2. **Select target language** (e.g., `fra_Latn` for French).
3. **Check** "Preserve original speaker's voice" (voice-to-voice).
4. Click **Start Dubbing**.
5. Watch progress bar.
6. **Download** the dubbed video when ready.

The UI automatically refreshes progress every 2 seconds.

---

## 🎤 Voice-to-Voice Translation

**What it does**: The final dubbed speaker sounds like the original actor, even though they are now speaking a different language.

**How it works**:
- Stage 9 extracts a **clean 3-10 second clip** of each speaker from the original dialogue.
- Stage 10 uses that clip as `ref_audio` in OmniVoice.
- The translated text is generated with the original timbre.

**Configuration**:
- `voice_to_voice.enabled`: set to `true` (default).
- If a speaker has no reference clip (e.g., too short), the system falls back to **voice design** using language-appropriate attributes.

---

## 🔧 Troubleshooting

### Out of memory (CUDA OOM)
- Reduce `generation.num_step` to 16.
- Set `CUDA_VISIBLE_DEVICES` to a single GPU.
- Reduce worker concurrency to 1.

### Whisper word timestamps are misaligned
- The audio must be 24 kHz mono. Stage 1 already ensures that.
- If still bad, use `stage_05_transcribe_wordlevel.py` with `--language` forced.

### NLLB translation quality is low
- Use the larger `nllb-200-distilled-1.3B` (already default).

### Gradio UI shows "Connection error"
- Ensure backend container is running: `docker-compose ps`.
- Check `BACKEND_URL` in frontend environment.

---

## ⚡ Performance Tuning

| Parameter | Effect | Recommendation |
|-----------|--------|----------------|
| `num_step: 16` vs `32` | 2x faster, slight quality drop | Use 16 for preview, 32 for final |
| `worker concurrency` | Number of parallel jobs per GPU | Keep at 1 (OmniVoice uses ~8-12 GB VRAM) |
| `crossfade_duration: 0.01` | Smooth joins | 0.005-0.02 is safe |

---

## 📄 Credits & License

**Models**:
- [OmniVoice](https://github.com/k2-fsa/OmniVoice) – Apache 2.0
- [Whisper](https://github.com/openai/whisper) – MIT
- [NLLB-200](https://github.com/facebookresearch/fairseq/tree/nllb) – CC BY-NC 4.0
- [Demucs](https://github.com/facebookresearch/demucs) – MIT
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) – MIT

**Platform code**: MIT (see LICENSE file).

---

**Enjoy dubbing with full control – no cloud, no compromises.**
