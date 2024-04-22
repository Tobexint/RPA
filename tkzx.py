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
        self.base_url = "https://news.yahoo.com/"
        self.category_url = "https://yahoo.com/news/politics/"
        self.article_url = "https://r.search.yahoo.com/_ylt=AwrijqZmcSFmnAQAUnVXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1714677351/RO=10/RU=https%3a%2f%2fwww.yahoo.com%2fnews%2fnetanyahu-says-9-chilling-words-151443025.html%3ffr%3dsycsrp_catchall/RK=2/RS=vSXP5EWVlLWc6kZrDKDFa1w1p8g-"
        self.xlsx_file = "tnews_data.xlsx"
        self.search_phrase = "Netanyahu"
        self.time_period = 12
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.log_file = "tbots_logs.log"
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
        try:
            search_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "ybar-sbq")))
            search_input.send_keys(self.search_phrase)
            search_input.submit()
            self.logger.info("Search successful.")
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")

    def select_news_category(self):
        #category_url = "https://yahoo.com/news/politics/"
        try:
            self.logger.info("Attempting to select news category.")
            self.driver.get(self.category_url)
            #news_category = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "_yb_17cz853 _yb_u188ux  rapid-noclick-resp")))
            #anchor_element = news_category.find_element(By.CSS_SELECTOR, "a")
            #self.driver.get(news_category.get_attribute("https://yahoo.com/news/politics/"))
            self.logger.info("News category selected successfully.")
            #self.select_news_category(category_url)
        except Exception as e:
            self.logger.error(f"Error selecting news category: {str(e)}")

    def extract_news_data(self):
        self.logger.info("Extracting news data...")
        self.driver.get(self.article_url)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Title", "Date", "Description", "Picture Filename", "Search Phrase Count", "Contains Money"])

        #articles = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "textWrap pl-16 pr-16 ov-h")))
        #articles = self.driver.get(self.article_url)
        articles = self.driver.find_elements(By.CLASS_NAME, "caas-container caas-video-pause")
        for article in articles:
            title = self.get_element_text(article, "caas-lead-header-d3672395-4352-3f6a-9228-510ba80094fd")
            date = self.get_element_text(article, "2024-04-17T15:14:43.000Z")
            description = self.get_element_text(article, "caas-body")
            picture_url = self.get_element_attribute(article, "caas-img caas-lazy has-preview caas-loaded", "https://s.yimg.com/ny/api/res/1.2/m1PD8iUdHiD63515SW4LLw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTU0MDtjZj13ZWJw/https://media.zenfs.com/en/fox_news_text_979/51cde5f41794c37b6c52f9fc108f21a3")
            picture_filename = self.download_picture(picture_url)
            search_phrase_count = self.count_search_phrases(title, description)
            contains_money = self.check_contains_money(title, description)
            ws.append([title, date, description, picture_filename, search_phrase_count, contains_money])
        wb.save(self.xlsx_file)
        self.logger.info("News data saved to 'news_data.xlsx'.")

    def get_element_text(self, ID):
        #element = parent_element.find_element(By.CLASS_NAME, class_name)
        #element = self.driver.find_element(By.ID, class_name)
        try:
            element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, ID))
            )
            return element.text if element else ""
        except TimeoutException:
            print(f"Element with id name '{ID}' not found or not visible.")

    def get_element_attribute(self, parent_element, class_name, attribute):
        element = parent_element.find_element(By.CLASS_NAME, class_name)
        element = self.driver.find_element(By.CLASS_NAME, class_name)
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
