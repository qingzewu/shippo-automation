import pandas as pd

def read_xlsx(file_path):
    """Reads an XLSX file and returns a list of dictionaries."""
    try:
        df = pd.read_excel(file_path)

        # Convert 'Zip/Postal Code' to string if it exists
        if 'Zip/Postal Code' in df.columns:
            df['Zip/Postal Code'] = df['Zip/Postal Code'].astype(str)

        # Ensure the dataframe is stripped of unnecessary columns
        required_columns = [
            "Recipient Name", "Email", "Phone", "Street Line 1",
            "Street Line 2", "City", "State/Province", "Zip/Postal Code",
            "Country", "SKU", "Quantity", "Item Weight", "Item Weight Unit"
        ]
        extra_columns = set(df.columns) - set(required_columns)
        if extra_columns:
            df = df.drop(columns=list(extra_columns))

        return df.to_dict('records')

    except Exception as e:
        raise ValueError(f"Failed to read XLSX file: {e}")

def write_xlsx(file_path, data, sheet_name="Sheet1"):
    """Writes data to an XLSX file."""
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
    except Exception as e:
        raise ValueError(f"Failed to write XLSX file: {e}")