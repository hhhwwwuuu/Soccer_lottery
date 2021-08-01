import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import json
import os
import logging
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

chromedriver = "D:\\chromedriver\\92\\chromedriver.exe"  # set your chromedrive path here
# mainHttp = "https://www.mendeley.com/search/?page=1"
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
# options.add_argument("--user-data-dir=" + r"C:/Users/Zhiqiang/AppData/Local/Google/Chrome/User Data/")
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

    def __init__(self, url, league_url):
        self.url = url
        self.league_url = league_url
        self.result = defaultdict()
        self.league = None
        self.date = None
        self.table_header = ['company', 'league', 'home', 'score', 'guest', 'asia_home', 'asia_handicap', 'asia_guest',
                             'euro_home', 'euro_draw', 'euro_guest', 'final_Kaisa_home', 'final_aisa_handicap',
                             'final_Kaisa_guest', 'final_euro_home', 'final_euro_draw', 'final_euro_guest']
        self.table_data = defaultdict(list)
        logging.info("Crawling data from {}".format(url))
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        self.driver = webdriver.Chrome(chromedriver, options=options)
        wait = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions)
        self.__open_browser()

        """
        获取上赛季记录
        """
        #self.get_last_season_data()


        self.home, self.h_rank, self.guest, self.g_rank = self.get_team_names()
        self.league, self.date = self.get_date()

        self.save_file = '_'.join([self.date.split()[0], self.home, self.guest]) + '.json'
        self.get_credit_status()
        self.get_history_battle()
        self.save_record()

    def get_last_season_data(self):
        self.driver.get(self.league_url)
        time.sleep(2)

        header = self.driver.find_element_by_xpath("//div[@class='data-count-porlet porlet']//table[@class='odds-table']/thead").text
        data = {key:[] for key in header.split()}

        standings = self.driver.find_elements_by_xpath(
            "//div[@class='data-count-porlet porlet']//table[@class='odds-table']/tbody/tr")
        # print(len(standings))
        for team in standings:
            #print(team.text)

            # detail_info = team.find_element_by_xpath("td[3]").text.split()
            # print(detail_info)
            for index, key in zip(range(len(data.keys())), data.keys()):
                if index == 0:
                    data[key].append(int(team.find_element_by_xpath("td[1]").text))
                elif index == 1:
                    data[key].append(team.find_element_by_xpath("td[2]/span[1]").text)
                else:
                    data[key].append(team.find_element_by_xpath(f"td[{index + 1}]").text)

        last_standings = pd.DataFrame(data=data)
        league_name = self.driver.find_element_by_xpath("//em[@class='team-name']").text
        year = self.driver.find_element_by_xpath("//cite[@id='season']").text
        last_standings.to_csv(os.path.join('data', '_'.join([year, league_name]) + '.csv'), index=False, encoding='utf-8-sig')
        logging.info(f"{year} {league_name} has been download!")
        data = pd.read_csv(os.path.join('data', '_'.join([year, league_name]) + '.csv'), encoding='utf-8')
        #print(data.head(5))
        logging.info(f"{league_name} standings has been collected!")


    def __open_browser(self):
        self.driver.get(self.url)
        time.sleep(2)

    def get_date(self):
        info = self.driver.find_element_by_xpath("//div[@class='info']").text
        league, date, time = info.split()[:3]
        self.result['league'] = league
        self.result['date'] = ' '.join([date, time])
        return league, ' '.join([date, time])

    def get_team_names(self):
        # 获取对阵双方名字和排位
        home_rank = self.driver.find_element_by_xpath("//div[@class='home']//span[1]").text[1:-1]
        home_name = self.driver.find_element_by_xpath("//div[@class='home']//span[2]").text
        # print(home_rank, home_name)
        guest_name = self.driver.find_element_by_xpath("//div[@class='away']//span[1]").text
        guest_rank = self.driver.find_element_by_xpath("//div[@class='away']//span[2]").text[1:-1]
        self.result['home'] = {'team': home_name, 'rank': home_rank}
        self.result['guest'] = {'team': guest_name, 'rank': guest_rank}
        return home_name, home_rank, guest_name, guest_rank

    def get_credit_status(self):
        # 获取联赛积分状态
        home_standing = self.driver.find_element_by_xpath("//div[@class='bd same']//table").text.splitlines()
        guest_standing = self.driver.find_element_by_xpath("//div[@class='bd same ml6']//table").text.splitlines()
        items = ['matched', 'win', 'draw', 'loss', 'gain_scores', 'lost_scores', 'balance', 'credits', 'rank', 'win_rate']
        self.result['league_standing'] = {}
        self.result['league_standing']['home'] = {}
        self.result['league_standing']['guest'] = {}
        for i in range(len(home_standing)):
            # ignore header
            if i == 0:
                continue

            # i == 1: 总计 all
            # i == 2: 主场 as_home
            # i == 3: 客场 as_guest
            title = ['all', 'as_home', 'as_guest']
            h_tmp = home_standing[i].split()
            g_tmp = guest_standing[i].split()
            self.result['league_standing']['home'][title[i - 1]] = {}
            self.result['league_standing']['guest'][title[i - 1]] = {}
            for pos in range(len(h_tmp)):
                if pos == 0:
                    continue

                self.result['league_standing']['home'][title[i - 1]][items[pos - 1]] = h_tmp[pos]
                self.result['league_standing']['guest'][title[i - 1]][items[pos - 1]] = g_tmp[pos]






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
        history_match = self.driver.find_element_by_xpath(
            "//div[@class='porlet' and @id='porlet_3']//table[@class='odds-table']")

        #print(self.driver.page_source)
        self.__save_table(history_match)

        print("+++++++++++++++++++++++++++++")
        # # 同主客
        # self.driver.find_elements_by_xpath("//div[@class='porlet' and @id='porlet_3']//div[@class='conditions']/label")[
        #     0].click()
        # print(self.driver.find_element_by_xpath(
        #     "//div[@class='porlet' and @id='porlet_3']//table[@class='odds-table']").text)
        # 同赛事
        # 同主客，同赛事

    def __save_table(self, table):
        # TODO: 将函数泛化，可以捕捉table的id 抓取所有
        # print(table.text)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        frame = soup.find_all("div", class_="porlet", id="porlet_3")[0]

        company_list = frame.find("tr").find("div", class_="analysis-menu").get_text().split()
        cur_company = frame.find("tr").find("span", "title").get_text()
        self.select_company(cur_company, 3)
        # 遍历table中每一行data
        for tr in frame.find_all("tr")[2:]:
            #print(td.prettify())

            league_name = tr.find("a").get_text()
            print(league_name)
            date = tr.find_all("td", limit=2)[1].get_text()
            print(date)
            print(cur_company)
            print()
            # 遍历某一行中所有cells
            for item in tr.find_all("span")[:-4]:
                # 删除表单中角球的数据
                #print(item.attrs)
                if 'class' in item.attrs:
                    if item['class'][0] in ["icon-corner", "num-corner"]:
                        continue
                print(item.get_text())

            cur_status = frame.find("tr").find_all("span", "title", limit=2)[1].get_text()
            print(cur_status)
            # self.driver.find_element_by_xpath()
            print("+++++++++++++++")

    def select_status(self, cur_status, table):
        # TODO: 对亚培和欧赔都进行切换
        pass

    def select_company(self, cur_company, table):
        """
        选择公司
        :param cur_company:
        :return:
        """
        # TODO: 对亚培，欧赔都进行公司切换
        for span in self.driver.find_elements_by_xpath(
            f"//div[@class='porlet' and @id='porlet_{table}']//table[@class='odds-table']//td[@class='w4'][2]//div["
            "@class='analysis-menu-row']//span"):
            if span.text == cur_company:
                span.click()

    def check_exist(self):
        if os.path.exists(os.path.join('data', 'single', self.save_file)):
            return True
        return False

    def save_record(self):
        if not self.check_exist():
            with open(os.path.join('data', 'single', self.save_file), 'w', encoding='utf-8') as f:
                json.dump(self.result, f, indent=4, ensure_ascii=False)
            f.close()
            logging.info(f"{self.date} -- Home: {self.home} -- Guest: {self.guest} have been saved in {self.save_file}")
        else:
            logging.info(f"The match of {self.home} vs. {self.guest} in {self.date} has been saved!")

    def quit_crawl(self):
        # close chrome browser after collection
        self.driver.quit()

