# core/veluse_deep_scraper.py
import os
import re
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai

# Authoritative Local Key Matrix
PLACES_API_KEY = "AIzaSyCw2uiAPlOvLJ8J_9lN2yh2YkU88Vtjz0Q"
GEMINI_API_KEY = "AIzaSyBmKoDNqzbTg-3PInaEefdt5cZBjU8D43s"

# Initialize Google GenAI Client
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Correct Workspace Output Destination
OUTPUT_FILE = r"C:\Users\sajme\OneDrive\Desktop\VELUSE AGENCY\database\la_beverly_hills_owners.csv"

def fetch_places_matrix(query: str, location_tag: str) -> list:
    """Queries legacy textsearch API and details endpoint to aggregate unique medical listings with websites and phone numbers."""
    print(f"[*] Sweeping Places Matrix for: '{query}' ({location_tag})")
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={PLACES_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            print(f"[-] Textsearch error for '{query}': {data.get('status')}")
            return []
        
        results = data.get("results", [])
        extracted = []

        def get_details(item):
            place_id = item.get("place_id")
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "website,formatted_phone_number",
                "key": PLACES_API_KEY
            }
            try:
                res = requests.get(details_url, params=details_params, timeout=10).json()
                result = res.get("result", {})
                phone = result.get("formatted_phone_number", item.get("formatted_phone_number", "PENDING_CALL_VERIFICATION"))
                website = result.get("website", "")
                
                # If no website but maps url is available, use it as last resort
                if not website:
                    website = item.get("url", "")
                    
                return {
                    "name": item.get("name"),
                    "location": location_tag,
                    "phone": phone,
                    "website": website
                }
            except Exception as e:
                return {
                    "name": item.get("name"),
                    "location": location_tag,
                    "phone": item.get("formatted_phone_number", "PENDING_CALL_VERIFICATION"),
                    "website": item.get("url", "")
                }

        # Query Place Details concurrently for the results
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_details, item) for item in results]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    extracted.append(res)
                    
        return extracted
    except Exception as e:
        print(f"[-] Places API Connection Error: {e}")
        return []

def deep_crawl_clinic_ecosystem(lead: dict) -> dict:
    """Performs concurrent homepage analysis and deep subpage team crawls."""
    url = lead["website"]
    lead["owner_name"] = "PENDING_VERIFICATION"
    lead["owner_ig"] = "PENDING_VERIFICATION"
    lead["owner_linkedin"] = "PENDING_VERIFICATION"
    lead["email"] = "PENDING_SCRAPE"
    lead["meta_pixel"] = "FALSE"
    lead["google_tag"] = "FALSE"
    lead["ai_opener"] = "Hey! Noticed your premium clinic is scaling up local visibility formats online."
    
    if not url or not url.startswith("http") or "maps.google.com" in url or "google.com" in url:
        return lead

    try:
        headers = {"User-Agent": "VeluseOS-Bot/2.0 (Premium Data Integration)"}
        res = requests.get(url, timeout=8, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        html_content = res.text

        # 1. Base Metadata Checks (Pixels & Global Tags)
        if "fbevents.js" in html_content or "fbq(" in html_content: lead["meta_pixel"] = "TRUE"
        if "gtag" in html_content or "googletagmanager" in html_content: lead["google_tag"] = "TRUE"

        # 2. Extract Base Homepage Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}', html_content)
        valid_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
        if valid_emails: lead["email"] = list(set(valid_emails))[0]

        # 3. Discover Deep Team/About Links
        subpages_to_crawl = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].lower()
            text = a_tag.get_text().lower()
            if any(k in href or k in text for k in ["about", "team", "meet", "staff", "doctor", "founder", "owner", "provider"]):
                full_url = href if href.startswith("http") else os.path.join(url, href.lstrip("/"))
                subpages_to_crawl.append(full_url)
        
        # Deduplicate internal links and cap depth to prevent infinite crawling loops
        subpages_to_crawl = list(set(subpages_to_crawl))[:3]

        # 4. Crawl Deep Roster Subpages for Names & Direct Social Media Links
        for sub_url in subpages_to_crawl:
            try:
                sub_res = requests.get(sub_url, timeout=6, headers=headers)
                sub_text = sub_res.text
                sub_soup = BeautifulSoup(sub_text, "html.parser")

                # Parse specific Social Network Strings
                for link in sub_soup.find_all("a", href=True):
                    href_val = link["href"]
                    if "linkedin.com/in/" in href_val and lead["owner_linkedin"] == "PENDING_VERIFICATION":
                        lead["owner_linkedin"] = href_val
                    if "instagram.com/" in href_val and lead["owner_ig"] == "PENDING_VERIFICATION":
                        # Strip common clinic group accounts from personal handle profiles
                        if not any(c in href_val.lower() for c in ["/p/", "/share", "clinic", "spa", "medical"]):
                            lead["owner_ig"] = href_val

                # Extract Names following Medical and Corporate Titles via Regex
                page_visible_text = sub_soup.get_text()
                name_match = re.search(r'(?:Dr\.|Dr|Dr\. User|Doctor|Founder|Owner|Medical Director)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', page_visible_text)
                if name_match and lead["owner_name"] == "PENDING_VERIFICATION":
                    lead["owner_name"] = name_match.group(1)
            except Exception:
                continue

        # 5. Call Gemini 3.5 Flash to construct an optimized contextual hook
        clean_summary = re.sub(r'<[^>]+>', ' ', html_content)[:2500].strip()
        prompt = (
            f"Generate a single, ultra-short B2B sales opening sentence under 25 words for the owner of this medical clinic. "
            f"Reference their specific location, treatments, or digital gaps (Pixel: {lead['meta_pixel']}). No intro fluff, "
            f"go straight into a personalized operational observation. Text summary:\n{clean_summary}"
        )
        ai_response = ai_client.models.generate_content(model='gemini-3.5-flash', contents=prompt)
        if ai_response.text:
            lead["ai_opener"] = ai_response.text.strip().replace('"', '')

    except Exception:
        pass
    return lead

