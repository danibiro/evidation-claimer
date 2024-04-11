from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import yaml
import logging as log

log.basicConfig(
    filename="log.txt",
    filemode="a",
    level=log.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)

MAX_TIMEOUT = 7

def driver_init():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def read_files():
    try:
        with open("user_config.yaml", "r") as user_stream:
            user_config = yaml.safe_load(user_stream)
            return user_config
    except yaml.YAMLError as exc:
        log.error(exc)
        exit(1)
    except FileNotFoundError as exc:
        log.error("No user input file found!")
        exit(1)

def init(driver):
    driver.get("https://my.evidation.com/login")
    log.info("Directed to evidation.com/login")
    
def accept_cookies(wait):
    try:
        cookie_accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
        cookie_accept_button.click()
        log.info("Cookies accepted")
    except NoSuchElementException as _:
        log.warn("Accept cookies not needed")

def login(wait, user_config):
    email = user_config["email"]
    password = user_config["password"]
    
    email_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="email"]')))
    email_input.send_keys(email)
    
    password_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]')))
    password_input.send_keys(password)

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div/form/button')))
    login_button.click()

if __name__ == "__main__":
    driver = driver_init()
    wait = WebDriverWait(driver, MAX_TIMEOUT)
    user_config = read_files()
    init(driver)
    accept_cookies(wait)
    login(wait, user_config)