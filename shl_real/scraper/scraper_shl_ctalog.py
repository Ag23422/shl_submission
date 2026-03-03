# # # # # # import requests
# # # # # # from bs4 import BeautifulSoup

# # # # # # url = "https://www.shl.com/products/product-catalog/?start=0&type=2"

# # # # # # headers = {"User-Agent": "Mozilla/5.0"}
# # # # # # response = requests.get(url, headers=headers)

# # # # # # soup = BeautifulSoup(response.text, "html.parser")

# # # # # # table = soup.find("table")
# # # # # # tbody = table.find("tbody")

# # # # # # rows = tbody.find_all("tr", attrs={"data-course-id": True})

# # # # # # print("Rows found:", len(rows))

# # # # # # for r in rows[:5]:
# # # # # #     link = r.find("a")
# # # # # #     print(link["href"], " | ", link.text.strip())

# # # # # import requests
# # # # # from bs4 import BeautifulSoup
# # # # # import time

# # # # # BASE_URL = "https://www.shl.com"
# # # # # CATALOG_URL = "https://www.shl.com/products/product-catalog/"

# # # # # def scrape_catalog():
# # # # #     records = []
# # # # #     offset = 0
# # # # #     step = 12

# # # # #     headers = {"User-Agent": "Mozilla/5.0"}

# # # # #     while True:
# # # # #         url = f"{CATALOG_URL}?start={offset}&type=2"
# # # # #         print(f"Scraping: {url}")

# # # # #         response = requests.get(url, headers=headers)
# # # # #         if response.status_code != 200:
# # # # #             break

# # # # #         soup = BeautifulSoup(response.text, "html.parser")

# # # # #         rows = soup.find_all("tr", attrs={"data-course-id": True})

# # # # #         if not rows:
# # # # #             break

# # # # #         for row in rows:
# # # # #             title_cell = row.find("td", class_="custom__table-heading__title")
# # # # #             if not title_cell:
# # # # #                 continue

# # # # #             link_tag = title_cell.find("a")
# # # # #             if not link_tag:
# # # # #                 continue

# # # # #             name = link_tag.get_text(strip=True)
# # # # #             relative_url = link_tag["href"]
# # # # #             full_url = BASE_URL + relative_url

# # # # #             general_cells = row.find_all("td", class_="custom__table-heading__general")

# # # # #             remote_support = "No"
# # # # #             adaptive_support = "No"
# # # # #             test_types = []

# # # # #             if len(general_cells) >= 3:

# # # # #                 # Remote testing
# # # # #                 if general_cells[0].find("span"):
# # # # #                     remote_support = "Yes"

# # # # #                 # Adaptive
# # # # #                 if general_cells[1].find("span"):
# # # # #                     adaptive_support = "Yes"

# # # # #                 # Test type
# # # # #                 key_cell = row.find("td", class_="product-catalogue__keys")
# # # # #                 if key_cell:
# # # # #                     test_types = [
# # # # #                         span.get_text(strip=True)
# # # # #                         for span in key_cell.find_all("span")
# # # # #                     ]

# # # # #             records.append({
# # # # #                 "name": name,
# # # # #                 "url": full_url,
# # # # #                 "remote_support": remote_support,
# # # # #                 "adaptive_support": adaptive_support,
# # # # #                 "test_type": test_types
# # # # #             })

# # # # #         offset += step
# # # # #         time.sleep(1)

# # # # #     print(f"\nTotal listing records scraped: {len(records)}")
# # # # #     return records


# # # # # if __name__ == "__main__":
# # # # #     scrape_catalog()

# # # # import requests
# # # # from bs4 import BeautifulSoup
# # # # import time

# # # # BASE_URL = "https://www.shl.com"
# # # # CATALOG_URL = "https://www.shl.com/products/product-catalog/"

# # # # def scrape_catalog():
# # # #     records = []
# # # #     offset = 0
# # # #     step = 12
# # # #     headers = {"User-Agent": "Mozilla/5.0"}

# # # #     while True:
# # # #         url = f"{CATALOG_URL}?start={offset}"
# # # #         print(f"Scraping: {url}")