def run_production_enrichment_pipeline():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Comprehensive Multi-Query Expansion Grid
    queries = [
        ("Med Spa", "Beverly Hills, CA"),
        ("Aesthetic Clinic", "Beverly Hills, CA"),
        ("Plastic Surgeon", "Beverly Hills, CA"),
        ("Med Spa", "Los Angeles, CA"),
        ("Dermatologist Clinic", "Los Angeles, CA")
    ]
    
    raw_aggregated = []
    for q, loc in queries:
        raw_aggregated.extend(fetch_places_matrix(q, loc))
        
    # Deduplicate matching nodes based on corporate text identity
    unique_matrix = {item["name"]: item for item in raw_aggregated}.values()
    print(f"[+] Deduplicated Matrix: Found {len(unique_matrix)} unique commercial prospects.")
    
    print("[*] Launching multi-threaded web crawler with deep subpage inspection parsing...")
    enriched_leads = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(deep_crawl_clinic_ecosystem, item): item for item in unique_matrix}
        for i, future in enumerate(as_completed(futures)):
            enriched_leads.append(future.result())
            if (i+1) % 10 == 0:
                print(f"    -> Audited {i+1}/{len(unique_matrix)} sites...")

    print("[*] Generating output arrays and applying workflow workforce partition metrics...")
    allocated_phone_counter = 0
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Clinic Name", "Target Location", "Main Phone Line", "Owner Full Name",
            "Direct Owner IG Profile URL", "LinkedIn Identity URL", "Professional Email Address",
            "Active Campaign Status", "Workload Allocation Vector", "Website",
            "Meta Pixel Active", "Google Tag Active", "AI Cold Opener", "Notes"
        ])
        
        for lead in enriched_leads:
            phone_val = lead.get("phone", "")
            
            # Workforce Vector Assignment Parameters
            if phone_val and phone_val != "PENDING_CALL_VERIFICATION":
                if allocated_phone_counter < 40:
                    workload_vector = "THIRU_COLD_CALL"
                elif 40 <= allocated_phone_counter < 80:
                    workload_vector = "MEDUN_DM"
                else:
                    workload_vector = "BACKLOG_SEQUENCER"
                allocated_phone_counter += 1
            else:
                workload_vector = "BACKLOG_SEQUENCER"
                
            writer.writerow([
                lead["name"], lead["location"], phone_val,
                lead["owner_name"], lead["owner_ig"], lead["owner_linkedin"],
                lead["email"], "PENDING", workload_vector, lead["website"],
                lead["meta_pixel"], lead["google_tag"], lead["ai_opener"],
                "Deep subpage data compilation complete."
            ])
            
    print("="*80)
    print(f"[+] PIPELINE DISPATCH COMPLETE: High-fidelity database ledger deployed.")
    print(f"    File target verification path: {OUTPUT_FILE}")
    print("="*80)

if __name__ == "__main__":
    run_production_enrichment_pipeline()
