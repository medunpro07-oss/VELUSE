# Veluse Med Spa Lead Scraper

Build a single Python script that searches Google for luxury med spas in Austin TX, scrapes their homepages, generates personalized Instagram DM openers via Gemini, and saves results to CSV.

## Proposed Changes

### Script

#### [NEW] [veluse_medspa_scraper.py](file:///c:/Users/sajme/OneDrive/Desktop/VELUSE%20AGENCY/veluse_medspa_scraper.py)

A single-file Python script with these components:

1. **Google Search** — Uses `requests` with a browser-like User-Agent to fetch Google search results for `"Luxury Med Spas in Austin, Texas"`. Parses result links, filters out directories (Yelp, Facebook, Instagram, TikTok, YouTube, Twitter, LinkedIn, Pinterest, Groupon, Angi, Thumbtack, MapQuest, YellowPages, BBB) and collects up to 20 unique homepage URLs.
2. **Homepage Scraper** — For each URL, fetches the page with `requests` + 10s timeout, parses with `BeautifulSoup`, strips scripts/styles/nav/footer, extracts visible text, and truncates to ~5000 chars for the LLM.
3. **Gemini Integration** — Configures `google-generativeai` with the user's API key (read from `GEMINI_API_KEY` env var). Sends each homepage's text to `gemini-2.0-flash` with the exact prompt the user specified.
4. **CSV Output** — Writes `url` and `dm_first_line` columns to `veluse_medspa_leads.csv` in the project directory.
5. **Rate Limiting** — 2-second `time.sleep()` between every HTTP request and every Gemini call.
6. **Error Handling** — `try/except` around every network call and Gemini call; logs errors to console and skips to the next URL on failure.

> [!IMPORTANT]
> The user must set the `GEMINI_API_KEY` environment variable before running the script. The script will exit with a clear message if it's missing.

---

### Dependencies

The script needs three pip packages: `requests`, `beautifulsoup4`, and `google-generativeai`. We'll install them before running.

## Verification Plan

### Manual Verification
1. Set the `GEMINI_API_KEY` env var
2. Run: `python veluse_medspa_scraper.py`
3. Confirm it prints progress (URLs found, scraping status, Gemini responses)
4. Open `veluse_medspa_leads.csv` and verify it contains rows with `url` and `dm_first_line` columns
