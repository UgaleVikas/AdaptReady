from datetime import datetime
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

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open URL
    driver.get("https://patinformed.wipo.int/")

    # Input search WITH "rop"
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@class="searchField"]'))
    )
    search_input.click()
    search_input.send_keys("rop")

    # Click Search button
    try:
        search_btn = driver.find_element(By.XPATH, '//*[@class="margin-right"]')
        search_btn.click()
    except:
        pass

    # click on alert
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="green"]'))
        ).click()
    except:
        pass  # ignore if not found

    # Click first result in search results
    first_result = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '(//*[@class="title cropper"])[1]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", first_result)
    time.sleep(1)
    first_result.click()

    # Extract a date
    def get_date(label):
        try:
            xpath = f"//td[contains(normalize-space(), '{label}')]/following-sibling::td"
            print(f" Looking for: {label} using XPath: {xpath}")

            # Wait until the element is present
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = element.text.split("(")[0].strip()
            return datetime.strptime(text, "%Y-%m-%d")
        except Exception as e:
            print(f"Could not extract '{label}':", str(e))
            return None


    filing_date = get_date("Filing date")
    publication_date = get_date("Publication date")
    grant_date = get_date("Grant date")

    # Print extracted dates
    print("\n Dates Extracted:")
    print(" Filing date:", filing_date.date() if filing_date else "Not Found")
    print(" Publication date:", publication_date.date() if publication_date else "Not Found")
    print(" Grant date:", grant_date.date() if grant_date else "Not Found")

    #  Calculate date differences
    def compare_dates(date1, date2, label1, label2):
        if date1 and date2:
            diff = abs((date1 - date2).days)
            print(f" Difference between {label1} and {label2}: {diff} days")
        else:
            print(f" Cannot calculate {label1} and {label2}: Missing data")

    compare_dates(publication_date, grant_date, "Publication", "Grant")
    compare_dates(publication_date, filing_date, "Publication", "Filing")
    compare_dates(grant_date, filing_date, "Grant", "Filing")

except Exception as e:
    print(" Error:", str(e))

finally:
    driver.quit()
