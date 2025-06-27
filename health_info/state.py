import pandas as pd
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import random

# Load URLs from CSV (no headers)
df = pd.read_csv("doctor_links.csv", header=None, names=["State", "DoctorProfileURL"]).drop_duplicates(
    subset="DoctorProfileURL")

print(f"Actual length: {len(df)}")

# For storing extracted doctor data
results = []

# Common headers to avoid 403 Forbidden
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


def scrape_profile(row):
    url = row["DoctorProfileURL"]
    state = row["State"]

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        data = {}
        for tr in soup.find_all('tr'):
            label = tr.find('td', class_='element-label')
            value = tr.find('td', class_='element-data')
            if label and value:
                key = label.get_text(strip=True)
                val = value.get_text(" ", strip=True)
                data[key] = val

        name_tag = soup.find("h2", {"id": "title-position"})
        if not name_tag:
            return None

        full_name = name_tag.get_text(strip=True)
        doctor_name = full_name.split()
        if len(doctor_name) < 3:
            return None

        address_raw = data.get("Practice Address", "")
        address_cleaned = BeautifulSoup(address_raw.replace("<br>", " "), "html.parser").get_text(" ", strip=True)
        address_parts = address_cleaned.split()

        street = " ".join(address_parts[:-3]) if len(address_parts) >= 3 else ""
        city = address_parts[-3] if len(address_parts) >= 3 else ""
        state_postcode = address_parts[-2] if len(address_parts) >= 2 else ""
        postcode = address_parts[-1] if len(address_parts) >= 1 else ""
        state_from_addr = state_postcode.split()[0] if state_postcode else ""

        # Optional random delay (politeness)
        time.sleep(random.uniform(0.5, 1.5))

        return {
            "title": doctor_name[-1],
            "forename": " ".join(doctor_name[0:-2]),
            "surname": doctor_name[-2],
            "institution": data.get("Practice Name", ""),
            "department": data.get("Specialty", ""),
            "street": street,
            "city": city,
            "state": state_from_addr or state,
            "postcode": postcode,
            "country": "United States",
            "specialty": data.get("Specialty", ""),
            "reg_number": "",
            "tel_1": data.get("Phone", ""),
            "tel_2": "",
            "tel_3": "",
            "fax_1": "",
            "fax_2": "",
            "fax_3": "",
            "mobile": "",
            "email_1": "",
            "email_2": "",
            "language": "",
            "gender": "",
            "workplace": data.get("Practice Name", ""),
            "website": data.get("Website", ""),
            "source_result_url": url
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


# Multithreading execution
with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    futures = [executor.submit(scrape_profile, row) for _, row in df.iterrows()]
    for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
        result = future.result()
        if result:
            results.append(result)
        print(f"Processed {i}/{len(futures)}")

# Save to CSV
output_df = pd.DataFrame(results)
output_df.to_csv("scraped_doctor_details.csv", index=False)
print("Scraping complete. Saved to scraped_doctor_details.csv")
