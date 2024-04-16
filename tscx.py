import time
from datetime import datetime
import re
import logging
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import openpyxl
import requests

class AlJazeeraBot:
    def __init__(self):
        self.base_url = "https://www.aljazeera.com/"
        self.xlsx_file = "news_data.xlsx"
        self.search_phrase = "Donald Trump"
        self.time_period = 7
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.log_file = "bots_logs.log"
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger("AlJazeeraBot")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger
    def run(self):
        try:
            self.logger.info("starting Al Jazeera Bot...")
            self.open_website()
            self.search_news()
            self.select_news_category()
            self.extract_news_data()
        except Exception as e:
            self.logger.exception("An error occurred during the bot execution: {}".format(str(e)))
        finally:
            self.driver.quit()

    def open_website(self):
        self.logger.info("Opening Al Jazeera website...")
        self.driver.get(self.base_url)

    def search_news(self):
        search_input = self.wait.until(EC.visibility_of_element_located((By.ID, "header-search__input")))
        search_input.send_keys(self.search_phrase)
        search_input.submit()

    def select_news_category(self):
        news_category = self.waituntil(EC.visibility_of_element_located((By.CSS_SELECTOR, ".menu-level").a))
        self.driver.get(news_category.get_attribute("href"))

    def extract_news_data(self):
        self.logger.info("Extracting news data...")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Title", "Date", "Description", "Picture Filename", "Search Phrase Count", "Contains Money"])

        articles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".article-mezzoti")))
        for article in articles:
            title = self.get_element_text(article, ".top-sec-item > h2")
            date = self.get_element_text(article, ".release-date")
            description = self.get_element_text(article, ".description")
            picture_url = self.get_element_attribute(article, ".lazyimg.lazyimage source", "data-srcset")
            picture_filename = self.download_picture(picture_url)
            search_phrase_count = self.count_search_phrases(title, description)
            contains_money = self.check_contains_money(title, description)
            ws.append([title, date, description, picture_filename, search_phrase_count, contains_money])
        wb.save(self.xlsx_file)
        self.logger.info("News data saved to 'news_data.xlsx'.")

    def get_element_text(self, parent_element, selector):
        element = parent_element.find_element(By.CSS_SELECTOR, selector)
        return element.text if element else ""

    def get_element_attribute(self, parent_element, selector, attribute):
        element = parent_element.find_element.find_element(By.CSS_SELECTOR, selector)
        return element.get_attribute(attribute) if element else ""

    def count_search_phrases(self, *texts):
        for text in texts:
            if re.search(r"\$[\d,.]+|\d+ (?:dollars|USD)", text):
                return "True"
        return "False"

    def download_picture(self, url):
        if url:
            picture_filename = "picture_{:%Y%m%d%H%M%S}.jpg".format(datetime.now())
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(picture_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            return picture_filename
        return ""

    def wait_for_page_load(self, url):
        self.logger.info("waiting for page to load...")
     #self.wait.until(EC.url_to_be(url))

    def wait_for_element(self, selector):
        self.logger.info("Waiting for element {}...".format(selector))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))

if __name__ == "__main__":
    bot = AlJazeeraBot()
    bot.run()
