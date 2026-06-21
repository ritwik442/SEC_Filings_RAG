

import sys
from edgar import get_cik_from_ticker, get_latest_filing_url, fetch_filing_text, save_filing

if __name__ == "__main__":
    ticker = sys.argv[1].upper()
    filing_type = sys.argv[2] if len(sys.argv) > 2 else "10-K"

    cik, name = get_cik_from_ticker(ticker)
    print(f"Fetching {filing_type} for {name} (CIK {cik})...")

    url = get_latest_filing_url(cik, filing_type)
    text = fetch_filing_text(url)
    save_filing(text, ticker.lower(), filing_type)