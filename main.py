from controllers.shipment_controller import process_shipments
from utils.csv_handler import read_csv, write_csv
from utils.config import INPUT_CSV, OUTPUT_CSV, BULK_PDF_FILE

def main():
    # Read shipment data from CSV
    shipment_data = read_csv(INPUT_CSV)

    # Process shipments and collect results
    results, pdf_files = process_shipments(shipment_data)

    # Write results back to a new CSV
    fieldnames = list(shipment_data[0].keys()) + ["tracking_number", "carrier", "shipment_level", "price", "label_path", "error_message"]
    write_csv(OUTPUT_CSV, fieldnames, results)

    print(f"Processed shipments. Results written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()