# # # #         response = requests.get(url, headers=headers)
# # # #         if response.status_code != 200:
# # # #             break

# # # #         soup = BeautifulSoup(response.text, "html.parser")

# # # #         rows = soup.find_all("tr")
# # # #         current_section = None
# # # #         page_count = 0

# # # #         for row in rows:

# # # #             # Detect section header
# # # #             header_cell = row.find("th", class_="custom__table-heading__title")
# # # #             if header_cell:
# # # #                 current_section = header_cell.get_text(strip=True)
# # # #                 print("Detected section:", repr(current_section))
# # # #                 continue

# # # #             # Detect data row
# # # #             if row.get("data-course-id"):

# # # #                 # Only extract Individual Test Solutions
# # # #                 if not current_section or "Individual Test" not in current_section:
# # # #                     continue

# # # #                 title_cell = row.find("td", class_="custom__table-heading__title")
# # # #                 if not title_cell:
# # # #                     continue

# # # #                 link_tag = title_cell.find("a")
# # # #                 if not link_tag:
# # # #                     continue

# # # #                 name = link_tag.get_text(strip=True)
# # # #                 relative_url = link_tag["href"]
# # # #                 full_url = BASE_URL + relative_url

# # # #                 general_cells = row.find_all("td", class_="custom__table-heading__general")

# # # #                 remote_support = "No"
# # # #                 adaptive_support = "No"
# # # #                 test_types = []

# # # #                 if len(general_cells) >= 3:

# # # #                     if general_cells[0].find("span"):
# # # #                         remote_support = "Yes"

# # # #                     if general_cells[1].find("span"):
# # # #                         adaptive_support = "Yes"

# # # #                     key_cell = row.find("td", class_="product-catalogue__keys")
# # # #                     if key_cell:
# # # #                         test_types = [
# # # #                             span.get_text(strip=True)
# # # #                             for span in key_cell.find_all("span")
# # # #                         ]

# # # #                 records.append({
# # # #                     "name": name,
# # # #                     "url": full_url,
# # # #                     "remote_support": remote_support,
# # # #                     "adaptive_support": adaptive_support,
# # # #                     "test_type": test_types
# # # #                 })

# # # #                 page_count += 1

# # # #         if page_count == 0:
# # # #             break

# # # #         offset += step
# # # #         time.sleep(1)

# # # #     print(f"\nTotal Individual Test Solutions scraped: {len(records)}")
# # # #     return records


# # # # if __name__ == "__main__":
# # # #     scrape_catalog()

# # # import requests
# # # from bs4 import BeautifulSoup
# # # import time

# # # BASE_URL = "https://www.shl.com"
# # # CATALOG_URL = "https://www.shl.com/products/product-catalog/"

# # # def scrape_individual_tests():
# # #     records = []
# # #     offset = 0
# # #     step = 12
# # #     headers = {"User-Agent": "Mozilla/5.0"}

# # #     while True:
# # #         url = f"{CATALOG_URL}?start={offset}&type=1"
# # #         print(f"Scraping: {url}")

# # #         response = requests.get(url, headers=headers)
# # #         if response.status_code != 200:
# # #             break

# # #         soup = BeautifulSoup(response.text, "html.parser")

# # #         rows = soup.find_all("tr", attrs={"data-course-id": True})

# # #         if not rows:
# # #             break

# # #         for row in rows:
# # #             title_cell = row.find("td", class_="custom__table-heading__title")
# # #             if not title_cell:
# # #                 continue

# # #             link_tag = title_cell.find("a")
# # #             if not link_tag:
# # #                 continue

# # #             name = link_tag.get_text(strip=True)
# # #             relative_url = link_tag["href"]
# # #             full_url = BASE_URL + relative_url

# # #             general_cells = row.find_all("td", class_="custom__table-heading__general")

# # #             remote_support = "No"
# # #             adaptive_support = "No"
# # #             test_types = []

# # #             if len(general_cells) >= 3:

# # #                 if general_cells[0].find("span"):
# # #                     remote_support = "Yes"

