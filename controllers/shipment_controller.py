import shippo
import logging
from shippo.models import components
from controllers.label_downloader import download_label
from utils.config import SHIPPO_API_KEY_TEST as SHIPPO_API_KEY

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Shippo SDK
shippo_sdk = shippo.Shippo(api_key_header=SHIPPO_API_KEY)

def process_shipments(shipment_data):
    """Processes shipments in bulk based on the provided data."""
    results = []
    pdf_files = []
    errors = []

    # Hardcoded address_from details
    address_from = components.AddressCreateRequest(
        name="Wu",
        email="michaelqwu123@gmail.com",
        phone="+1 909 551 9764",
        street1="14989 Redwood Ln",
        city="Chino Hills",
        state="CA",
        zip="91709",
        country="US"
    )

    for index, row in enumerate(shipment_data):
        try:
            recipient_name = row.get("Recipient Name", "Unknown")
            logging.info(f"Processing shipment {index + 1} for {recipient_name}")

            # Validate required fields
            required_fields = ["Recipient Name", "Street Line 1", "City", "State/Province",
                               "Zip/Postal Code", "Country", "Item Weight", "Item Weight Unit"]
            missing_fields = [field for field in required_fields if field not in row or not row[field]]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Create recipient address (address_to)
            address_to = components.AddressCreateRequest(
                name=row["Recipient Name"],
                email=row.get("Email", ""),
                phone=row.get("Phone", ""),
                street1=row["Street Line 1"],
                street2=row.get("Street Line 2", None),
                city=row["City"],
                state=row["State/Province"],
                zip=row["Zip/Postal Code"],
                country=row["Country"]
            )

            # Create parcel object based on item details
            parcel = components.ParcelCreateRequest(
                length=6,  # Default length
                width=6,   # Default width
                height=2,  # Default height
                distance_unit=components.DistanceUnitEnum.IN,
                weight=row["Item Weight"],
                mass_unit=components.WeightUnitEnum[row["Item Weight Unit"]]
            )

            # Create shipment with address_from and address_to
            logging.debug("Creating shipment...")
            shipment = shippo_sdk.shipments.create(
                components.ShipmentCreateRequest(
                    address_from=address_from,
                    address_to=address_to,
                    parcels=[parcel],
                    async_=False
                )
            )
            logging.info(f"Shipment created successfully for {recipient_name}.")

            # Find USPS Ground Advantage rate
            usps_ground_advantage_rate = next(
                (rate for rate in shipment.rates if rate.provider == "USPS" and rate.servicelevel.name == "Ground Advantage"),
                None
            )

            if not usps_ground_advantage_rate:
                raise ValueError("USPS Ground Advantage rate not available for this shipment.")

            # Log the selected rate
            logging.info(
                f"Selected rate: {usps_ground_advantage_rate.provider}, "
                f"Service: {usps_ground_advantage_rate.servicelevel.name}, "
                f"Price: {usps_ground_advantage_rate.amount} {usps_ground_advantage_rate.currency}"
            )

            # Purchase the label using the selected rate
            logging.debug("Purchasing label...")
            transaction = shippo_sdk.transactions.create(
                components.TransactionCreateRequest(
                    rate=usps_ground_advantage_rate.object_id,
                    label_file_type="PDF_4x6",
                    async_=False
                )
            )

            if transaction.status == "SUCCESS":
                label_url = transaction.label_url
                label_path = download_label(label_url, f"label_{index + 1}.pdf")
                pdf_files.append(label_path)
                logging.info(f"Label purchased successfully. Tracking number: {transaction.tracking_number}")

                # Combine original row with additional details
                combined_result = {**row}  # Start with all original columns
                combined_result.update({   # Add additional fields
                    "tracking_number": transaction.tracking_number,
                    "carrier": usps_ground_advantage_rate.provider,
                    "shipment_level": usps_ground_advantage_rate.servicelevel.name,
                    "price": usps_ground_advantage_rate.amount,
                    # "label_path": label_url
                })

                # Append to results
                results.append(combined_result)
            else:
                error_message = transaction.messages
                logging.error(f"Label purchase failed for {recipient_name}: {error_message}")
                errors.append(f"Label purchase failed for {recipient_name}: {error_message}")

        except Exception as e:
            # Log and record recipient-specific error
            error_message = f"Error processing shipment {index + 1} for {recipient_name}: {str(e)}"
            logging.error(error_message)
            errors.append(error_message)

    return results, pdf_files, errors
