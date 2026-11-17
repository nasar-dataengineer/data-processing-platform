import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
PROGRESS_FOLDER = os.path.join(BASE_DIR, "progress")
MAX_UPLOAD_SIZE = 1024 * 1024 * 1024  # 1GB
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "json", "parquet", "txt", "pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(PROGRESS_FOLDER, exist_ok=True)
