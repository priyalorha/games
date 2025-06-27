import pandas as pd
import concurrent.futures
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ---------- CONFIG ----------
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
MAX_WORKERS = 3
REQUEST_DELAY = (1, 3)
MAX_RETRIES = 2

# ---------- Load CSV ----------
df = pd.read_csv("doctor_links.csv", header=None, names=["State", "DoctorProfileURL"]).drop_duplicates(
    subset="DoctorProfileURL")
print(f"Total profiles to scrape: {len(df)}")

results = []
errors = []


# ---------- Address Parser (Simplified since we have state) ----------
def parse_address(address_raw):
    if not address_raw:
        return '', '', ''

    # Clean HTML and normalize
    soup = BeautifulSoup(address_raw.replace("<br>", "\n").replace("<br/>", "\n"), "html.parser")
    address_text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in address_text.split('\n') if line.strip()]

    street = ''
    city = ''
    postcode = ''

    try:
        if lines:
            street = lines[0]

            # Last line typically contains city and postcode
            if len(lines) > 1:
                last_line = lines[-1]

                # Handle cases like "Birmingham, AL 35205" or "Birmingham 35205"
                if ',' in last_line:
                    city_part, postcode_part = last_line.rsplit(',', 1)
                    city = city_part.strip()
                    # Extract just the postcode (5 digits)
                    postcode = ''.join(filter(str.isdigit, postcode_part))[:5]
                else:
                    # Try to extract postcode from end (5 digits)
                    postcode = ''.join(filter(str.isdigit, last_line))[-5:]
                    city = last_line.replace(postcode, '').strip().rstrip(',')

    except Exception as e:
        print(f"Address parsing error: {e}")

    return street, city, postcode


# ---------- Create Browser Instance ----------
def create_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


# ---------- Profile Scraper ----------
def scrape_profile(row):
    url = row["DoctorProfileURL"]
    state = row["State"]  # Using the state from CSV

    time.sleep(random.uniform(*REQUEST_DELAY))
    driver = None

    for attempt in range(MAX_RETRIES):
        try:
            driver = create_browser()
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.element-data"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Parse all data fields
            data = {}
            for tr in soup.find_all('tr'):
                label = tr.find('td', class_='element-label')
                value = tr.find('td', class_='element-data')
                if label and value:
                    key = label.get_text(strip=True)
                    val = value.get_text(" ", strip=True)
                    data[key] = val

            # Extract name
            name_tag = soup.find("h2") or soup.find("h1")
            if not name_tag:
                raise ValueError("Could not find name element")

            # working as expected, do not touch

            title = ''
            full_name = ''
            forename = ''
            surname = ''
            try:
                name_tag = name_tag.get_text(strip=True)
                if '  ' in name_tag:
                    name_text = name_tag.replace(',', ' ').split("  ")
                    title = name_text[1] if len(name_tag) > 1 else ''
                    # Handle name components
                    full_name = name_text[0].split()
                    forename = " ".join(full_name[:-1]) if len(full_name) > 1 else ""
                    surname = full_name[-1] if full_name else ""

                else:
                    name_tag = name_tag.rsplit(',', 1)
                    title = name_tag[1]
                    full_name = name_text[0].split()
                    forename = " ".join(full_name[:-1]) if len(full_name) > 1 else ""
                    surname = full_name[-1] if full_name else ""
            except Exception as e:
                print(name_tag)
                forename = name_tag


            # Parse address (using state from CSV)
            address_raw = data.get("Practice Address", "").strip()

            street = ''
            city = ''
            pincode = ''
            try:
                if '\n' in address_raw:

                    address_new = address_raw.split('\n')
                    street = address_new[0]
                    city_state_info = address_new[1].split(',')
                    city = city_state_info[0]
                    pincode = city_state_info[1].split(' ')[1]

                elif ',' in address_raw:

                    address_new = address_raw.rsplit(',', 1)
                    pincode = address_new[1].split(' ')[1]
                    for i in reversed(range(len(address_new[0]))):
                        if i == ' ' or i == '\n':
                            city = address_new[0][i:]
                            street = address_new[0][:i]

            except Exception as e:
                print(e, address_raw)

            # Build result
            result = {
                "title": title,
                "forename": forename,
                "surname": surname,

                "full_address": data.get("Practice Address", ""),
                "institution": data.get("Practice Name", ""),
                "department": data.get("Specialty", ""),
                "street": street,
                "city": city,
                "state": state,  # Using the state from CSV
                "postcode": pincode,
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

            return result

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if driver:
                try:
                    screenshot_path = f"error_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved: {screenshot_path}")
                except:
                    pass

            if attempt < MAX_RETRIES - 1:
                time.sleep(5)

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    # If all retries failed
    errors.append({
        "url": url,
        "state": state
    })
    return None


# ---------- Main Execution ----------
if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(scrape_profile, row) for _, row in df.iterrows()]

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            if result:
                results.append(result)
            if i % 10 == 0:
                print(f"Processed {i} profiles...")
                time.sleep(5)

    # ---------- Save Results ----------
    if results:
        output_df = pd.DataFrame(results)
        output_df.to_csv("doctors_details.csv", index=False)
        print(f"✅ Successfully saved {len(results)} profiles.")

    if errors:
        error_df = pd.DataFrame(errors)
        error_df.to_csv("scraping_errors.csv", index=False)
        print(f"⚠️ Encountered {len(errors)} errors. Saved to scraping_errors.csv.")

    print("🎉 Scraping complete.")
