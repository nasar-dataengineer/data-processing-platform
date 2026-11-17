import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator

from .config import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE,
    PROCESSED_FOLDER,
    PROGRESS_FOLDER,
    REPORTS_FOLDER,
    UPLOAD_FOLDER,
)
from .modules.report import dataset_report_csv, dataset_report_html, dataset_report_pdf
from .modules.visualization import correlation_matrix, histogram_data, missing_value_summary
from .preprocessing import (
    generate_recommendations,
    inspect_dataset,
    preprocess_dataset,
)
from .utils.file_reader import get_memory_usage, get_preview, load_file, safe_filename
from .utils.logger import logger


class PreprocessOptions(BaseModel):
    filename: str
    output_format: str = Field("csv")
    missing_strategy: str = Field("median")
    constant_value: Optional[str] = None
    remove_duplicates: bool = True
    remove_empty_rows: bool = False
    remove_empty_columns: bool = False
    trim_spaces: bool = True
    remove_duplicate_columns: bool = False
    convert_to_numeric: bool = False
    convert_to_float: bool = False
    convert_to_integer: bool = False
    convert_to_boolean: bool = False
    convert_to_datetime: bool = False
    encoding: Optional[str] = None
    scaling: Optional[str] = None
    outlier_method: Optional[str] = None
    variance_threshold: float = 0.0
    correlation_threshold: float = 0.95
    mutual_information: bool = False
    target_column: Optional[str] = None

    @validator("output_format")
    def validate_output_format(cls, value: str) -> str:
        allowed = {"csv", "xlsx", "xls", "json", "parquet", "pdf"}
        if value not in allowed:
            raise ValueError("Unsupported output format")
        return value

    @validator("missing_strategy")
    def validate_missing_strategy(cls, value: str) -> str:
        allowed = {
            "mean",
            "median",
            "mode",
            "constant",
            "ffill",
            "bfill",
            "drop_rows",
            "drop_columns",
        }
        if value not in allowed:
            raise ValueError("Unsupported missing value strategy")
        return value

    @validator("encoding")
    def validate_encoding(cls, value: Optional[str]) -> Optional[str]:
        allowed = {"label", "onehot", "ordinal", None}
        if value not in allowed:
            raise ValueError("Unsupported encoding method")
        return value

    @validator("scaling")
    def validate_scaling(cls, value: Optional[str]) -> Optional[str]:
        allowed = {"minmax", "standard", "robust", "maxabs", None}
        if value not in allowed:
            raise ValueError("Unsupported scaling method")
        return value

    @validator("outlier_method")
    def validate_outlier_method(cls, value: Optional[str]) -> Optional[str]:
        allowed = {"iqr", "zscore", "isolation_forest", None}
        if value not in allowed:
            raise ValueError("Unsupported outlier method")
        return value


