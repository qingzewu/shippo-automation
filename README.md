# Shippo Automation

shippo-automation is a Python-based automation tool designed to streamline the process of managing shipments, generating shipping labels, and retrieving tracking information using the Shippo API. It simplifies bulk shipment handling and provides CSV-based input/output workflows, allowing for seamless integration into existing systems.

Features
	•	Read shipment details from an input CSV file.
## Features
- Read shipment details from an input CSV file.
- Create shipments in bulk using the Shippo API.
- Generate shipping labels and download them as PDFs.
- Merge all shipping labels into a single bulk PDF for easy printing.
- Write back tracking details (tracking number, carrier, service level, and price) to the output CSV.
- Flexible configuration for parcel dimensions and units (e.g., cm, inches).

## Project Structure

### Input CSV (data/shipments.csv)

Column	Description
name_from	Name of the sender
street1_from	Street address of the sender
city_from	City of the sender
state_from	State of the sender
zip_from	ZIP code of the sender
country_from	Country of the sender (ISO2 code)
name_to	Name of the recipient
street1_to	Street address of the recipient
city_to	City of the recipient
state_to	State of the recipient
zip_to	ZIP code of the recipient
country_to	Country of the recipient (ISO2 code)
length	Length of the parcel
width	Width of the parcel
height	Height of the parcel
weight	Weight of the parcel
unit	Weight unit (e.g., LB, KG)
length_unit	Dimension unit (e.g., IN, CM)

Output CSV (data/shipments_with_tracking.csv)

### Output CSV (data/shipments_with_tracking.csv)

Column	Description
tracking_number	Tracking number for the shipment
carrier	Carrier used for the shipment
shipment_level	Service level (e.g., Ground, Express)
price	Price of the shipment
label_path	URL to the shipping label PDF
error_message	Any error messages during processing

Setup and Installation

## Setup and Installation

### Requirements
- Python 3.7+
- Dependencies (listed in requirements.txt):
  - requests
  - PyPDF2
  - shippo

### Installation
1. Clone the repository:
cd shippo-automation


	2.	Create a virtual environment:

	2. Create a virtual environment:
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


	3.	Install dependencies:

	3. Install dependencies:

Usage

## Usage

Update the data/shipments.csv file with shipment details.

2. Run the Project

Execute the project with:

python main.py

3. Outputs
	•	Processed CSV: After processing, check the data/shipments_with_tracking.csv file for tracking numbers, carrier details, and shipping costs.
	•	Shipping Labels:
	•	Individual labels are downloaded to the labels/ directory.
	•	All labels are merged into a single PDF: bulk_labels.pdf.

Configuration

## Configuration

Update your Shippo API key in utils/config.py:

SHIPPO_API_KEY = "your_shippo_api_key"

Customizing Units

Ensure the unit and length_unit fields in your input CSV match valid options:
	•	unit: Use LB for pounds or KG for kilograms.
	•	length_unit: Use IN for inches or CM for centimeters.

Error Handling
	•	Any errors during shipment creation or label generation are logged in the error_message column of the output CSV.
	•	Failed shipments will not have tracking numbers, carriers, or labels.

Example Workflow

## Example Workflow

name_from,street1_from,city_from,state_from,zip_from,country_from,name_to,street1_to,city_to,state_to,zip_to,country_to,length,width,height,weight,unit,length_unit
Shawn Ippotle,215 Clayton St.,San Francisco,CA,94117,US,Mr Hippo,123 Broadway 1,New York,NY,10007,US,5,5,5,2,LB,IN
Jane Doe,456 Main St.,Los Angeles,CA,90001,US,John Smith,789 Park Ave,Chicago,IL,60601,US,12,10,8,5,KG,CM

2. Run the Project

python main.py

3. Output CSV

name_from,street1_from,city_from,state_from,zip_from,country_from,name_to,street1_to,city_to,state_to,zip_to,country_to,length,width,height,weight,unit,length_unit,tracking_number,carrier,shipment_level,price,label_path
Shawn Ippotle,215 Clayton St.,San Francisco,CA,94117,US,Mr Hippo,123 Broadway 1,New York,NY,10007,US,5,5,5,2,LB,IN,1Z9999W99999999999,UPS,Ground,8.29,https://deliver.goshippo.com/7e6521d082f8492b939b92c124bc20ea.pdf
Jane Doe,456 Main St.,Los Angeles,CA,90001,US,John Smith,789 Park Ave,Chicago,IL,60601,US,12,10,8,5,KG,CM,ERROR,ERROR,ERROR,ERROR,ERROR

4. Bulk PDF

Check bulk_labels.pdf in the project root for a merged PDF of all labels.


## License

This project is licensed under the MIT License. See the LICENSE file for details.