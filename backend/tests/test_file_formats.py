import asyncio
from io import BytesIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from fastapi import UploadFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from backend.preprocessing import preprocess_dataset
from backend import main
from backend.utils.file_reader import load_file


class FileFormatTests(unittest.TestCase):
    def test_reads_pdf_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "table.pdf"
            document = SimpleDocTemplate(str(path), pagesize=letter)
            table = Table([["name", "score"], ["Ada", "10"], ["Lin", "12"]])
            table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
            document.build([table])

            frame = load_file(str(path))

            self.assertEqual(frame.columns.tolist(), ["name", "score"])
            self.assertEqual(frame.to_dict(orient="records"), [
                {"name": "Ada", "score": "10"},
                {"name": "Lin", "score": "12"},
            ])

    def test_reads_pdf_text_without_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "text.pdf"
            pdf = canvas.Canvas(str(path))
            pdf.drawString(40, 750, "First line")
            pdf.drawString(40, 730, "Second line")
            pdf.save()

            frame = load_file(str(path))

            self.assertEqual(frame["text"].tolist(), ["First line", "Second line"])
            self.assertEqual(frame["page"].tolist(), [1, 1])

    def test_reads_tab_delimited_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "table.txt"
            path.write_text("name\tscore\nAda\t10\n", encoding="utf-8")

            frame = load_file(str(path))

            self.assertEqual(frame.to_dict(orient="records"), [{"name": "Ada", "score": 10}])

    def test_reads_xlsx_with_declared_engine(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "table.xlsx"
            pd.DataFrame({"name": ["Ada"], "score": [10]}).to_excel(
                path, index=False, engine="openpyxl"
            )

            frame = load_file(str(path))

            self.assertEqual(frame.to_dict(orient="records"), [{"name": "Ada", "score": 10}])

    def test_preprocesses_and_exports_csv_and_pdf(self):
        source = pd.DataFrame({"name": [" Ada ", None]})

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("backend.preprocessing.PROCESSED_FOLDER", temp_dir):
                for output_format in ("csv", "pdf"):
                    _, filename, report = preprocess_dataset(
                        source.copy(),
                        "input.csv",
                        {
                            "output_format": output_format,
                            "missing_strategy": "median",
                        },
                    )
                    output_path = Path(temp_dir) / filename

                    self.assertTrue(output_path.exists())
                    self.assertEqual(report["final_rows"], 2)
                    if output_format == "pdf":
                        self.assertTrue(output_path.read_bytes().startswith(b"%PDF"))
                    else:
                        result = pd.read_csv(output_path)
                        self.assertEqual(result["name"].tolist(), ["Ada", "Ada"])

    def test_pdf_upload_preprocess_and_download_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "input.pdf"
            document = SimpleDocTemplate(str(source_path), pagesize=letter)
            table = Table([["name", "score"], ["Ada", "10"], ["Lin", "12"]])
            table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
            document.build([table])

            upload_dir = root / "uploads"
            processed_dir = root / "processed"
            reports_dir = root / "reports"
            progress_dir = root / "progress"
            for directory in (upload_dir, processed_dir, reports_dir, progress_dir):
                directory.mkdir()

            with (
                patch.object(main, "UPLOAD_FOLDER", str(upload_dir)),
                patch.object(main, "PROCESSED_FOLDER", str(processed_dir)),
                patch.object(main, "REPORTS_FOLDER", str(reports_dir)),
                patch.object(main, "PROGRESS_FOLDER", str(progress_dir)),
                patch("backend.preprocessing.PROCESSED_FOLDER", str(processed_dir)),
            ):
                async def run_endpoints():
                    with source_path.open("rb") as source_file:
                        uploaded_file = UploadFile(filename="input.pdf", file=source_file)
                        upload_result = await main.upload_file(uploaded_file)
                        await uploaded_file.close()

                    filename = upload_result["metadata"]["filename"]
                    self.assertIn("preview", upload_result["metadata"])
                    for output_format in ("csv", "pdf"):
                        background_tasks = main.BackgroundTasks()
                        response = main.preprocess_dataset_endpoint(
                            main.PreprocessOptions(
                                filename=filename,
                                output_format=output_format,
                                missing_strategy="median",
                            ),
                            background_tasks,
                        )
                        await background_tasks()
                        self.assertEqual(main.progress(filename)["status"], "completed")

                        download = main.download_processed_file(
                            response["processed_filename"]
                        )
                        content = Path(download.path).read_bytes()
                        if output_format == "pdf":
                            self.assertTrue(content.startswith(b"%PDF"))
                        else:
                            self.assertEqual(
                                pd.read_csv(BytesIO(content))["name"].tolist(),
                                ["Ada", "Lin"],
                            )

                asyncio.run(run_endpoints())


if __name__ == "__main__":
    unittest.main()