# # #                 if general_cells[1].find("span"):
# # #                     adaptive_support = "Yes"

# # #                 key_cell = row.find("td", class_="product-catalogue__keys")
# # #                 if key_cell:
# # #                     test_types = [
# # #                         span.get_text(strip=True)
# # #                         for span in key_cell.find_all("span")
# # #                     ]

# # #             records.append({
# # #                 "name": name,
# # #                 "url": full_url,
# # #                 "remote_support": remote_support,
# # #                 "adaptive_support": adaptive_support,
# # #                 "test_type": test_types
# # #             })

# # #         offset += step
# # #         time.sleep(1)

# # #     print(f"\nTotal Individual Test Solutions scraped: {len(records)}")
# # #     return records


# # # if __name__ == "__main__":
# # #     scrape_individual_tests()

# # import requests
# # from bs4 import BeautifulSoup
# # import time

# # BASE_URL = "https://www.shl.com"
# # CATALOG_URL = "https://www.shl.com/products/product-catalog/"

# # def scrape_individual_tests():
# #     records = []
# #     offset = 0
# #     step = 12
# #     headers = {"User-Agent": "Mozilla/5.0"}

# #     while True:
# #         url = f"{CATALOG_URL}?start={offset}"
# #         print(f"Scraping: {url}")

# #         response = requests.get(url, headers=headers)
# #         if response.status_code != 200:
# #             break

# #         soup = BeautifulSoup(response.text, "html.parser")

# #         all_rows = soup.find_all("tr", attrs={"data-course-id": True})

# #         # Stop only when server returns no rows at all
# #         if not all_rows:
# #             break

# #         rows = soup.find_all("tr")
# #         current_section = None

# #         for row in rows:
# #             header_cell = row.find("th", class_="custom__table-heading__title")
# #             if header_cell:
# #                 current_section = header_cell.get_text(strip=True)
# #                 continue

# #             if row.get("data-course-id"):
# #                 if current_section and "Individual Test" in current_section:

# #                     title_cell = row.find("td", class_="custom__table-heading__title")
# #                     if not title_cell:
# #                         continue

# #                     link_tag = title_cell.find("a")
# #                     if not link_tag:
# #                         continue

# #                     name = link_tag.get_text(strip=True)
# #                     relative_url = link_tag["href"]
# #                     full_url = BASE_URL + relative_url

# #                     records.append({
# #                         "name": name,
# #                         "url": full_url
# #                     })

# #         offset += step
# #         time.sleep(1)

# #     print(f"\nTotal Individual Tests scraped: {len(records)}")
# #     return records


# # if __name__ == "__main__":
# #     scrape_individual_tests()

# from playwright.sync_api import sync_playwright

# BASE_URL = "https://www.shl.com/products/product-catalog/"

# def scrape_individual_tests():
#     records = []
#     seen_urls = set()
#     page_index = 1

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()

#         page.goto(BASE_URL)
#         page.wait_for_load_state("networkidle")

#         # Accept cookies if present
#         try:
#             page.locator("#CybotCookiebotDialogBodyButtonAccept").click(timeout=3000)
#             page.wait_for_load_state("networkidle")
#         except:
#             pass

#         while True:
#             print(f"\nProcessing page {page_index}")

#             # 🔹 Locate Individual section wrapper
#             individual_wrapper = page.locator(
#                 "th.custom__table-heading__title:has-text('Individual Test Solutions')"
#             ).locator("xpath=ancestor::div[contains(@class,'custom__table-wrapper')]")

#             if individual_wrapper.count() == 0:
#                 print("Individual wrapper not found.")
#                 break

#             # Wait for rows inside THIS wrapper only
#             try:
#                 individual_wrapper.locator("tr[data-entity-id]").first.wait_for(timeout=15000)
#             except:
#                 print("Rows not found inside Individual wrapper.")
#                 break

#             rows = individual_wrapper.locator("tr[data-entity-id]")
#             count = rows.count()
#             print("Rows found:", count)

