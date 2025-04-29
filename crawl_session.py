import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()  # allows you to use a local .env file for dev

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

import requests
from bs4 import BeautifulSoup
import re
import datetime
import json
import os

# Target URL
url = "https://www.capitol.hawaii.gov/advreports/advreport.aspx?year=2025&report=deadline&active=true&rpt_type=&measuretype=hb&title=House%20Bills%20Introduced"

# Request page
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Prepare data
bill_data = []

rows = soup.select("table#ctl00_ContentPlaceHolder1_gridMain tr")[1:]  # skip header row

for row in rows:
    cols = row.find_all("td")
    if len(cols) >= 8:
        bill_number = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)
        current_referral = cols[2].get_text(strip=True)
        intro_date = cols[4].get_text(strip=True)
        current_status = cols[5].get_text(strip=True)
        status_date = cols[6].get_text(strip=True)
        last_action = cols[7].get_text(strip=True)

        committees = re.findall(r'\b[A-Z]{2,4}\b', current_referral)

        bill_data.append({
            "bill_number": bill_number,
            "title": title,
            "description": last_action,
            "year": 2025,
            "committees": committees,
            "status": current_status,
            "hearings": [],  # not available on this summary page
            "testimony_link": f"https://www.capitol.hawaii.gov/measure_submittestimony.aspx?billtype={bill_number[:2]}&billnumber={bill_number[2:]}&year=2025",
            "link": f"https://www.capitol.hawaii.gov/measure_indiv.aspx?billtype={bill_number[:2]}&billnumber={bill_number[2:]}&year=2025",
            "last_updated": datetime.datetime.now().isoformat()
        })

# Save to file or print
os.makedirs("scraped_data", exist_ok=True)
now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
with open(f"scraped_data/hb_bills_{now}.json", "w") as f:
    json.dump(bill_data, f, indent=2)

print(f"✅ Scraped {len(bill_data)} House bills successfully.")

