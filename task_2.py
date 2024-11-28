import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

barcodes = [
    "8885020500158", "0745178218665", "5056080608822",
    "5056080613413", "5056080613475", "6159084322211",
    "796554957180", "8720246543087", "4063846017942",
    "5056080613017", "5056080615321"
]

output_dir = "задание_2"
os.makedirs(output_dir, exist_ok=True)

not_found = []

base_url = "https://minim.kz/poisk?filter_name="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

session = requests.Session()

def download_images(barcode, img_urls):
    folder_path = os.path.join(output_dir, barcode)
    os.makedirs(folder_path, exist_ok=True)

    for idx, img_url in enumerate(img_urls, start=1):
        img_data = session.get(img_url, headers=headers).content
        img_name = f"{barcode}-{idx}.jpg"
        with open(os.path.join(folder_path, img_name), "wb") as img_file:
            img_file.write(img_data)

for barcode in barcodes:
    print(f"Processing barcode: {barcode}")
    search_url = base_url + barcode
    try:
        response = session.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        if "410 Gone" in response.text:
            print(f"Barcode {barcode} returned 410 Gone. Skipping...")
            not_found.append(barcode)
            continue

        product_link = soup.select_one("a.c-product-item__link")
        if not product_link:
            print(f"Barcode {barcode} not found.")
            not_found.append(barcode)
            continue

        product_url = urljoin(base_url, product_link["href"])
        product_response = session.get(product_url, headers=headers)
        product_soup = BeautifulSoup(product_response.text, "html.parser")

        img_tags = product_soup.select("img.c-product-info__image-img")
        img_urls = [img["src"] for img in img_tags if "src" in img.attrs]

        if not img_urls:
            print(f"No images found for barcode {barcode}.")
            not_found.append(barcode)
            continue

        print(f"Found {len(img_urls)} images for barcode {barcode}. Downloading...")
        download_images(barcode, img_urls)

    except Exception as e:
        print(f"Error processing barcode {barcode}: {e}")
        not_found.append(barcode)

if not_found:
    with open(os.path.join(output_dir, "not_found.txt"), "w") as f:
        f.write("\n".join(not_found))

print("Task completed.")