#             for i in range(count):
#                 row = rows.nth(i)
#                 link = row.locator("a").first

#                 name = link.inner_text().strip()
#                 href = link.get_attribute("href")
#                 full_url = "https://www.shl.com" + href

#                 if full_url not in seen_urls:
#                     seen_urls.add(full_url)
#                     records.append({
#                         "name": name,
#                         "url": full_url
#                     })

#             # 🔹 Find Next button ONLY inside Individual wrapper
#             next_button = individual_wrapper.locator(
#                 "a.pagination__arrow:has-text('Next')"
#             )

#             if next_button.count() == 0:
#                 print("No more Individual pages.")
#                 break

#             print("Clicking Individual Next")
#             next_button.first.click()
#             page.wait_for_load_state("networkidle")

#             page_index += 1

#         browser.close()

#     print("\nTotal Individual Tests scraped:", len(records))
#     return records


# if __name__ == "__main__":
#     scrape_individual_tests()

from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://www.shl.com/products/product-catalog/"

def scrape_individual_tests():
    records = []
    seen_urls = set()
    page_index = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        # Accept cookies if present
        try:
            page.locator("#CybotCookiebotDialogBodyButtonAccept").click(timeout=3000)
            page.wait_for_load_state("networkidle")
        except:
            pass

        while True:
            print(f"\nProcessing page {page_index}")

            # 🔹 Locate Individual section wrapper
            individual_wrapper = page.locator(
                "th.custom__table-heading__title:has-text('Individual Test Solutions')"
            ).locator("xpath=ancestor::div[contains(@class,'custom__table-wrapper')]")

            if individual_wrapper.count() == 0:
                print("Individual wrapper not found.")
                break

            # Wait for rows inside THIS wrapper only
            try:
                individual_wrapper.locator("tr[data-entity-id]").first.wait_for(timeout=15000)
            except:
                print("Rows not found inside Individual wrapper.")
                break

            rows = individual_wrapper.locator("tr[data-entity-id]")
            count = rows.count()
            print("Rows found:", count)

            for i in range(count):
                row = rows.nth(i)

                # --- NAME + URL ---
                link = row.locator("td.custom__table-heading__title a").first
                name = link.inner_text().strip()
                href = link.get_attribute("href")
                full_url = "https://www.shl.com" + href

                if full_url in seen_urls:
                    continue

                seen_urls.add(full_url)

                # --- GET ALL TD CELLS ---
                cells = row.locator("td")
                td_count = cells.count()

                # Safety check
                if td_count < 4:
                    print(f"Skipping malformed row: {name}")
                    continue

                # --- REMOTE SUPPORT (Column 1) ---
                remote_cell = cells.nth(1)
                remote_support = "Yes" if remote_cell.locator("span.catalogue__circle.-yes").count() > 0 else "No"

                # --- ADAPTIVE SUPPORT (Column 2) ---
                adaptive_cell = cells.nth(2)
                adaptive_support = "Yes" if adaptive_cell.locator("span.catalogue__circle.-yes").count() > 0 else "No"
                # --- TEST TYPE (Last Column) ---
                test_type_cell = cells.nth(td_count - 1)
                badges = test_type_cell.locator("span")

                test_type = []
                for j in range(badges.count()):
                    letter = badges.nth(j).inner_text().strip()
                    if letter:
                        test_type.append(letter)

                # --- SAVE RECORD ---
                records.append({
                    "name": name,
                    "url": full_url,
                    "remote_support": remote_support,
                    "adaptive_support": adaptive_support,
                    "test_type": test_type
                })

            # 🔹 Find Next button ONLY inside Individual wrapper
            next_button = individual_wrapper.locator(
                "a.pagination__arrow:has-text('Next')"
            )

            if next_button.count() == 0:
                print("No more Individual pages.")
                break

            print("Clicking Individual Next")
            next_button.first.click()
            page.wait_for_load_state("networkidle")

            page_index += 1

        browser.close()

    print("\nTotal Individual Tests scraped:", len(records))

    with open("data/raw_catalog.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return records


if __name__ == "__main__":
    scrape_individual_tests()