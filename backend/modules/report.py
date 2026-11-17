import csv
import os
from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None


def dataset_summary_csv(report: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Metric", "Value"])
        for key, value in report.items():
            writer.writerow([key, value])
    return output_path

dataset_report_csv = dataset_summary_csv


def dataset_report_html(report: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    html = [
        "<html>",
        "<head><meta charset='utf-8'><title>Data Processing Report</title></head>",
        "<body style='font-family:Arial,sans-serif;background:#0f172a;color:#e2e8f0;padding:24px;'>",
        "<div style='max-width:900px;margin:auto;background:#111827;padding:24px;border-radius:20px;'>",
        "<h1 style='color:#38bdf8;'>AI Data Processing Report</h1>",
        f"<p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>",
        "<table style='width:100%;border-collapse:collapse;margin-top:16px;'>",
        "<thead><tr><th style='text-align:left;padding:10px;border-bottom:1px solid #374151;'>Metric</th><th style='text-align:left;padding:10px;border-bottom:1px solid #374151;'>Value</th></tr></thead>",
        "<tbody>",
    ]

    for key, value in report.items():
        html.append(
            f"<tr><td style='padding:10px;border-bottom:1px solid #374151;'>{key}</td><td style='padding:10px;border-bottom:1px solid #374151;'>{value}</td></tr>"
        )

    html.extend([
        "</tbody>",
        "</table>",
        "</div>",
        "</body>",
        "</html>",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    return output_path


def dataset_report_pdf(report: dict, output_path: str):
    if canvas is None:
        raise RuntimeError("reportlab is required for PDF generation")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 50, "AI Data Processing Report")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    y = height - 100
    for key, value in report.items():
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 10)

        c.drawString(40, y, f"{key}:")
        c.drawString(220, y, str(value))
        y -= 20

    c.save()
    return output_path
