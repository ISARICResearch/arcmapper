from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import arcmapper

DATA_DICTIONARY = (
    Path(__file__).parent
    / "data"
    / "CCPUKSARIEastMidlands_DataDictionary_2022-06-06.csv"
)


def chromedriver_present():
    try:
        Service()
    except Exception:
        return False
    return True


def save_screenshot(driver, name="screenshot"):
    screenshot_path = Path(f"{name}.png")
    driver.save_screenshot(screenshot_path)
    return str(screenshot_path)


@pytest.fixture
def driver():
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)

    process = arcmapper.launch_subprocess()  # app initializes during import
    arcmapper.wait_for_server()  # subprocess isolates startup

    driver.get("http://127.0.0.1:8050")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "upload-intermediate-file"))
    )

    yield driver

    driver.quit()
    process.terminate()
    process.wait()


def test_e2e(driver):
    upload_input_file = driver.find_element(
        By.XPATH, '//*[@id="upload-input-file"]/div/input'
    )
    upload_input_file.send_keys(str(DATA_DICTIONARY))
    map_btn = driver.find_element(By.ID, "map-btn")
    map_btn.click()


# select first and third row
# save to intermediate file
# download FHIR mapping


def test_e2e_with_intermediate_file():
    pass
