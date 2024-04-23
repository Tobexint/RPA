import time
from datetime import datetime
import re
import logging
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

        title_element = self.driver.find_element(By.ID, "caas-lead-header-d3672395-4352-3f6a-9228-510ba80094fd")
        date_element = self.driver.find_element(By.XPATH, "//time[@itemprop='datePublished']")
        description_element = self.driver.find_element(By.CLASS_NAME, "caas-body")
        picture_element = self.driver.find_element(By.CLASS_NAME, "caas-img")

        title = self.get_element_text(title_element)
        date = self.get_element_text(date_element)
        description = self.get_element_text(description_element)
        picture_url = self.get_element_attribute(picture_element, "src")
        picture_filename = self.download_picture(picture_url)
        search_phrase_count = self.count_search_phrases(title, description)
        contains_money = self.check_contains_money(title, description)

        ws.append([title, date, description, picture_filename, search_phrase_count, contains_money])
        wb.save(self.xlsx_file)
        self.logger.info("News data saved to 'news_data.xlsx'.")

if __name__ == "__main__":
    bot = AlJazeeraBot()
    bot.run()
