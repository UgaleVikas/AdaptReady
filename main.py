from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set Chrome options
options = Options()
options.add_argument("--incognito")
options.add_argument("--start-maximized")

# Search list
search_terms = ["para", "rop"]

# Loop through search terms
for term in search_terms:
    print(f"\nSearching for: {term}")

    # Launch browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open WIPO PATENTS page
        driver.get("https://patinformed.wipo.int/")

        # Enter search term
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="searchField"]'))
        )
        search_input.click()
        search_input.send_keys(term)

        # Click Search
        try:
            driver.find_element(By.XPATH, '//*[@class="margin-right"]').click()
        except Exception as e:
            print(" Search button error:", e)

        # Dismiss optional alert
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="green"]'))
            ).click()
        except:
            pass  

        # Click first search result
        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '(//*[@class="title cropper"])[1]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", first_result)
        time.sleep(1)
        first_result.click()

        time.sleep(5)

        # Function to extract dates
        def get_date(label):
            try:
                xpath = f"//td[contains(normalize-space(), '{label}')]/following-sibling::td"
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                text = element.text.split("(")[0].strip()
                return datetime.strptime(text, "%Y-%m-%d")
            except Exception as e:
                print(f" Could not extract '{label}':", str(e))
                return None

        # Extract dates
        filing_date = get_date("Filing date")
        publication_date = get_date("Publication date")
        grant_date = get_date("Grant date")

        print("\n Extracted Dates:")
        print(" Filing date      :", filing_date.date() if filing_date else "Not Found")
        print(" Publication date :", publication_date.date() if publication_date else "Not Found")
        print(" Grant date       :", grant_date.date() if grant_date else "Not Found")

        # Calculate and print difference in Y-M-D format
        def print_date_diff(date1, date2, label1, label2):
            if date1 and date2:
                if date1 > date2:
                    delta = relativedelta(date1, date2)
                else:
                    delta = relativedelta(date2, date1)

                print(f" Difference between {label1} and {label2}: {delta.years} years, {delta.months} months, {delta.days} days")
            else:
                print(f" Cannot calculate {label1} and {label2}: Missing data")

        print()
        print_date_diff(publication_date, grant_date, "Publication", "Grant")
        print_date_diff(publication_date, filing_date, "Publication", "Filing")
        print_date_diff(grant_date, filing_date, "Grant", "Filing")

    except Exception as e:
        print(" Error during processing:", str(e))

    finally:
        driver.quit()
