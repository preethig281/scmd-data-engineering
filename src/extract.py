import requests

# Stable identifiers for the SCMD May 2026 resource
RESOURCE_ID = "673cd266-20af-4535-bfaa-08feab0d7ed2"
API_URL = "https://opendata.nhsbsa.net/api/3/action/resource_show"
OUTPUT_PATH = "data/raw/scmd_provisional_202605.csv"


def download_scmd():
    """Fetch the SCMD CSV's current download URL from the CKAN API, then save the file."""

    # 1. Ask the API for the resource info
    response = requests.get(API_URL, params={"id": RESOURCE_ID})
    response.raise_for_status()  # stops here if the API call failed (e.g. 404)

    data = response.json()
    if not data.get("success"):
        raise Exception("API did not return success")

    # 2. Pull the download URL out of the response
    download_url = data["result"]["url"]
    expected_size = data["result"]["size"]
    print("Download URL:", download_url)

    # 3. Download the CSV
    print("Downloading... this may take a moment for a 35 MB file")
    csv_response = requests.get(download_url)
    csv_response.raise_for_status()

    # 4. Save it to data/raw/
    with open(OUTPUT_PATH, "wb") as f:
        f.write(csv_response.content)

    actual_size = len(csv_response.content)
    print("Saved to", OUTPUT_PATH)
    print("File size:", actual_size, "bytes")

    # 5. Sanity check: does the size match what the API promised?
    if actual_size != expected_size:
        print("WARNING: size mismatch! Expected", expected_size)
    else:
        print("Size matches API — download verified.")


if __name__ == "__main__":
    download_scmd()