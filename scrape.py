import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

# -- config --
base_url = "https://www.govtrack.us/congress/bills/118/"
bill_prefixes = ["hr", "s", "hres", "sres", "hjres", "sjres"]
max_bill_number = 400  # adjust for more bills
headers = {"User-Agent": "Mozilla/5.0"}

# -- helper fns --
def check_bill_exists(url):
    # check if a bill page exists (using head req)
    try:
        resp = requests.head(url, allow_redirects=True, headers=headers)
        return resp.status_code == 200
    except Exception as e:
        print(f"error checking {url}: {e}")
        return False

def extract_panel_data(soup):
    # extract property-panel rows as a dict from the overview page
    panel_data = {}
    rows = soup.select("div.property-panel .row")
    for row in rows:
        cols = row.find_all("div", recursive=False)
        if len(cols) >= 2:
            label = cols[0].get_text(strip=True)
            value = cols[1].get_text(separator=" ", strip=True)
            panel_data[label] = value
    return panel_data

def extract_history_status(soup):
    # extract history info from the overview page and return the latest status with date
    history_div = soup.find("div", id="bill-history")
    if not history_div:
        return None
    table = history_div.find("table", id="status-row-grid")
    if not table:
        return None
    rows = table.find_all("tr", class_="status-item")
    latest_date = None
    latest_status = None
    for row in rows:
        date_td = row.find("td", class_=lambda x: x and "date" in x)
        if date_td:
            wrapper = date_td.find("div", class_="wrapper")
            if wrapper:
                span = wrapper.find("span", class_="nowrap")
                if span:
                    date_str = span.text.strip()
                    try:
                        date_obj = datetime.strptime(date_str, "%b %d, %Y")
                    except Exception:
                        continue
                    if (latest_date is None) or (date_obj > latest_date):
                        latest_date = date_obj
                        status_td = row.find("td", class_="status-description")
                        if status_td:
                            status_label_div = status_td.find("div", class_="status-label")
                            if status_label_div:
                                latest_status = status_label_div.text.strip()
    if latest_date and latest_status:
        formatted_date = latest_date.strftime("%b %d, %Y")
        return f"{latest_status} ({formatted_date})"
    return None

# -- scraping fns --
def scrape_overview(bill_url, bill_number):
    # scrape the overview page (no /details) for title, summary, sponsor, cosponsors, and panel data
    try:
        resp = requests.get(bill_url, headers=headers)
        if resp.status_code != 200:
            print(f"failed to fetch overview: {bill_url}")
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # title from h1
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "n/a"
        
        # summary: try to find a <p> with style containing "margin-bottom:"
        summary_tag = soup.find("p", style=lambda v: v and "margin-bottom:" in v)
        summary = summary_tag.text.strip() if summary_tag else "n/a"
        
        # sponsor: first a with class "name" inside an h3
        sponsor_tag = soup.select_one("h3 a.name")
        sponsor = sponsor_tag.text.strip() if sponsor_tag else "n/a"
        
        # cosponsors (overview): find an a tag with href containing "cosponsors"
        cosponsors_tag = soup.find("a", href=lambda x: x and "cosponsors" in x)
        cosponsors_overview = cosponsors_tag.text.strip() if cosponsors_tag else "n/a"
        
        # get panel data
        panel = extract_panel_data(soup)
        introduced = panel.get("Introduced", "n/a")
        status = panel.get("Status", "n/a")
        prognosis = panel.get("Prognosis", "n/a")
        source_url = panel.get("Source", bill_url)
        
        # override status with history info if available
        history_status = extract_history_status(soup)
        if history_status:
            status = history_status
        
        return {
            "Bill Number": bill_number.upper(),
            "Title": title,
            "Summary": summary,
            "Sponsor": sponsor,
            "Cosponsors (Overview)": cosponsors_overview,
            "Introduced": introduced,
            "Status": status,
            "Prognosis": prognosis,
            "Source URL": source_url
        }
    except Exception as e:
        print(f"error scraping overview {bill_url}: {e}")
        return {}

