"""
Veluse Agency — Med Spa Lead Scraper (V3.1 - Enterprise Hyper-Threading)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Uses Google Places API to scrape hundreds of Med Spas across major Texas markets concurrently.
2. Vists each website to scrape valid emails and scan for Meta/Google Pixels concurrently.
3. Generates hyper-personalized DM given the website's text using GPT-4o-mini concurrently.
4. Exports to an industrial-grade CSV using Pandas.
"""

import os
import sys
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from openai import OpenAI
import concurrent.futures

OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veluse_medspa_leads_v3.csv")

QUERIES = [
    "Med Spa in Dallas, TX",
    "Medical Spa in Houston, TX",
    "Luxury Aesthetics in San Antonio, TX",
    "Med Spa in Austin, TX",
    "Medical Spa in Fort Worth, TX",
    "Med Spa in El Paso, TX",
    "Med Spa in Plano, TX",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

SYSTEM_PROMPT = (
    "You are an elite B2B closer for Veluse Agency. "
    "Write a punchy, conversational first line for a cold-email/DM to a Med Spa owner. "
    "Mention a specific service they offer to prove you read their site, "
    "then casually ask if they have the system/capacity to handle an extra 20-30 high-ticket patients this month. "
    "Keep it under 30 words. NO cheesy greetings. Tone: Sharp, professional, curious."
)

def get_places_from_google(api_key: str, query: str) -> list:
    places = []
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": api_key}
    
    while True:
        resp = requests.get(url, params=params).json()
        results = resp.get("results", [])
        
        def get_website(place_id, name):
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {"place_id": place_id, "fields": "website", "key": api_key}
            try:
                details_resp = requests.get(details_url, params=details_params, timeout=5).json()
                website = details_resp.get("result", {}).get("website")
                return {"name": name, "url": website} if website else None
            except:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_website, r.get("place_id"), r.get("name")) for r in results]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    places.append(res)
        
        next_page_token = resp.get("next_page_token")
        if not next_page_token:
            break
            
        time.sleep(2)
        params = {"pagetoken": next_page_token, "key": api_key}
        
    return places

def analyze_website(url: str, max_chars: int = 4000) -> dict:
    result = {"text": "", "emails": "", "has_meta_pixel": False, "has_google_tag": False}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return result

    html = resp.text
    if "fbevents.js" in html or "fbq(" in html:
        result["has_meta_pixel"] = True
    if "gtag/js" in html or "googletagmanager.com" in html:
        result["has_google_tag"] = True

    soup = BeautifulSoup(html, "html.parser")
    found_emails = set(re.findall(EMAIL_REGEX, soup.get_text(separator=" ", strip=True)))
    valid_emails = [e for e in found_emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    result["emails"] = " | ".join(valid_emails)

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
        
    clean_text = re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()
    result["text"] = clean_text[:max_chars]
    return result

def generate_dm_opener(client: OpenAI, text: str) -> str:
    if len(text) < 100:
        return ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Website Text:\n{text[:4000]}"},
            ],
            max_tokens=80,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""

def process_url(url, name, openai_client):
    site_data = analyze_website(url)
    if not site_data["text"]:
        return None
        
    dm = generate_dm_opener(openai_client, site_data["text"])
    if not dm:
        return None
        
    return {
        "Business Name": name,
        "Website": url,
        "Emails": site_data["emails"],
        "Meta Pixel Active": site_data["has_meta_pixel"],
        "Google Tag Active": site_data["has_google_tag"],
        "AI Cold Opener": dm
    }

def main():
    print("[*] VELUSE AGENCY - INDUSTRIAL LEAD SCRAPER (V3.1 - Hyper-Threaded)")
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    google_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()

    if not openai_key or not google_key:
        print("ERROR: Missing API Keys. Ensure both OPENAI_API_KEY and GOOGLE_PLACES_API_KEY are set.")
        sys.exit(1)

    openai_client = OpenAI(api_key=openai_key)
    all_places = {}
    
    print(f"[*] Sweeping {len(QUERIES)} target queries via Google Places API...")
    for q in QUERIES:
        print(f"  -> {q}")
        places = get_places_from_google(google_key, q)
        for p in places:
            all_places[p["url"]] = p["name"]
            
    unique_urls = list(all_places.keys())
    print(f"\n[*] Extracted {len(unique_urls)} unique Med Spa URLs. Commencing deep scrape...")
    
    leads = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_url = {executor.submit(process_url, url, all_places[url], openai_client): url for url in unique_urls}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            completed += 1
            url = future_to_url[future]
            print(f"[{completed}/{len(unique_urls)}] Processed {url}")
            try:
                result = future.result()
                if result:
                    leads.append(result)
            except Exception as e:
                pass
        
    if leads:
        df = pd.DataFrame(leads)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n[+] MISSION ACCOMPLISHED. {len(leads)} leads securely written to {OUTPUT_CSV}")
    else:
        print("[-] No leads generated payload.")

if __name__ == "__main__":
    main()
