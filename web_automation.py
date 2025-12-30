# web_automation.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
class WebAutomation:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please install ChromeDriver")
    
    def open_website(self, url):
        if self.driver:
            self.driver.get(url)
            return True
        return False
    
    def find_element_by_text(self, text):
        try:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            return element
        except:
            return None
    
    def click_element(self, element):
        if element:
            element.click()
            return True
        return False
    
    def type_in_element(self, element, text):
        if element:
            element.clear()
            element.send_keys(text)
            return True
        return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