def scrape_details(details_url):
    # scrape the details page (/details) for committees, votes, related bills, and subjects
    try:
        resp = requests.get(details_url, headers=headers)
        if resp.status_code != 200:
            print(f"failed to fetch details: {details_url}")
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # committees: from "committee assignments" section
        committees = "n/a"
        committees_header = soup.find("h2", string=lambda t: t and "committee assignments" in t.lower())
        if committees_header:
            committees_div = committees_header.find_next("div")
            if committees_div:
                committees = committees_div.get_text(separator=", ", strip=True)
        
        # votes: from "votes" section
        vote_type, vote_date, vote_result = "n/a", "n/a", "n/a"
        votes_header = soup.find("h2", string=lambda t: t and "votes" in t.lower())
        if votes_header:
            vote_info = votes_header.find_next("div")
            if vote_info:
                a_tag = vote_info.find("a")
                vote_type = a_tag.text.strip() if a_tag else "n/a"
                br_tag = vote_info.find("br")
                if br_tag:
                    vote_date = br_tag.previous_sibling.strip() if br_tag.previous_sibling else "n/a"
                    vote_result = br_tag.next_sibling.strip() if br_tag.next_sibling else "n/a"
        
        # related bills: from "related bills" section
        related_bills = "n/a"
        related_header = soup.find("h2", string=lambda t: t and "related bills" in t.lower())
        if related_header:
            related_div = related_header.find_next("div")
            if related_div:
                related_list = [a.text.strip() for a in related_div.find_all("a")]
                related_bills = ", ".join(related_list) if related_list else "n/a"
        
        # subjects: from "subject areas" section
        subjects = "n/a"
        subjects_header = soup.find("h2", string=lambda t: t and "subject areas" in t.lower())
        if subjects_header:
            subjects_div = subjects_header.find_next("div")
            if subjects_div:
                subjects_list = [a.text.strip() for a in subjects_div.find_all("a")]
                subjects = ", ".join(subjects_list) if subjects_list else "n/a"
        
        return {
            "Committees": committees,
            "Vote Type": vote_type,
            "Vote Date": vote_date,
            "Vote Result": vote_result,
            "Related Bills": related_bills,
            "Subjects": subjects
        }
    except Exception as e:
        print(f"error scraping details {details_url}: {e}")
        return {}

def scrape_cosponsors(cosponsors_url):
    # scrape the cosponsors page (/cosponsors) to get cosponsor names as a comma-separated list
    try:
        resp = requests.get(cosponsors_url, headers=headers)
        if resp.status_code != 200:
            print(f"failed to fetch cosponsors page: {cosponsors_url}")
            return {"Cosponsor List": "n/a"}
        soup = BeautifulSoup(resp.text, "html.parser")
        
        cosponsor_list = []
        table = soup.find("table", id="cosponsors")
        if table:
            rows = table.find_all("tr")
            # skip header row
            for row in rows[1:]:
                a_tag = row.find("a")
                if a_tag:
                    cosponsor_list.append(a_tag.text.strip())
        cosponsor_list_str = ", ".join(cosponsor_list) if cosponsor_list else "n/a"
        return {"Cosponsor List": cosponsor_list_str}
    except Exception as e:
        print(f"error scraping cosponsors {cosponsors_url}: {e}")
        return {"Cosponsor List": "n/a"}

# -- main script --
# generate valid bill links using your method
valid_bill_links = []
for prefix in bill_prefixes:
    for num in range(1, max_bill_number + 1):
        bill_url = f"{base_url}{prefix}{num}"
        if check_bill_exists(bill_url):
            print(f"found: {bill_url}")
            valid_bill_links.append(bill_url)
print(f"found {len(valid_bill_links)} valid bills.\n")

# list to hold complete bill data
complete_bill_data = []

for bill_url in valid_bill_links:
    bill_number = bill_url.rstrip("/").split("/")[-1]
    overview_url = bill_url          # overview page
    details_url = bill_url + "/details"    # details page
    cosponsors_url = bill_url + "/cosponsors"  # cosponsors page
    
    print(f"scraping overview for: {bill_number}")
    overview_data = scrape_overview(overview_url, bill_number)
    
    print(f"scraping details for: {bill_number}")
    details_data = scrape_details(details_url)
    
    print(f"scraping cosponsors for: {bill_number}")
    cosponsors_data = scrape_cosponsors(cosponsors_url)
    
    # merge all dicts; overview data takes precedence if keys overlap
    merged_data = {**details_data, **overview_data, **cosponsors_data}
    complete_bill_data.append(merged_data)
    
    time.sleep(0.05)  # minimal cooldown

# convert to dataframe and reorder columns
df = pd.DataFrame(complete_bill_data)
desired_order = [
    "Bill Number", "Title", "Summary", "Sponsor", "Cosponsors (Overview)",
    "Cosponsor List", "Introduced", "Status", "Prognosis", "Source URL",
    "Committees", "Vote Type", "Vote Date", "Vote Result",
    "Related Bills", "Subjects"
]
final_columns = [col for col in desired_order if col in df.columns] + \
                [col for col in df.columns if col not in desired_order]
df = df[final_columns]

csv_filename = "congress_118_bills.csv"
df.to_csv(csv_filename, index=False)
print(f"saved to {csv_filename}")
