<div align="center">
  <img src="https://img.icons8.com/color/150/000000/microphone.png" alt="Logo">
  <h1 align="center">🎬 Movie Voice Dubbing Studio</h1>
  <p align="center">
    <strong>A fully local, GPU-accelerated cinematic dubbing pipeline matching 100% original speaker timelines.</strong>
  </p>

  [![GitHub Repo](https://img.shields.io/badge/GitHub-Manoj--11--Dahal%2FMovie--Voice--Dubbing-blue?style=for-the-badge&logo=github)](https://github.com/Manoj-11-Dahal/Movie-Voice-Dubbing.git)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)]()
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-purple?style=for-the-badge&logo=fastapi)]()
  [![PyTorch](https://img.shields.io/badge/PyTorch-2.4%2B-orange?style=for-the-badge&logo=pytorch)]()
</div>

<hr/>

## 🌟 Overview

**Movie Voice Dubbing Studio** is an advanced, offline architecture designed to autonomously translate and dub video content while mathematically preserving the original acoustic environment. 

By orchestrating **Whisper**, **Pyannote**, **Demucs**, and **OmniVoice-0.1.3**, this pipeline extracts a target video, maps the exact temporal boundaries of every specific character in the scene, synthesizes deep-layer multi-language translations, and clones 100% identical biometric voice acoustics. The generated vocal stems are seamlessly layered back onto the pristine, isolated background/music track, guaranteeing zero interference with the source movie's sound design.

<br>

<div align="center">
  <!-- (Replace this with a screenshot of the beautiful Glassmorphism Gradio Dashboard) -->
  <img src="https://via.placeholder.com/800x400.png?text=OmniVoice+Studio+Dashboard+Preview" alt="Dashboard Preview">
</div>

<br>

## ⚙️ 12-Stage ML Pipeline Architecture

Our platform executes a strict algorithmic sequence orchestrated over Celery Task Queues:

| Stage | Subsystem | Action |
| :--- | :--- | :--- |
| **01** | `FFmpeg` | Forcefully extracts isolated audio bound to `24kHz` Mono constraints. |
| **02** | `Denoise` | Scrubs digital hiss and static to prime stems for ML interpolation. |
| **03** | `Demucs` | Deconstructs the acoustic layers, physically capturing exactly 100% unharmed Music/SFX background templates. |
| **04** | `Pyannote` | Diarization array maps chronological IDs (`SPEAKER_00`, `SPEAKER_01`) dynamically separating different characters. |
| **05** | `Whisper` | Scans text generating highly-precise millisecond word-level timestamps (`time stand`). |
| **06** | `Alignment` | Mathematically cross-references Speaker IDs mapping precisely who spoke which words. |
| **07** | `DistilRoBERTa`| Analyzes NLP acoustics, embedding biometric emotion tokens (e.g. `[laughter]`) to prevent robotic tones. |
| **08** | `Deep Translator`| Parses the timeline JSON and translates the localized variables natively. |
| **09** | `FFmpeg` | Dynamically slices clean 8-second 100% identical biometric vocal markers per unique character ID. |
| **10** | `OmniVoice` | AI Model synthesizes the exact audio utilizing the biometric markers and mathematically forces boundaries adhering exactly to the original timeline durations. |
| **11** | `Audio Muxing` | Layers the isolated translated AI stems perfectly back onto the untouched pure `Demucs` background music. |
| **12** | `FFmpeg` | Non-destructive `copy` multiplexer binds the final English/French/Spanish audio matrix onto the MP4 timeline. |

---

## ⚡ Deployment & Installation

### Option 1: Native Windows Executable (Recommended for Local GPU)
This project features a fully automated deployment loop specifically engineered for local desktop usage, bypassing Docker-induced GPU driver conflicts.

1. Clone the repository:
   ```bash
   git clone https://github.com/Manoj-11-Dahal/Movie-Voice-Dubbing.git
   cd Movie-Voice-Dubbing
   ```
2. Start your local **Redis** instance (Required on Port `6379`).
3. Run the Auto-Orchestrator:
   ```bash
   python start.py
   ```
   > 🚀 **How it works:** `start.py` will automatically build a secure Virtual Environment, download and map over 60 Pip dependencies targeting your specific Python binaries, download Gigabytes of huggingface Machine Learning models proactively, and finally spawn the `FastAPI`, `Celery Worker`, and `Gradio UI` background threads.

### Option 2: Docker Containerization
For native Linux environments scaling to AWS/GCP pipelines.
```bash
docker-compose up --build
```

---

## 🎨 Frontend Architecture

The interface natively runs on `http://127.0.0.1:7860`. Built around a custom HTML/CSS Glassmorphism injection over Gradio, the UI seamlessly polls the backend Celery tasks parsing live UI status pills reporting the exact fractional state of the 12-stage pipeline globally. 

## 🔧 Environment Variables

On initial launch, a `.env` file is generated. Ensure that if you plan to fully utilize Pyannote's gated diarization protocols, you provide a valid Huggingface Authorize Token.

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
OUTPUT_DIR=./storage/output
UPLOAD_DIR=./storage/uploads
BACKEND_URL=http://localhost:8000
HF_AUTH_TOKEN=your_huggingface_access_token_here
```

## 📜 License
This project operates under the **MIT License**. Deep Translation arrays and OmniVoice libraries possess independent usage metrics dynamically located via `./LICENSE`.
