from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from bs4 import BeautifulSoup

import re
from dotenv import load_dotenv
import os
import googlemaps
import sqlite3

load_dotenv()

api_key = os.getenv('GMAP_KEY')
gmaps = googlemaps.Client(key=api_key)

# Install (if haven't installe) and get ChromeDriver path
driver_path = chromedriver_autoinstaller.install()
print(driver_path)
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

try:
    # Open Subway Malaysia store locator page
    url = "https://subway.com.my/find-a-subway"
    driver.get(url)
    
    driver.execute_script("document.getElementById('fp_searchAddress').value = 'Kuala Lumpur';")
    driver.execute_script("document.getElementById('fp_searchAddressBtn').click();")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the first `fp_ll_holder` div
    wait = WebDriverWait(driver, 20)
    div = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fp_ll_holder")))[0]

    html = div.get_attribute('innerHTML')
    soup = BeautifulSoup(html, "html.parser")

    # Find all `fp_listitem` divs
    list_items = soup.find_all("div", class_="fp_listitem")

    stores = []

    for item in list_items:
        store_data = {}
        #store_data['latitude'] = item.get('data-latitude')
        #store_data['longitude'] = item.get('data-longitude')

        # Extract Store Name
        name_tag = item.find("h4")
        store_data["name"] = name_tag.text.strip() if name_tag else "N/A"

        # Extract Address & Opening Hours
        paragraphs = item.find("div", class_="infoboxcontent").find_all("p")
        address = []
        hours = []

        #day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        #day_short = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']

        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and "Find out more" not in text:
                address_pattern = r'[\w\s\W]+,?[\w\s\W]+ \d{5}'
                #if "AM" in text or "PM" in text or any(d in text for d in day) or any(d in text for d in day_short):
                #    hours.append(text)  # Considered as opening hours
                #else:
                #    address.append(text)  # Considered as address

                if re.search(address_pattern, text):
                    address.append(text)
                else:
                    hours.append(text)

        store_data["address"] = " ".join(address) if address else "N/A"
        store_data["opening_hours"] = " , ".join(hours) if hours else "N/A"

        # Extract Google Maps & Waze Links
        links = item.find("div", class_="location_right").find_all("a")
        for link in links:
            href = link.get("href")
            if "maps" in href:
                store_data["google_maps"] = href
            elif "waze" in href:
                store_data["waze"] = href

        stores.append(store_data)
    
    conn = sqlite3.connect('subway_store.db')
    cursor = conn.cursor()

    sql_query = """

    INSERT INTO subway (outlet_name, address, opening_hours, waze_link, gmaps_link, latitude, longitude)
    VALUES (?,?,?,?,?,?,?)

    """

    
    for store in stores:
        if 'K.L' in store['address'] or 'Kuala Lumpur' in store['address']:
            geocode_result = gmaps.geocode(store['address'])[0]['geometry']['location']

            latitude = geocode_result['lat'] if geocode_result else 'N/A'
            longitude = geocode_result['lng'] if geocode_result else 'N/A'

            cursor.execute(sql_query, (store['name'], store['address'], store['opening_hours'], store.get('waze', 'N/A'),  store.get('google_maps', 'N/A'), latitude, longitude))

    conn.commit()
    conn.close()

    
finally:
    driver.quit()  # Close the browser
