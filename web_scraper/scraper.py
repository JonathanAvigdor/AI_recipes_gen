from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_ica_offers(url: str):
    """ Scarpes weekly offers from ICA,
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    # click cookie consent button
    agree_button_selector = "button#onetrust-accept-btn-handler"
    try:
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, agree_button_selector)))
        driver.execute_script("arguments[0].click();", button)
    except:
        pass

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    key = "article > div.offer-card__details-container"
    key_2 = "article > div.offer-card__image-container > div > span.sr-only"

    product_title = [i.text.replace("\xa0kr. ", "").split(". ")[0] for i in soup.select(key)]
    new_price = [i.text for i in soup.select(key_2)]

    grocery_offers = list(zip(product_title, new_price))

    driver.quit()
    return grocery_offers


