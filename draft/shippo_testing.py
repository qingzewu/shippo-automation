import shippo
from shippo.models import components

# Initialize Shippo SDK with the API key
shippo_sdk = shippo.Shippo(api_key_header="shippo_test_7b8cc24c4c879f92ed2297befec123915b47c39d")

# Define the main function
def create_address():
    # Create an address using Shippo API
    try:
        address = shippo_sdk.addresses.create(
            components.AddressCreateRequest(
                name="Shawn Ippotle",
                company="Shippo",
                street1="215 Clayton St.",
                city="San Francisco",
                state="CA",
                zip="94117",
                country="US",  # ISO2 country code
                phone="+1 555 341 9393",
                email="shippotle@shippo.com"
            )
        )
        print("Address created successfully:", address)
    except Exception as e:
        print("Error creating address:", str(e))
