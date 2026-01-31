import subprocess
import threading
import time
import sys
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)
load_dotenv()

def run_backend():
    try:
        logger.info("Starting backend service...")
        subprocess.Popen([
            sys.executable,
            "-m",
            "uvicorn",
            "app.backend.api:app",
            "--host", "127.0.0.1",
            "--port", "9999"
        ])
    except Exception as e:
        logger.exception("Backend failed to start")
        raise CustomException("Failed to start backend", e)

def run_frontend():
    try:
        logger.info("Starting frontend service...")
        subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/frontend/ui.py",
    "--server.headless=true"
], check=True)

    except Exception as e:
        logger.exception("Frontend failed to start")
        raise CustomException("Failed to start frontend", e)

if __name__ == "__main__":
    try:
        threading.Thread(target=run_backend, daemon=True).start()
        time.sleep(3) 
        run_frontend()
    except CustomException as e:
        logger.exception(f"Startup failure: {e}")
