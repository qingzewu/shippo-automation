import csv

def read_csv(file_path):
    """Reads the CSV file and returns a list of shipment data."""
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def write_csv(file_path, fieldnames, data):
    """Writes data to a CSV file."""
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)