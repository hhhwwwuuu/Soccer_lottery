import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

chromedriver = "D:\\chromedriver\\92\\chromedriver.exe"  # set your chromedrive path here
#mainHttp = "https://www.mendeley.com/search/?page=1"
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
#options.add_argument("--user-data-dir=" + r"C:/Users/Zhiqiang/AppData/Local/Google/Chrome/User Data/")
options.add_argument('--headless')

# TODO:
#  1. load browser --> V
#  2. get the team info --> V
#  3. extract history of two team (considering same host, same event)
#       - different companies
#       - init rate and final rate
#  4. extract recent histories with other teams for each team (considering same host, same event)
#       - different companies
#       - init rate and final rate


class MatchCrawler:

    def __init__(self, url):
        self.url = url
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        self.driver = webdriver.Chrome(chromedriver, options=options)
        wait = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions)
        self.__open_browser()
        self.home, self.h_rank, self.guest, self.g_rank = self.get_team_names()
        #print(self.home, self.h_rank, self.guest, self.g_rank )
        self.get_credit_status()
        self.get_history_battle()

    def __open_browser(self):
        self.driver.get(self.url)
        time.sleep(2)

    def get_team_names(self):
        # 获取对阵双方名字和排位
        home_rank = self.driver.find_element_by_xpath("//div[@class='home']//span[1]").text[1:-1]
        home_name = self.driver.find_element_by_xpath("//div[@class='home']//span[2]").text
        #print(home_rank, home_name)
        guest_name = self.driver.find_element_by_xpath("//div[@class='away']//span[1]").text
        guest_rank = self.driver.find_element_by_xpath("//div[@class='away']//span[2]").text[1:-1]
        #print(guest_rank, guest_name)
        return home_name, home_rank, guest_name, guest_rank

    def get_credit_status(self):
        # 获取联赛积分状态
        print(self.driver.find_element_by_xpath("//div[@class='bd same']//table").text)
        print(self.driver.find_element_by_xpath("//div[@class='bd same ml6']//table").text)

    def get_history_battle(self):
        """
        获取历史交锋情况
        - 不分主客的情况下对阵
        - 同主客情况下
        - 同赛事的情况下
        - 同主客，同赛事的请下

        按照日期，保留唯一比赛
        :return:
        """
        # default
        print(self.driver.find_element_by_xpath("//div[@class='porlet' and @id='porlet_3']//table[@class='odds-table']").text)

        print("+++++++++++++++++++++++++++++")
        # 同主客
        self.driver.find_elements_by_xpath("//div[@class='porlet' and @id='porlet_3']//div[@class='conditions']/label")[0].click()
        print(self.driver.find_element_by_xpath("//div[@class='porlet' and @id='porlet_3']//table[@class='odds-table']").text)
        # 同赛事
        # 同主客，同赛事