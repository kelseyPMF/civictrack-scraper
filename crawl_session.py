import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()  # allows you to use a local .env file for dev

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import datetime

from config import base_url, session_year, sleep_between_requests
from bill_scraper import scrape_bill
from utils import log_error

def crawl_session():
    bill_types = ["HB", "SB"]
    all_bills = []

    for bill_type in bill_types:
        list_url = f"{base_url}/measurelist.aspx?year={session_year}&billtype={bill_type}"
        try:
            response = requests.get(list_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            bill_links = soup.find_all("a", href=re.compile("measure_indiv.aspx"))
            for link in bill_links:
                href = link['href']
                match = re.search(r"billtype=(\w+)&billnumber=(\d+)&year=(\d+)", href)
                if match:
                    billtype = match.group(1)
                    billnumber = match.group(2)
                    bill = scrape_bill(billtype, billnumber)
                    if bill:
                        all_bills.append(bill)
                time.sleep(sleep_between_requests)

        except Exception as e:
            log_error(f"Error fetching bill list {bill_type}: {e}")

    # Save output
    output_folder = "scraped_data"
    os.makedirs(output_folder, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_path = os.path.join(output_folder, f"hawaii_bills_{today}.json")
    with open(output_path, "w") as f:
        json.dump(all_bills, f, indent=2)

    print(f"Scraped {len(all_bills)} bills successfully. Data saved to {output_path}")

if __name__ == "__main__":
    crawl_session()
