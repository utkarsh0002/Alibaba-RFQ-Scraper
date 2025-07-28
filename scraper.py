from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Setup Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open Alibaba RFQ page
url = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?spm=a2700.8073608.1998677541.1.82be65aaoUUItC&country=AE&recently=Y&tracelog=newest"
driver.get(url)
time.sleep(5)  # wait for page to load

data = []
MAX_PAGES = 5  # ✅ scrape only 5 pages for now
page = 1

while True:
    print(f"📄 Scraping page {page}...")

    # Find RFQ items on the current page
    items = driver.find_elements(By.CSS_SELECTOR, ".brh-rfq-item")

    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".brh-rfq-item__subject-link").text
        except:
            title = ""

        try:
            buyer_name = item.find_element(By.CSS_SELECTOR, ".text").text
        except:
            buyer_name = ""

        try:
            # First try: get country from image tag
            country = item.find_element(By.CSS_SELECTOR, ".brh-rfq-item__country-flag").get_attribute("title")
        except:
            try:
                # Second try: get the div and remove the "Posted in:" label if present
                country_div = item.find_element(By.CSS_SELECTOR, ".brh-rfq-item__country").text
                country = country_div.replace("Posted in:", "").strip()
            except:
                country = ""

        try:
            quantity = item.find_element(By.CSS_SELECTOR, ".brh-rfq-item__quantity-num").text
        except:
            quantity = ""

        try:
            posted_time_div = item.find_element(By.CSS_SELECTOR, ".brh-rfq-item__publishtime").text
            posted_time = posted_time_div.replace("Date Posted:", "").strip()
        except:
            posted_time = ""

        data.append({
            "Product Title": title,
            "Buyer Name": buyer_name,
            "Country": country,
            "Quantity": quantity,
            "Posted Time": posted_time
        })

    print(f"✅ Scraped {len(items)} items from page {page}")

    # ✅ stop if max pages reached
    if page >= MAX_PAGES:
        print(f"✅ Reached page limit ({MAX_PAGES}). Stopping.")
        break

    # ✅ look for Next button
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.next")
        next_button.click()
        page += 1
        time.sleep(5)  # wait for next page to load
    except:
        print("🚫 No Next button found — scraping finished.")
        break

# Save all data to CSV (UTF-8)
df = pd.DataFrame(data)
df.to_csv("alibaba_rfq.csv", index=False, encoding="utf-8-sig")

print(f"✅ Scraping finished — {len(data)} items saved to alibaba_rfq_2pages.csv")

driver.quit()
