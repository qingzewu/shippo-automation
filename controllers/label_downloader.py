import requests
from PyPDF2 import PdfMerger
import os
from utils.config import LABELS_DIR, BULK_PDF_FILE

# Ensure labels directory exists
os.makedirs(LABELS_DIR, exist_ok=True)

def download_label(label_url, file_name):
    """Downloads a label from the given URL."""
    response = requests.get(label_url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(LABELS_DIR, file_name)
        with open(file_path, 'wb') as label_file:
            label_file.write(response.content)
        return file_path
    else:
        raise Exception(f"Failed to download label: {label_url}")

def merge_pdfs(pdf_file_paths, output_file):
    """
    Merges multiple PDF files into a single PDF.

    Args:
        pdf_file_paths (list): List of paths to individual PDF files.
        output_file (str): Path to save the merged PDF file.

    Returns:
        None
    """
    merger = PdfMerger()

    for pdf in pdf_file_paths:
        try:
            merger.append(pdf)
        except Exception as e:
            print(f"Error merging {pdf}: {e}")

    try:
        merger.write(output_file)
        print(f"Merged PDF created at: {output_file}")
    finally:
        merger.close()