import shippo
from shippo.models import components
from controllers.label_downloader import download_label
from utils.config import SHIPPO_API_KEY

# Initialize Shippo SDK
shippo_sdk = shippo.Shippo(api_key_header=SHIPPO_API_KEY)

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
            rate = shipment.rates[0]
            transaction = shippo_sdk.transactions.create(
                components.TransactionCreateRequest(
                    rate=rate.object_id,
                    label_file_type=components.LabelFileTypeEnum.PDF,
                    async_=False
                )
            )

            if transaction.status == "SUCCESS":
                label_url = transaction.label_url
                pdf_files.append(download_label(label_url, f"label_{index + 1}.pdf"))

                results.append({
                    **row,
                    "tracking_number": transaction.tracking_number,
                    "carrier": rate.provider,
                    "shipment_level": rate.servicelevel.name,
                    "price": rate.amount,
                    "label_path": label_url
                })
            else:
                results.append({
                    **row,
                    "tracking_number": "ERROR",
                    "carrier": "ERROR",
                    "shipment_level": "ERROR",
                    "price": "ERROR",
                    "label_path": "ERROR",
                    "error_message": transaction.messages
                })
        except Exception as e:
            results.append({
                **row,
                "tracking_number": "ERROR",
                "carrier": "ERROR",
                "shipment_level": "ERROR",
                "price": "ERROR",
                "label_path": "ERROR",
                "error_message": str(e)
            })

    return results, pdf_files