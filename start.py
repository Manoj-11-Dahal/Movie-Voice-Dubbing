import subprocess
import sys
import time
import os

def print_header(msg):
    print(f"\n{'='*50}\n====> {msg}\n{'='*50}\n")

def get_venv_python():
    """Detects or creates a virtual environment, and returns the correct python executable."""
    venv_dir = os.path.join(os.path.dirname(__file__), "venv")
    
    # Path mappings for Windows vs Linux/Mac
    if os.name == 'nt': # Windows
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else: # Linux/Mac/WSL
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")

    # Create VENV if it doesn't exist
    if not os.path.exists(venv_dir):
        print_header("INITIALIZING VIRTUAL ENVIRONMENT")
        print("Creating isolated environment in /venv. This may take a minute...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    else:
        print("[System] Virtual environment located.")

    # Force dependency checks on every boot to guarantee no missing modules
    print("Mapping and enforcing dependencies via pip install -r requirements.txt...")
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    subprocess.run([pip_exe, "install", "-r", req_path], check=True)
    print("Virtual Environment securely populated!")
    print_header("VENV SETUP COMPLETE")

    # ── ALL TO ALL: Pre-Cache All Gigabyte Machine Learning Weights Natively ──
    # Before we ever spin up the Uvicorn threads, we assert all HF local model caching is complete
    print_header("VERIFYING LOCAL AI MODEL WEIGHTS")
    download_script = os.path.join(os.path.dirname(__file__), "scripts", "download_models.py")
    if os.path.exists(download_script):
        print("Executing centralized model verification script...")
        subprocess.run([python_exe, download_script], check=True)
    else:
        print("[System] Model download script bypassed (script omitted).")

    return python_exe

def check_redis():
    """Validates if Redis is running locally before starting the pipeline."""
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=2)
        if "PONG" in result.stdout:
            return True
    except Exception:
        pass
    
    print("[WARNING] Redis ping failed or not in PATH.")
    print("Ensure Redis is running locally on port 6379 for Celery Worker tasks.")
    time.sleep(1)
    return True

def start_services():
    print_header("INITIALIZING OMNIVOICE DUBBING SERVER")
    
    # 0. Boot Virtual Environment & Install Depdendencies dynamically
    python_exe = get_venv_python()
    
    check_redis()

    # Pre-configurations
    env = os.environ.copy()
    env["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
    env["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/1"
    env["OUTPUT_DIR"] = "./storage/output"
    env["UPLOAD_DIR"] = "./storage/uploads"
    env["BACKEND_URL"] = "http://localhost:8000"
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__))

    processes = []

    try:
        # 1. Start FastAPI Backend (Using venv python)
        print("[1/3] Spinning up FastAPI Master Server (Port: 8000)...")
        backend_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            env=env,
            cwd=os.path.dirname(__file__)
        )
        processes.append(("FastAPI Backend", backend_proc))
        time.sleep(2) 

        # 2. Start Celery Worker (Using venv python)
        print("[2/3] Spinning up Celery ML Pipeline Worker...")
        celery_proc = subprocess.Popen(
            [python_exe, "-m", "celery", "-A", "backend.app.tasks.celery_app", "worker", "-l", "info", "-P", "solo"],
            env=env,
            cwd=os.path.dirname(__file__)
        )
        processes.append(("Celery Worker", celery_proc))
        time.sleep(2)

        # 3. Start Gradio Frontend (Using venv python)
        print("[3/3] Spinning up Premium UI Dashboard (Port: 7860)...")
        frontend_script = os.path.join(os.path.dirname(__file__), "frontend", "gradio_app.py")
        frontend_proc = subprocess.Popen(
            [python_exe, frontend_script],
            env=env,
            cwd=os.path.dirname(__file__)
        )
        processes.append(("Gradio UI", frontend_proc))
        
        print_header("SERVER ONLINE: http://127.0.0.1:7860")
        
        # Keep main thread aggressively alive to watch the subprocesses
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print_header("SHUTTING DOWN ALL SERVICES")
        for name, proc in processes:
            print(f"Terminating {name}...")
            proc.terminate()
            proc.wait()
        print("Graceful shutdown mapped successfully.")
        sys.exit(0)

if __name__ == "__main__":
    start_services()
