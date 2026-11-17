# Data Processing Platform

Upload CSV, Excel (`.xlsx`/`.xls`), JSON, Parquet, text, or PDF files to inspect and preprocess tabular data. Processed data can be downloaded as CSV or PDF.

PDF input supports selectable text and tables. Scanned/image-only PDFs require OCR and are not currently supported.

## Run locally

From the project directory, install the backend dependencies and start the API:

```powershell
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload
```

In a second terminal, install the frontend dependencies and start Vite:

```powershell
npm install
npm run dev
```

The frontend expects the API at `http://127.0.0.1:8000` by default. Set `VITE_API_BASE_URL` to override it.

## Tests

Run the backend format and preprocessing tests:

```powershell
python -m unittest backend.tests.test_file_formats
```
