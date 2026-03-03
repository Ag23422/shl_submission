import json
import re
import os
import requests
import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

BASE_DOMAIN = "https://www.shl.com"
INPUT_FILE = "data/raw_catalog.json"
OUTPUT_FILE = "data/processed_catalog.json"


# ---------------- PDF EXTRACTION ---------------- #

def extract_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text

    except Exception as e:
        print(f"❌ PDF extraction failed: {pdf_url}")
        return ""


def parse_pdf(text):
    data = {
        "job_family": None,
        "product_category": None,
        "skills": []
    }

    if not text:
        return data

    clean = re.sub(r'\s+', ' ', text)

    # -------- Job Family --------
    jf_index = clean.find("Job Family")
    if jf_index != -1:
        snippet = clean[jf_index:jf_index + 300]
        match = re.search(r'Job Family/?Title\s*(.*?)\s*(Average|Maximum|Number|Details)', snippet)
        if match:
            data["job_family"] = match.group(1).strip()

    # -------- Product Category --------
    pc_index = clean.find("Product Category")
    if pc_index != -1:
        snippet = clean[pc_index:pc_index + 200]
        match = re.search(r'Product Category\s*(.*?)\s*(Knowledge|Question|Designed|$)', snippet)
        if match:
            data["product_category"] = match.group(1).strip()

    # -------- Skills Extraction --------
    skills_start = clean.find("The following areas are covered")
    if skills_start != -1:
        snippet = clean[skills_start:skills_start + 500]

        # Extract capitalized phrases (skills are usually Title Case)
        possible_skills = re.findall(r'\b[A-Z][a-zA-Z &]{3,}\b', snippet)

        # Remove obvious noise
        filtered = []
        for s in possible_skills:
            if s not in ["The", "Following", "Areas", "Covered"]:
                filtered.append(s.strip())

        data["skills"] = list(set(filtered))

    return data

# ---------------- MAIN SCRAPER ---------------- #

def scrape_detail():

    if not os.path.exists(INPUT_FILE):
        print("❌ raw_catalog.json not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    enriched = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for idx, record in enumerate(records):

            print(f"\nProcessing {idx+1}/{len(records)}: {record['name']}")

            try:
                page.goto(record["url"], timeout=60000)

                # Stable wait condition
                page.wait_for_selector("h1", timeout=15000)

            except Exception:
                print("⚠ Page failed to load. Skipping.")
                continue

            # ---------- DESCRIPTION ----------
            description = ""
            try:
                desc = page.locator(
                    "h4:has-text('Description')"
                ).locator("xpath=following-sibling::p[1]")

                if desc.count() > 0:
                    description = desc.first.inner_text().strip()
            except:
                pass

            # ---------- DURATION ----------
            duration = None
            try:
                dur = page.locator(
                    "h4:has-text('Assessment length')"
                ).locator("xpath=following-sibling::p[1]")

                if dur.count() > 0:
                    duration_text = dur.first.inner_text()
                    match = re.search(r'(\d+)', duration_text)
                    if match:
                        duration = int(match.group(1))
            except:
                pass

            # ---------- FACT SHEET LINK ----------
            pdf_url = None
            try:
                link = page.locator(
                    "a:has-text('Product Fact Sheet')"
                ).first.get_attribute("href")

                if link:
                    if link.startswith("http"):
                        pdf_url = link
                    else:
                        pdf_url = BASE_DOMAIN + link

            except:
                pass

            # ---------- PDF PARSING ----------
            pdf_data = {
                "job_family": None,
                "product_category": None,
                "skills": []
            }

            if pdf_url:
                print("Downloading PDF...")
                pdf_text = extract_pdf_text(pdf_url)
                pdf_data = parse_pdf(pdf_text)

                # Debug (temporary)
                print("Job Family:", pdf_data["job_family"])
                print("Skills:", pdf_data["skills"][:5])

            enriched.append({
                "name": record["name"],
                "url": record["url"],
                "description": description,
                "job_family": pdf_data.get("job_family"),
                "product_category": pdf_data.get("product_category"),
                "skills": pdf_data.get("skills", []),
                "duration_minutes": duration,
                "remote_support": record.get("remote_support"),
                "adaptive_support": record.get("adaptive_support"),
                "test_type": record.get("test_type")
            })

        browser.close()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print("\n✅ Detail scraping complete.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_detail()