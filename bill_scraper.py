import requests
from bs4 import BeautifulSoup
import re
import datetime
from config import base_url, headers, session_year
from utils import log_error

def scrape_bill(bill_type, bill_number):
    url = f"{base_url}/session/measure_indiv.aspx?billtype={bill_type}&billnumber={bill_number}&year={session_year}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("span", id="ctl00_ContentPlaceHolder1_lblMeasureTitle").text.strip()
        description = soup.find("span", id="ctl00_ContentPlaceHolder1_lblReportTitle").text.strip()

        referral_text = soup.find("span", id="ctl00_ContentPlaceHolder1_lblReferral").text.strip()
        committees = re.findall(r'\b[A-Z]{2,4}\b', referral_text)

        hearing_divs = soup.find_all("div", class_="hearingNotice")
        hearings = []
        for div in hearing_divs:
            text = div.get_text(" ", strip=True)
            match = re.search(r"(.*?) Hearing.*?(\w+day), (\w+ \d{1,2}, \d{4}), (\d{1,2}:\d{2} [APMapm\.]+)", text)
            if match:
                hearings.append({
                    "committee": match.group(1).strip(),
                    "date": match.group(3),
                    "time": match.group(4),
                    "location": "Check full notice"
                })

        if hearings:
            status = f"Scheduled for {['first', 'second', 'last'][min(len(hearings), 3)-1]} committee hearing"
        elif committees:
            status = "Waiting to be scheduled for first committee hearing"
        else:
            status = "No committees assigned yet"

        testimony_link_tag = soup.find("a", href=re.compile("measure_submittestimony.aspx"))
        if testimony_link_tag:
            testimony_link = base_url + "/" + testimony_link_tag['href'].lstrip("/")
        else:
            testimony_link = f"{base_url}/measure_submittestimony.aspx?billtype={bill_type}&billnumber={bill_number}&year={session_year}"

        return {
            "bill_number": f"{bill_type}{bill_number}",
            "year": session_year,
            "title": title,
            "description": description,
            "committees": committees,
            "hearings": hearings,
            "status": status,
            "link": url,
            "testimony_link": testimony_link,
            "last_updated": datetime.datetime.now().isoformat()
        }

    except Exception as e:
        log_error(f"Error scraping {bill_type}{bill_number}: {e}")
        return None