app = FastAPI(
    title="AI Data Processing API",
    version="2.0.0",
    description="AI Data Processing Platform backend for large dataset support, preprocessing, visualization, and report generation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def progress_path(filename: str) -> str:
    return os.path.join(PROGRESS_FOLDER, f"{safe_filename(filename)}.json")


def write_progress(
    filename: str,
    status: str,
    percent: int = 0,
    message: str = "",
    processed_filename: Optional[str] = None,
    report: Optional[Dict[str, Any]] = None,
) -> None:
    payload = {
        "filename": filename,
        "status": status,
        "percent": percent,
        "message": message,
        "processed_filename": processed_filename,
    }
    if report is not None:
        payload["report"] = report

    with open(progress_path(filename), "w", encoding="utf-8") as progress_file:
        json.dump(payload, progress_file, indent=2)


def read_progress(filename: str) -> Dict[str, Any]:
    path = progress_path(filename)
    if not os.path.exists(path):
        return {"status": "not_started", "percent": 0, "message": "Awaiting preprocessing."}
    with open(path, "r", encoding="utf-8") as progress_file:
        return json.load(progress_file)


@app.on_event("startup")
def startup_event():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    os.makedirs(PROGRESS_FOLDER, exist_ok=True)
    logger.info("AI Data Processing API started")


@app.get("/")
def home():
    return {"message": "AI Data Processing API is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = safe_filename(file.filename)
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    total_bytes = 0

    with open(upload_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_UPLOAD_SIZE:
                raise HTTPException(status_code=413, detail="Uploaded file is too large.")
            buffer.write(chunk)

    try:
        df = load_file(upload_path)
    except Exception as exc:
        logger.exception("Failed to load uploaded dataset")
        raise HTTPException(status_code=400, detail=str(exc))

    metadata = inspect_dataset(df, file_path=upload_path)
    metadata["recommendations"] = generate_recommendations(metadata)
    metadata["filename"] = filename
    write_progress(filename, status="uploaded", percent=0, message="Dataset uploaded and ready.")

    return {"message": "Upload successful", "metadata": metadata}


@app.get("/dataset-info")
def dataset_info(filename: str = Query(...), processed: bool = Query(False)):
    safe_name = safe_filename(filename)
    folder = PROCESSED_FOLDER if processed else UPLOAD_FOLDER
    dataset_path = os.path.join(folder, safe_name)
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = load_file(dataset_path)
    metadata = inspect_dataset(df, file_path=dataset_path)
    metadata["recommendations"] = generate_recommendations(metadata)
    metadata["processed"] = processed
    return metadata


@app.get("/preview")
def preview_dataset(
    filename: str = Query(...), processed: bool = Query(False), rows: int = Query(20)
):
    safe_name = safe_filename(filename)
    folder = PROCESSED_FOLDER if processed else UPLOAD_FOLDER
    dataset_path = os.path.join(folder, safe_name)
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = load_file(dataset_path)
    return {"preview": get_preview(df, rows=rows)}


@app.post("/preprocess")
def preprocess_dataset_endpoint(
    options: PreprocessOptions, background_tasks: BackgroundTasks
):
    safe_name = safe_filename(options.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, safe_name)
    if not os.path.exists(upload_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found.")

    processed_filename = f"cleaned_{Path(safe_name).stem}.{options.output_format.lstrip('.')}"
    write_progress(
        safe_name,
        status="queued",
        percent=5,
        message="Preprocessing queued.",
        processed_filename=processed_filename,
    )
    background_tasks.add_task(run_preprocessing_task, options.dict())

    return {
        "message": "Preprocessing started.",
        "task_key": safe_name,
        "processed_filename": processed_filename,
    }


def run_preprocessing_task(options: Dict[str, Any]) -> None:
    filename = safe_filename(options["filename"])
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(upload_path):
        write_progress(filename, status="failed", percent=0, message="Source file not found.")
        return

    processed_filename = f"cleaned_{Path(filename).stem}.{options['output_format'].lstrip('.')}"
    write_progress(filename, status="processing", percent=10, message="Loading dataset.")

    try:
        df = load_file(upload_path)
        write_progress(filename, status="processing", percent=25, message="Running preprocessing pipeline.")
        _, saved_filename, report = preprocess_dataset(df, filename, options)
        write_progress(
            filename,
            status="completed",
            percent=100,
            message="Preprocessing completed successfully.",
            processed_filename=saved_filename,
            report=report,
        )
    except Exception as exc:
        logger.exception("Background preprocessing failed")
        write_progress(filename, status="failed", percent=0, message=str(exc))


@app.get("/progress")
def progress(filename: str = Query(...)):
    safe_name = safe_filename(filename)
    return read_progress(safe_name)


@app.get("/download")
def download_processed_file(filename: str = Query(...)):
    safe_name = safe_filename(filename)
    processed_path = os.path.join(PROCESSED_FOLDER, safe_name)
    if not os.path.exists(processed_path):
        raise HTTPException(status_code=404, detail="Processed file not found.")
    return FileResponse(processed_path, media_type="application/octet-stream", filename=safe_name)


@app.post("/report")
def create_report(filename: str = Query(...), report_type: str = Query("html")):
    safe_name = safe_filename(filename)
    processed_path = os.path.join(PROCESSED_FOLDER, safe_name)
    if not os.path.exists(processed_path):
        raise HTTPException(status_code=404, detail="Processed file not found.")

    df = load_file(processed_path)
    metadata = inspect_dataset(df, file_path=processed_path)
    metadata["recommendations"] = generate_recommendations(metadata)

    report_name = f"report_{Path(safe_name).stem}.{report_type}"
    report_path = os.path.join(REPORTS_FOLDER, report_name)

    if report_type == "html":
        dataset_report_html(metadata, report_path)
    elif report_type == "csv":
        dataset_report_csv(metadata, report_path)
    elif report_type == "pdf":
        dataset_report_pdf(metadata, report_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported report type.")

    return {"message": "Report generated", "report_filename": report_name}


@app.get("/download-report")
def download_report(report_filename: str = Query(...)):
    safe_name = safe_filename(report_filename)
    report_path = os.path.join(REPORTS_FOLDER, safe_name)
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(report_path, media_type="application/octet-stream", filename=safe_name)
