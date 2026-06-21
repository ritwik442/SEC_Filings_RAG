

import re
import time
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Your Name your@email.com",
    "Accept-Encoding": "gzip, deflate",
}

EDGAR_BASE = "https://www.sec.gov"  


def get_latest_filing_url(cik: str, filing_type: str = "10-K") -> str:
    
    cik_padded = str(cik).zfill(10)


    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()


    filings = data["filings"]["recent"]
    forms = filings["form"]
    accessions = filings["accessionNumber"]
    primary_docs = filings["primaryDocument"]

    for form, accession, primary_doc in zip(forms, accessions, primary_docs):
        if form == filing_type:

            accession_clean = accession.replace("-", "")
            cik_short = str(int(cik))  

            doc_url = (
                f"{EDGAR_BASE}/Archives/edgar/data/"
                f"{cik_short}/{accession_clean}/{primary_doc}"
            )
            print(f"Found {filing_type} filing: {accession}")
            print(f"Document URL: {doc_url}")
            return doc_url

    raise ValueError(f"No {filing_type} filing found for CIK {cik}")

def list_filings(cik: str, limit: int = 20):
    
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    recent = resp.json()["filings"]["recent"]

    print(f"{'Form':<12} {'Filed':<12} Accession")
    print("-" * 45)
    for form, date, accession in list(zip(
        recent["form"], recent["filingDate"], recent["accessionNumber"]
    ))[:limit]:
        print(f"{form:<12} {date:<12} {accession}")

        

def get_cik_from_ticker(ticker: str) -> tuple[str, str]:

    import json, os
    cache = "data/company_tickers.json"
    if not os.path.exists(cache):
        resp = requests.get("https://www.sec.gov/files/company_tickers.json",
                            headers=HEADERS)
        resp.raise_for_status()
        os.makedirs("data", exist_ok=True)
        with open(cache, "w") as f:
            f.write(resp.text)

    data = json.loads(open(cache).read())
    ticker = ticker.upper()
    for entry in data.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"]), entry["title"]
    raise ValueError(f"No company found for ticker {ticker}")

def linearize_table(table) -> str:
    
    rows = table.find_all("tr")
    if len(rows) < 2:
        return ""

    def cells_of(row):
        return [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]

    headers = cells_of(rows[0])

    while headers and not headers[0]:
        headers = headers[1:]

    lines = []
    for row in rows[1:]:
        cells = cells_of(row)
        if not any(cells):
            continue                        
        label = cells[0]
        values = cells[1:]
        if not label or not any(values):
            continue                        

        pairs = []
        for i, val in enumerate(values):
            if not val:
                continue                    
            header = headers[i] if i < len(headers) else f"col{i+1}"
            pairs.append(f"{header}={val}" if header else val)
        if pairs:
            lines.append(f"{label}: " + ", ".join(pairs))
    return "\n".join(lines)





def fetch_filing_text(doc_url: str) -> str:
    
    time.sleep(0.5)

    resp = requests.get(doc_url, headers=HEADERS)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()

    tables_processed = 0
    for table in soup.find_all("table"):
        linearized = linearize_table(table)
        if linearized:
            replacement = soup.new_tag("p")
            replacement.string = "\n" + linearized + "\n"
            table.replace_with(replacement)
            tables_processed += 1
        else:
            table.decompose()              
    print(f"Linearized {tables_processed} tables")

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    print(f"Extracted {len(text):,} characters of clean text")
    return text

def save_filing(text: str, company: str, filing_type: str):
    
    import os
    os.makedirs("data", exist_ok=True)
    filename = f"data/{company}_{filing_type}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved to {filename}")
    return filename