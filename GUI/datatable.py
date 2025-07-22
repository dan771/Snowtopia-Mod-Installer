import requests
import os
from bs4 import BeautifulSoup
import zipfile
from io import BytesIO
import urllib.parse

def fetch_map_data(url="https://snowtopiamodding.com/maps"):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the main table
    table = soup.find("table")
    if not table:
        raise ValueError("No table found on the page.")

    # Extract headers
    headers = [th.text.strip() for th in table.find_all("th")]

    # Extract rows
    result = []
    for row in table.find("tbody").find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue

        entry = {}
        for idx, cell in enumerate(cells):
            header = headers[idx]
            text = cell.text.strip()

            if header == "Download":
                link = cell.find("a")
                entry[header] = link["href"] if link and link.has_attr("href") else None
            elif header == "Thumbnail":
                img = cell.find("img")
                entry[header] = img["src"] if img and img.has_attr("src") else None
            else:
                entry[header] = text

        result.append(entry)

    return result

def calculate_file_name(download, include_zip):
    suffix = ".zip"
    if (include_zip):
        suffix = ""
    
    return urllib.parse.unquote(download.removeprefix("https://www.mapdownloads.snowtopiamodding.com/").removesuffix(suffix))

def get_all_maps_download_links(precomputed_datatable):
    maps = []
    should_download = []
    for map_data in precomputed_datatable:
        if map_data["Download"].startswith("https://www.mapdownloads.snowtopiamodding.com"):
            maps.append(map_data)

    for downloadable_map in maps:
        filename = calculate_file_name(downloadable_map["Download"], False)
        if os.path.exists(os.path.join("maps", filename)):
            print(filename, "is already downloaded, skipping.")
        else:
            should_download.append(downloadable_map["Download"])
    
    return should_download

def list_to_cfg_line(list):
    string = ""

    for entry in list:
        string += entry + ","
    
    return string.rstrip(",")

def get_top_rated_maps(precomputed_datatable):
    # Filter only maps with a valid download link
    downloadable_maps = [
        m for m in precomputed_datatable
        if m.get("Download", "").startswith("https://www.mapdownloads.snowtopiamodding.com")
    ]

    # Sort by Rating (as float), descending
    sorted_maps = sorted(
        downloadable_maps,
        key=lambda m: float(m.get("Rating", 0)),
        reverse=True
    )

    # Create top-N lists
    top_10 = [calculate_file_name(m["Download"], False) for m in sorted_maps[:10]]
    top_25 = [calculate_file_name(m["Download"], False) for m in sorted_maps[:25]]
    top_50 = [calculate_file_name(m["Download"], False) for m in sorted_maps[:50]]

    return [top_10, top_25, top_50]

def download_map(link):
    # Get the filename from the link
    filename = link.removeprefix("https://www.mapdownloads.snowtopiamodding.com/")
    zip_name = os.path.basename(filename)
    folder_name = urllib.parse.unquote(zip_name.removesuffix(".zip"))

    print(f"Downloading: {zip_name}")
    
    # Make sure maps folder exists
    os.makedirs("maps", exist_ok=True)

    # Download the file
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Failed to download {zip_name}")
        return

    # Save to a temporary zip file
    zip_path = os.path.join("maps", zip_name)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract into maps/<folder_name>
    extract_path = os.path.join("maps", folder_name)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    # Delete the zip file
    os.remove(zip_path)
    print(f"Extracted and cleaned up: {folder_name}")