# def process_shipments(shipment_data):
#     """Processes shipments in bulk based on the provided data."""
#     results = []
#     pdf_files = []
#     errors = []

#     # Hardcoded address_from details
#     address_from = components.AddressCreateRequest(
#         name="Wu",
#         email="michaelqwu123@gmail.com",
#         phone="+1 909 551 9764",
#         street1="14989 Redwood Ln",
#         city="Chino Hills",
#         state="CA",
#         zip="91709",
#         country="US"
#     )

#     for index, row in enumerate(shipment_data):
#         try:
#             recipient_name = row.get("Recipient Name", "Unknown")
#             logging.info(f"Processing shipment {index + 1} for {recipient_name}")

#             # Validate required fields
#             required_fields = ["Recipient Name", "Street Line 1", "City", "State/Province",
#                                "Zip/Postal Code", "Country", "Item Weight", "Item Weight Unit"]
#             missing_fields = [field for field in required_fields if field not in row or not row[field]]
#             if missing_fields:
#                 raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

#             # Create recipient address (address_to)
#             address_to = components.AddressCreateRequest(
#                 name=row["Recipient Name"],
#                 email=row.get("Email", ""),
#                 phone=row.get("Phone", ""),
#                 street1=row["Street Line 1"],
#                 street2=row.get("Street Line 2", None),
#                 city=row["City"],
#                 state=row["State/Province"],
#                 zip=row["Zip/Postal Code"],
#                 country=row["Country"]
#             )

#             # Create parcel object based on item details
#             parcel = components.ParcelCreateRequest(
#                 length=6,  # Default length
#                 width=6,   # Default width
#                 height=2,  # Default height
#                 distance_unit=components.DistanceUnitEnum.IN,
#                 weight=row["Item Weight"],
#                 mass_unit=components.WeightUnitEnum[row["Item Weight Unit"]]
#             )

#             # Create shipment with address_from and address_to
#             logging.debug("Creating shipment...")
#             shipment = shippo_sdk.shipments.create(
#                 components.ShipmentCreateRequest(
#                     address_from=address_from,
#                     address_to=address_to,
#                     parcels=[parcel],
#                     async_=False
#                 )
#             )
#             logging.info(f"Shipment created successfully for {recipient_name}.")

#             # Find USPS Ground Advantage rate
#             usps_ground_advantage_rate = next(
#                 (rate for rate in shipment.rates if rate.provider == "USPS" and rate.servicelevel.name == "Ground Advantage"),
#                 None
#             )

#             if not usps_ground_advantage_rate:
#                 raise ValueError("USPS Ground Advantage rate not available for this shipment.")

#             # Log the selected rate
#             logging.info(
#                 f"Selected rate: {usps_ground_advantage_rate.provider}, "
#                 f"Service: {usps_ground_advantage_rate.servicelevel.name}, "
#                 f"Price: {usps_ground_advantage_rate.amount} {usps_ground_advantage_rate.currency}"
#             )

#             # Purchase the label using the selected rate
#             logging.debug("Purchasing label...")
#             transaction = shippo_sdk.transactions.create(
#                 components.TransactionCreateRequest(
#                     rate=usps_ground_advantage_rate.object_id,
#                     label_file_type="PDF_4x6",
#                     async_=False
#                 )
#             )

#             if transaction.status == "SUCCESS":
#                 label_url = transaction.label_url
#                 label_path = download_label(label_url, f"label_{index + 1}.pdf")
#                 pdf_files.append(label_path)
#                 logging.info(f"Label purchased successfully. Tracking number: {transaction.tracking_number}")

#                 # Append shipment details to results
#                 results.append({
#                     **row,
#                     "tracking_number": transaction.tracking_number,
#                     "carrier": usps_ground_advantage_rate.provider,
#                     "shipment_level": usps_ground_advantage_rate.servicelevel.name,
#                     "price": usps_ground_advantage_rate.amount,
#                     "label_path": label_url
#                 })
#             else:
#                 error_message = transaction.messages
#                 logging.error(f"Label purchase failed for {recipient_name}: {error_message}")
#                 errors.append(f"Label purchase failed for {recipient_name}: {error_message}")

#         except Exception as e:
#             # Log and record recipient-specific error
#             error_message = f"Error processing shipment {index + 1} for {recipient_name}: {str(e)}"
#             logging.error(error_message)
#             errors.append(error_message)

#     return results, pdf_files, errors