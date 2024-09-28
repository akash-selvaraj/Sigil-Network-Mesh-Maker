import requests
import base64
from PIL import Image
from io import BytesIO

def fetch_and_save_heatmaps(url):
    try:
        # Make the GET request to fetch the heatmap data
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Check for error in the response
        if 'error' in data:
            print(f"Error: {data['error']}")
            return

        # Decode the upload heatmap image
        img_data_upload = base64.b64decode(data['upload_heatmap_image'])
        img_upload = Image.open(BytesIO(img_data_upload))

        # Save the upload heatmap as a PNG file
        img_upload.save("upload_heatmap.png")
        print("Upload heatmap saved as 'upload_heatmap.png'")

        # Decode the download heatmap image
        img_data_download = base64.b64decode(data['download_heatmap_image'])
        img_download = Image.open(BytesIO(img_data_download))

        # Save the download heatmap as a PNG file
        img_download.save("download_heatmap.png")
        print("Download heatmap saved as 'download_heatmap.png'")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
url = 'http://localhost:5000/get_heatmap'  # Replace with the actual URL of your endpoint
fetch_and_save_heatmaps(url)
