from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import uuid
import os
import shutil

from ..tasks.dubbing_task import process_video

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "storage/output")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    target_lang: str = Form("fra_Latn"),
    voice_to_voice: bool = Form(True)
):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    task = process_video.delay(job_id, file_path, target_lang, voice_to_voice)
    return {"job_id": job_id, "task_id": task.id}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return {"state": "GENERATING", "progress": 0.5}

@router.get("/download/{job_id}")
async def download_video(job_id: str):
    for f in os.listdir(OUTPUT_DIR):
        if job_id in f:
            return FileResponse(os.path.join(OUTPUT_DIR, f))
    return JSONResponse(status_code=404, content={"message": "Not found"})

@router.get("/health")
async def health_check():
    return {"status": "ok"}
