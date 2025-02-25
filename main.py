import os
from controllers.shipment_controller import process_shipments
from utils.csv_handler import read_csv, write_csv
from utils.xlsx_handler import read_xlsx, write_xlsx
from controllers.label_downloader import merge_pdfs

def main(input_file):
    """Main function for processing shipments."""
    # Extract the base name (without extension) from the input file path
    base_name, ext = os.path.splitext(os.path.basename(input_file))
    output_folder = 'data'
    os.makedirs(output_folder, exist_ok=True)

    xlsx_output_path = os.path.join(output_folder, f"{base_name}_反馈.xlsx")
    pdf_output_path = os.path.join(output_folder, f"{base_name}_bulk_labels.pdf")
    error_log_path = os.path.join(output_folder, f"{base_name}_errors.log")

    # Read the input file
    if ext == '.xlsx':
        shipment_data = read_xlsx(input_file)
    elif ext == '.csv':
        shipment_data = read_csv(input_file)
    else:
        print("Unsupported file type. Please provide a .csv or .xlsx file.")
        return
    print(shipment_data[1].keys())
    # Process shipments
    results, pdf_files, errors = process_shipments(shipment_data)
    # print(shipment_data[0].keys())
    print(results[0].keys())
    # Remove `label_path` and `error_message` from the results
    # Ensure the fieldnames match the filtered results
    fieldnames = list(shipment_data[0].keys()) + [
        "tracking_number", "carrier", "shipment_level", "price"
    ]
    print(fieldnames)
    # Save results
    if results:
        write_xlsx(xlsx_output_path, fieldnames, results)
        print(f"Processed shipments. Results written to {xlsx_output_path}")

    # Save error log
    if errors:
        with open(error_log_path, 'w') as error_log:
            error_log.write("\n".join(errors))
        print(f"Errors logged to {error_log_path}")

    # Merge PDF labels
    if pdf_files:
        merge_pdfs(pdf_files, pdf_output_path)
        print(f"Bulk PDF with all labels created: {pdf_output_path}")
    else:
        print("No labels were generated.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file>")
    else:
        main(sys.argv[1])