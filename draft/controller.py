import csv
import requests
from PyPDF2 import PdfMerger
import os
import shippo
from shippo.models import components

# Initialize Shippo SDK
shippo_sdk = shippo.Shippo(api_key_header="shippo_test_7b8cc24c4c879f92ed2297befec123915b47c39d")

# File paths
input_csv = "shipments.csv"
output_csv = "shipments_with_tracking.csv"
labels_dir = "labels"
bulk_pdf_file = "bulk_labels.pdf"

# Ensure labels directory exists
os.makedirs(labels_dir, exist_ok=True)

def read_csv(file_path):
    """Reads the CSV file and returns a list of shipment data."""
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

def write_csv(file_path, fieldnames, data):
    """Writes data to a CSV file."""
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def download_label(label_url, file_name):
    """Downloads a label from the given URL."""
    response = requests.get(label_url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(labels_dir, file_name)
        with open(file_path, 'wb') as label_file:
            label_file.write(response.content)
        return file_path
    else:
        raise Exception(f"Failed to download label: {label_url}")

def process_shipments(shipment_data):
    """Processes shipments in bulk."""
    results = []
    pdf_files = []
    for index, row in enumerate(shipment_data):
        try:
            # Create address objects
            address_from = components.AddressCreateRequest(
                name=row["name_from"],
                street1=row["street1_from"],
                city=row["city_from"],
                state=row["state_from"],
                zip=row["zip_from"],
                country=row["country_from"]
            )
            address_to = components.AddressCreateRequest(
                name=row["name_to"],
                street1=row["street1_to"],
                city=row["city_to"],
                state=row["state_to"],
                zip=row["zip_to"],
                country=row["country_to"]
            )

            # Create parcel object
            parcel = components.ParcelCreateRequest(
                length=row["length"],
                width=row["width"],
                height=row["height"],
                distance_unit=components.DistanceUnitEnum[row["length_unit"]],
                weight=row["weight"],
                mass_unit=components.WeightUnitEnum[row["unit"]]
            )

            # Create shipment
            shipment = shippo_sdk.shipments.create(
                components.ShipmentCreateRequest(
                    address_from=address_from,
                    address_to=address_to,
                    parcels=[parcel],
                    async_=False
                )
            )

            # Get the first rate and purchase the label
            rate = shipment.rates[0]  # Customize to select rate based on business logic
            transaction = shippo_sdk.transactions.create(
                components.TransactionCreateRequest(
                    rate=rate.object_id,
                    label_file_type=components.LabelFileTypeEnum.PDF,
                    async_=False
                )
            )

            if transaction.status == "SUCCESS":
                # Use label URL directly
                label_url = transaction.label_url

                # Optionally download the label for local storage
                label_file_name = f"label_{index + 1}.pdf"
                pdf_files.append(download_label(label_url, label_file_name))

                # Append results
                results.append({
                    **row,  # Original data
                    "tracking_number": transaction.tracking_number,
                    "carrier": rate.provider,
                    "shipment_level": rate.servicelevel.name,
                    "price": rate.amount,
                    "label_path": label_url
                })
            else:
                results.append({
                    **row,  # Original data
                    "tracking_number": "ERROR",
                    "carrier": "ERROR",
                    "shipment_level": "ERROR",
                    "price": "ERROR",
                    "label_path": "ERROR",
                    "error_message": transaction.messages
                })
        except Exception as e:
            results.append({
                **row,  # Original data
                "tracking_number": "ERROR",
                "carrier": "ERROR",
                "shipment_level": "ERROR",
                "price": "ERROR",
                "label_path": "ERROR",
                "error_message": str(e)
            })
    return results, pdf_files

def merge_pdfs(pdf_files, output_file):
    """Merges multiple PDF files into one."""
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()

def main():
    # Read shipment data from CSV
    shipment_data = read_csv(input_csv)

    # Process shipments and collect results
    results, pdf_files = process_shipments(shipment_data)

    # Merge PDFs into a bulk file
    if pdf_files:
        merge_pdfs(pdf_files, bulk_pdf_file)
        print(f"Bulk PDF created: {bulk_pdf_file}")

    # Write results back to a new CSV
    fieldnames = list(shipment_data[0].keys()) + ["tracking_number", "carrier", "shipment_level", "price", "label_path", "error_message"]
    write_csv(output_csv, fieldnames, results)

    print(f"Processed shipments. Results written to {output_csv}")

if __name__ == "__main__":
    main()