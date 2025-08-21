# test_search.py

import pytest
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

search_term = ["para"]

def test_example_search():
    print(f"\nSearching for: {search_term}")

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://patinformed.wipo.int/")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="searchField"]'))
        )
        search_input.click()
        search_input.send_keys(search_term)

        try:
            driver.find_element(By.XPATH, '//*[@class="margin-right"]').click()
        except Exception as e:
            print(" Search button error:", e)

        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="green"]'))
            ).click()
        except:
            pass

        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '(//*[@class="title cropper"])[1]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", first_result)
        time.sleep(1)
        first_result.click()

        time.sleep(5)

        def get_dates(label):
            dates = []
            try:
                xpath = f"//td[contains(normalize-space(), '{label}')]/following-sibling::td"
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    text = element.text.split("(")[0].strip()
                    if text:
                        try:
                            dt = datetime.strptime(text, "%Y-%m-%d")
                            dates.append(dt)
                        except ValueError as ve:
                            print(f" Date format error for '{label}': '{text}' - {ve}")
                if not dates:
                    print(f" No dates found for label '{label}'")
                return dates
            except Exception as e:
                print(f" Could not extract '{label}':", str(e))
                return dates

        filing_dates = get_dates("Filing date")
        publication_dates = get_dates("Publication date")
        grant_dates = get_dates("Grant date")

        print("\n Extracted Dates:")
        print(f" Filing dates ({len(filing_dates)} found):")
        for d in filing_dates:
            print(f"  - {d.date()}")

        print(f" Publication dates ({len(publication_dates)} found):")
        for d in publication_dates:
            print(f"  - {d.date()}")

        print(f" Grant dates ({len(grant_dates)} found):")
        for d in grant_dates:
            print(f"  - {d.date()}")

        def print_all_date_diffs(dates1, dates2, label1, label2):
            if not dates1 or not dates2:
                print(f" Cannot calculate {label1} and {label2}: Missing data")
                return
            print(f"\nDifferences between {label1} and {label2}:")
            for i, d1 in enumerate(dates1, start=1):
                for j, d2 in enumerate(dates2, start=1):
                    delta = relativedelta(d1, d2)
                    print(f" {label1}[{i}] ({d1.date()}) - {label2}[{j}] ({d2.date()}): {delta.years} years, {delta.months} months, {delta.days} days")

        print_all_date_diffs(publication_dates, grant_dates, "Publication", "Grant")
        print_all_date_diffs(publication_dates, filing_dates, "Publication", "Filing")
        print_all_date_diffs(grant_dates, filing_dates, "Grant", "Filing")

    except Exception as e:
        print(" Error during processing:", str(e))
    finally:
        driver.quit()
