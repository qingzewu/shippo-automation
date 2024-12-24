import shippo
import logging
from shippo.models import components
from controllers.label_downloader import download_label
from utils.config import Shippo_API_KEY_LIVE as SHIPPO_API_KEY

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Shippo SDK
shippo_sdk = shippo.Shippo(api_key_header=SHIPPO_API_KEY)

def process_shipments(shipment_data):
    """Processes shipments in bulk based on the new CSV format."""
    results = []
    pdf_files = []

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
            logging.info(f"Processing shipment {index + 1} for {row['Recipient Name']}")

            # Create recipient address (address_to)
            address_to = components.AddressCreateRequest(
                name=row["Recipient Name"],
                email=row["Email"],
                phone=row["Phone"],
                street1=row["Street Line 1"],
                street2=row["Street Line 2"] if row["Street Line 2"] else None,
                city=row["City"],
                state=row["State/Province"],
                zip=row["Zip/Postal Code"],
                country=row["Country"]
            )

            # Create parcel object based on item details
            parcel = components.ParcelCreateRequest(
                length=6,  # Assuming a default length (adjust if needed)
                width=6,   # Default width
                height=2,  # Default height
                distance_unit=components.DistanceUnitEnum.IN,
                weight=row["Item Weight"],
                mass_unit=components.WeightUnitEnum[row["Item Weight Unit"]]
            )

            # Create shipment with hardcoded address_from
            logging.debug("Creating shipment...")
            shipment = shippo_sdk.shipments.create(
                components.ShipmentCreateRequest(
                    address_from=address_from,
                    address_to=address_to,
                    parcels=[parcel],
                    async_=False
                )
            )
            logging.info(f"Shipment created successfully for {row['Recipient Name']}.")

            # Log available rates
            # logging.debug("Available rates:")
            for rate in shipment.rates:
                continue
                # logging.debug(
                #     f"Provider: {rate.provider}, "
                #     f"Service Level: {rate.servicelevel.name}, "
                #     f"Price: {rate.amount} {rate.currency}"
                # )

            # Find USPS Ground Advantage rate
            usps_ground_advantage_rate = None
            for rate in shipment.rates:
                if rate.provider == "USPS" and rate.servicelevel.name == "Ground Advantage":
                    usps_ground_advantage_rate = rate
                    break

            # Raise an error if USPS Ground Advantage is not available
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

            # Handle success
            if transaction.status == "SUCCESS":
                label_url = transaction.label_url
                pdf_files.append(download_label(label_url, f"label_{index + 1}.pdf"))
                logging.info(f"Label purchased successfully. Tracking number: {transaction.tracking_number}")

                # Append shipment details to results
                results.append({
                    **row,
                    "tracking_number": transaction.tracking_number,
                    "carrier": usps_ground_advantage_rate.provider,
                    "shipment_level": usps_ground_advantage_rate.servicelevel.name,
                    "price": usps_ground_advantage_rate.amount,
                    "label_path": label_url
                })
            else:
                # Handle transaction failure
                error_message = transaction.messages
                logging.error(f"Label purchase failed: {error_message}")
                raise Exception(f"Label purchase failed for {row['Recipient Name']}: {error_message}")

        except Exception as e:
            # Log recipient-specific error and stop the program
            error_message = f"Error processing shipment {index + 1} for {row['Recipient Name']}: {str(e)}"
            logging.error(error_message)

            # Raise an exception to stop processing further shipments
            raise Exception(error_message)

    return results, pdf_files