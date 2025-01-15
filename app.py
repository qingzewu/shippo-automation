from flask import Flask, request, send_file, render_template
import os
from controllers.shipment_controller import process_shipments
from utils.csv_handler import read_csv, write_csv
from utils.xlsx_handler import read_xlsx
from controllers.label_downloader import merge_pdfs

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'data'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def upload_file():
    """Render the upload page."""
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def handle_file_upload():
    """Handle file upload and process shipments."""
    file = request.files.get('file')
    if not file:
        return "No file uploaded. Please upload a .csv or .xlsx file.", 400

    # Save uploaded file
    file_name = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(file_path)

    # Extract base name and file extension
    base_name, ext = os.path.splitext(file_name)
    ext = ext.lower()

    # Set output paths
    csv_output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_with_tracking.csv")
    pdf_output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_bulk_labels.pdf")
    error_log_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_errors.log")

    try:
        # Read input file
        if ext == '.xlsx':
            shipment_data = read_xlsx(file_path)
        elif ext == '.csv':
            shipment_data = read_csv(file_path)
        else:
            return "Unsupported file type. Please upload a .csv or .xlsx file.", 400

        # Process shipments
        results, pdf_files, errors = process_shipments(shipment_data)

        # Ensure the fieldnames match the original input file + additional fields
        fieldnames = list(shipment_data[0].keys()) + [
            "tracking_number", "carrier", "shipment_level", "price"
        ]

        # Prepare processed results with all original fields and selected additional fields
        processed_results = []
        for original_row, processed_row in zip(shipment_data, results):
            # Start with all original columns from the input file
            combined_row = {key: original_row.get(key, "") for key in shipment_data[0].keys()}
            
            # Add the selected additional fields from the processing results
            for key in ["tracking_number", "carrier", "shipment_level", "price"]:
                combined_row[key] = processed_row.get(key, "")
            
            processed_results.append(combined_row)

        # Save results to CSV
        if processed_results:
            write_csv(csv_output_path, fieldnames, processed_results)

        # Save error log if errors occurred
        if errors:
            with open(error_log_path, 'w') as error_log:
                error_log.write("\n".join(errors))

        # Merge PDF labels if generated
        if pdf_files:
            merge_pdfs(pdf_files, pdf_output_path)
        # Provide options for downloading CSV and PDF
        if errors:
            return render_template('download.html', 
                                   csv_path=csv_output_path, 
                                   pdf_path=pdf_output_path, 
                                   error_log_path=error_log_path)

        return render_template('download.html', 
                               csv_path=csv_output_path, 
                               pdf_path=pdf_output_path)

    except Exception as e:
        return f"An error occurred while processing the file: {str(e)}", 500


@app.route('/download/<file_type>')
def download_file(file_type):
    """Serve files for download."""
    file_map = {
        "csv": request.args.get("csv_path"),
        "pdf": request.args.get("pdf_path"),
        "log": request.args.get("error_log_path"),
    }
    file_path = file_map.get(file_type)
    if not file_path or not os.path.exists(file_path):
        return "Requested file not found.", 404
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)