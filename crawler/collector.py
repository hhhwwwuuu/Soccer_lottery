from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

chromedriver = "D:\\chromedriver\\chromedriver.exe"  # set your chromedrive path here
mainHttp = "https://www.mendeley.com/search/?page=1"
query = "&query="
postfix = "&sortBy=relevance"

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 '
                  'Safari/537.36',
    'Connection': 'keep-alive',
}

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# set your user data path of Chrome HERE
# the default path in Windows likes C:/Users/%uer_name%/AppData/Local/Google/Chrome/User Data/
# replace %user_name% with your user name
options.add_argument("--user-data-dir=" + r"C:/Users/%uer_name%/AppData/Local/Google/Chrome/User Data/")


# options.add_argument('--headless')
# TODO:
#  1. load browser
#  2. get the team info
#  3. extract history of two team (considering same host, same event)
#       - different companies
#       - init rate and final rate
#  4. extract recent histories with other teams for each team (considering same host, same event)
#       - different companies
#       - init rate and final rate


class GameCrawler:

    def __init__(self, url):
        self.url = url

