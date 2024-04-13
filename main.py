from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import yaml
import logging as log
from time import sleep

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
        sleep(1)
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

def check_if_cards_exist(wait) -> int:
    # this is needed to load the elements correctly. a default list is shown with 3 elems before load, after load it refreshes
    try:
        cards2 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[2]/ol')))
        sleep(1)
        nr_children2 = len(cards2.find_elements(By.XPATH, "./*"))
        return nr_children2
    except NoSuchElementException:
        log.info("No cards left")
        return 0

def mood_check(driver, wait) -> bool:
    try:
        for elem in range(1, 4):
            try:
                mood_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'(//*[@id="field-react-aria-{elem}"])')))
                continue
            except:
                pass
        mood_button.click()
        
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/div[4]/div[2]/div[2]')))
        submit_button.click()
        driver.refresh()
        return True
    except:
        log.error("Could not check the mood")
        return False
        
def sleep_check(driver, wait) -> bool:
    try:
        for elem in range(1, 4):
            try:
                sleep_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'(//*[@id="field-react-aria-{elem}"])')))
                continue
            except:
                pass
        sleep_button.click()

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[2]/div/div[2]/div[4]/div[2]/div[2]')))
        submit_button.click()
        driver.refresh()
        return True
    except:
        log.error("Could not check sleep")
        return False

def learn_more(driver, wait, cards_left):
    while (cards_left != 0):
        learn_more_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[1]/div/div[2]/div[4]/div[2]')))
        learn_more_button.click()
        log.info("Clicked on Learn more")
        sleep(2)
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])
        driver.close()
        driver.switch_to.window(window_handles[0])
        driver.refresh()
        cards_left = cards_left - 1

if __name__ == "__main__":
    driver = driver_init()
    wait = WebDriverWait(driver, MAX_TIMEOUT)
    user_config = read_files()
    init(driver)
    accept_cookies(wait)
    login(wait, user_config)
    cards_left = check_if_cards_exist(wait)
    if (cards_left != 0):
        cards_left = cards_left - 1 if mood_check(driver, wait) == True else cards_left
        cards_left = cards_left - 1 if sleep_check(driver, wait) == True else cards_left
        learn_more(driver, wait, cards_left)