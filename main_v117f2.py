from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colors.colors import red, green, color
from datetime import datetime, timedelta
from speedtest import Speedtest
from statistics import mean
from random import shuffle
from time import sleep
from pyautogui import scroll, position
import keyboard
import threading
import json
import sys
import os

__version__ = "1.1.7f2"

FIREFOX_WEBDRIVER_FILE_PATH = r"firefox_webdriver/geckodriver.exe"
FOLLOWER_DATA_FILE_PATH = r"followers.txt"
FOLLOWER_LEAVES_DATA_FILE_PATH = r"follower_leaves.txt"
FOLLOWER_ACCESSIONS_DATA_FILE_PATH = r"follower_accessions.txt"

GOLD = 226


class Scraper:
    def __init__(self, username, password, target):
        self.username = username
        self.password = password
        self.target = target
        self.data_dir = os.path.dirname(r"data/")
        self.ERROR_101 = False
        self.users = set()
        self.current_follower = []
        self.data_per_follower = 5
        self.follower_per_sec = 0.40
        self.status = 0
        self.error_tries = 0
        self.sub_count = 0
        self.timestamp_2 = None
        self.FST = None
        self.file_id = None
        self.download_result = 1
        self.time_left = None

    def download_test(self):
        self.check_for_data()
        with open(fr"{self.data_dir}/{self.file_id}.json", encoding="utf-8") as json_file:
            try:
                download_list = []
                data_list = json.load(json_file)
                if data_list:  # check if list is empty
                    for data_package in data_list:
                        try:
                            if data_package["download"] is not None:
                                download_list.append(data_package["download"])
                        except KeyError:
                            pass
                    if download_list:  # checks if list is empty
                        self.data_per_follower = mean(download_list)
            except (json.decoder.JSONDecodeError, AttributeError):
                pass

        dl_test = Speedtest()
        dl_test.get_servers()
        dl_test.get_best_server()
        download_result = dl_test.download()
        self.download_result = download_result / 1024 / 1024  # Mbit/s

        print(green("download_test passed. ✓"))

    def open_page(self, url):
        self.driver.get(url)

        # accept cookies
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.aOOlW:nth-child(2)"))).click()

    def login(self):
        # fill inputs
        username = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        password = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
        username.clear()
        password.clear()
        username.send_keys(self.username)
        password.send_keys(self.password)

        # press submit_button
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        except ElementClickInterceptedException:
            sleep(1)
            self.login()

        return True

    def dismiss_popups(self):
        for i in range(2):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Jetzt nicht']"))).click()
                sleep(1)
            except TimeoutException:
                sleep(1)
                self.dismiss_popups()

        return True

    def goto_profile(self):
        self.driver.get(f"https://www.instagram.com/{self.target}/")
        return True

    def get_subs(self):
        input(color("Click on 'followers' to open the follower list. If you done that press Enter.", fg=GOLD))

        try:
            sub_count_atr = self.driver.find_elements_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[2]/a/div/span')
            if "." in sub_count_atr[0].get_attribute('title'):
                self.sub_count = int(sub_count_atr[0].get_attribute('title').replace(".", ""))
            else:
                self.sub_count = int(sub_count_atr[0].get_attribute('title'))
        except IndexError:
            try:
                sub_count_atr = self.driver.find_elements_by_xpath(
                    '/html/body/div[1]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[2]/a/div/span')
                if "." in sub_count_atr[0].get_attribute('title'):
                    self.sub_count = int(sub_count_atr[0].get_attribute('title').replace(".", ""))
                else:
                    self.sub_count = int(sub_count_atr[0].get_attribute('title'))
            except ValueError:
                self.sub_count = 1

        print(color("1. - Place your mouse on the scrollbox.\n"
                    '2. - Press the "x" and "y" key at the same time. ', fg=GOLD))

        while True:
            keyboard.wait("x+y")
            break
        x1, y1 = position()

        '''
        follower_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]/ul/div')))
        follower_box.click()
        '''

        def status_thr():
            self.check_for_data()
            with open(fr"{self.data_dir}/{self.file_id}.json", encoding="utf-8") as json_file:
                try:
                    dpf_list = []  # data_per_follower - list
                    fps_list = []  # follower_per_sec - list
                    data_list = json.load(json_file)
                    if data_list:  # check if list is empty
                        for data_package in data_list:
                            try:
                                if data_package["data_per_follower"] is not None:
                                    dpf_list.append(data_package["data_per_follower"])
                                if data_package["follower_per_sec"] is not None:
                                    fps_list.append(data_package["follower_per_sec"])
                            except KeyError:
                                pass
                        if dpf_list:  # checks if list is empty
                            self.data_per_follower = mean(dpf_list)
                        if fps_list:  # checks if list is empty
                            self.follower_per_sec = mean(fps_list)
                except (json.decoder.JSONDecodeError, AttributeError):
                    pass

            while self.status < 100 and self.ERROR_101 is False:  # 100% max
                os.system('cls')
                time_dpf = ((self.sub_count - len(self.users)) * self.data_per_follower) / self.download_result
                time_fps = (self.sub_count - len(self.users)) * self.follower_per_sec
                self.time_left = (time_dpf + time_fps) / 2
                if self.time_left is None:
                    print(f"Status: {int(self.status)}%")
                elif self.time_left > 60:
                    print(f"Status: {int(self.status)}% ({int(round(self.time_left / 60))} minute(s) left)")
                elif self.time_left <= 60:
                    print(f"Status: {int(self.status)}% ({int(round(self.time_left))} second(s) left)")
                sleep(1)
            else:
                sys.exit()

        threading.Thread(target=status_thr).start()

        def scroll_get_followers():
            # ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
            scroll(-1000000, x=x1, y=y1)

            sleep(1)

            for n in range(self.sub_count):
                # user without story
                followers = self.driver.find_elements_by_xpath(
                    f'/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]/ul/div/li[{n + 1}]/div/div[1]/div/div/a/img')

                try:
                    if followers[0].get_attribute('alt'):
                        self.users.add(followers[0].get_attribute('alt')[:-12])  # s Profilbild --> 12 Zeichen
                        if self.status < 100:  # 100% max
                            self.status = round(100 * len(self.users) / self.sub_count, 0)
                    else:
                        print("UNDEFINED USER!")
                except IndexError:
                    pass

                # user with story
                followers = self.driver.find_elements_by_xpath(
                    f'/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[2]/ul/div/li[{n + 1}]/div/div[1]/div[1]/div/span/img')
                try:
                    if followers[0].get_attribute('alt'):
                        self.users.add(followers[0].get_attribute('alt')[:-12])  # s Profilbild --> 12 Zeichen
                        if self.status < 100:  # 100% max
                            self.status = round(100 * len(self.users) / self.sub_count, 0)
                    else:
                        print("UNDEFINED USER!")
                except IndexError:
                    pass

        timestamp_1 = datetime.now()

        for _ in range((self.sub_count // 10) + 5):
            scroll_get_followers()

        # checks if one more scroll is needed
        def error_check():
            if len(self.users) < self.sub_count:
                scroll_get_followers()
                self.error_tries += 1
                if len(self.users) < self.sub_count:
                    if self.error_tries < 5:  # 5th time => error message
                        error_check()
                    else:
                        self.ERROR_101 = True
                        print(red(
                            f"ERROR (101): Followers could not be completely scraped. ({len(self.users)}/{self.sub_count})"))
                        inp = input(red(f"Do you want to save {len(self.users)}/{self.sub_count} followers? (y/n): "))
                        # print(self.users)
                        if inp == "n" or inp == "N":
                            # self.FST = timedelta.total_seconds(timestamp_2 - timestamp_1)
                            # self.save_data()
                            exit(-1)
                        elif inp == "y" or inp == "Y":
                            pass

        error_check()

        timestamp_2 = datetime.now()

        self.FST = timedelta.total_seconds(timestamp_2 - timestamp_1)
        print(red(f"FST: {self.FST} sec(s)"))  # Follower Srape Time
        print(red(f"ERROR TRIES: {self.error_tries}"))
        print(f"Status: 100%")

        self.current_follower = list(self.users)

        os.system('cls')
        return True

    def get_sub_leaves_newbies(self):
        if os.path.isfile(FOLLOWER_DATA_FILE_PATH):
            with open(FOLLOWER_DATA_FILE_PATH, "r") as file:
                old_followers = file.read().split('\n')
                old_followers = old_followers[:-1]  # one empty line left cause of /n
                # print(self.old_followers)
                # print(type(self.old_followers))
                # print(len(self.old_followers))

            if len(old_followers) > 0:
                # sub_leaves ----------------------------------------------------------------
                sub_leaves = []
                for i in old_followers:
                    if i not in self.current_follower:
                        sub_leaves.append(i)
                print(color(f"{len(sub_leaves)} follower leave(s) was/were found.", fg=GOLD))
                if len(sub_leaves) > 0:
                    with open(FOLLOWER_LEAVES_DATA_FILE_PATH, "w") as file:
                        file.write('\n'.join(sub_leaves) + "\n")
                # ----------------------------------------------------------------------------
                # sub_newbies ----------------------------------------------------------------
                sub_newbies = []
                for i in self.current_follower:
                    if i not in old_followers:
                        sub_newbies.append(i)
                print(color(f"{len(sub_newbies)} follower accession(s) was/were found.", fg=GOLD))
                if len(sub_newbies) > 0:
                    with open(FOLLOWER_ACCESSIONS_DATA_FILE_PATH, "w") as file:
                        file.write('\n'.join(sub_newbies) + "\n")
                # ----------------------------------------------------------------------------

        with open(FOLLOWER_DATA_FILE_PATH, "w") as file:
            file.write('\n'.join(self.current_follower) + "\n")

        return True

    def check_for_data(self):
        def create_user_data():
            # generate ID from current date and time
            date_time = str(datetime.now())[:-10]
            rep_chars = "-:0 "
            for char in rep_chars:
                date_time = date_time.replace(char, "")
            list_date_time = list(date_time)
            shuffle(list_date_time)
            self.file_id = "ID_" + "".join(list_date_time)

            with open(fr"{self.data_dir}/{self.file_id}.json", "w", encoding="utf-8") as fw:
                default_list = []
                json.dump(default_list, fw, indent=4)

        user_data = False
        # check dir ------------------------------------------
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        # ----------------------------------------------------

        # check files -----------------------------------------
        if not os.listdir(self.data_dir):
            create_user_data()
        else:
            for file in os.listdir(self.data_dir):
                if file.endswith(".json"):
                    self.file_id = file[:-5]
                    user_data = True
                    break
            if not user_data:
                create_user_data()
        # ----------------------------------------------------

    def save_data(self):
        self.check_for_data()
        # needs to be closed before rename if error 202
        json_file = open(fr"{self.data_dir}/{self.file_id}.json", encoding="utf-8")
        # check if sub_count is at least 1 --> FST/0 --> div_0 error
        if not self.sub_count == 0:
            new_data_entry = {"followers": len(self.users),
                              "FST": self.FST,
                              "download": self.download_result,
                              "follower_per_sec": self.FST / len(self.users),
                              "data_per_follower": (self.FST * self.download_result) / len(self.users)}
        else:
            new_data_entry = {"followers": self.sub_count,
                              "FST": self.FST,
                              "download": self.download_result,
                              "follower_per_sec": None,
                              "data_per_follower": None}
        try:
            data_list = json.load(json_file)
            data_list.append(new_data_entry)
            with open(fr"{self.data_dir}/{self.file_id}.json", "w", encoding="utf-8") as fw:
                json.dump(data_list, fw, indent=4)
        except (json.decoder.JSONDecodeError, AttributeError) as err:
            json_file.close()
            os.rename(fr"{self.data_dir}/{self.file_id}.json", fr"{self.data_dir}/{self.file_id}.txt")
            print(red(f"ERROR (202): Data could not be saved. ({err})"))
            exit(-1)

        return True

    def start(self):
        self.driver = webdriver.Firefox(executable_path=FIREFOX_WEBDRIVER_FILE_PATH)
        self.open_page("https://www.instagram.com/")

        download_test_thr = threading.Thread(target=self.download_test)
        download_test_thr.start()

        login = self.login()
        if login:
            print(green("login passed. ✓"))

        dismiss_popups = self.dismiss_popups()
        if dismiss_popups:
            print(green("dismiss_popups passed. ✓"))

        goto_profile = self.goto_profile()
        if goto_profile:
            print(green("goto_profile passed. ✓"))

        get_subs = self.get_subs()
        if get_subs:
            print(green("get_subs passed. ✓"))

        get_sub_leaves = self.get_sub_leaves_newbies()
        if get_sub_leaves:
            print(green("get_sub_leaves_newbies passed. ✓"))

        save_data = self.save_data()
        if save_data:
            print(green("save_data passed. ✓"))

        def finish_info():
            while True:
                if not download_test_thr.is_alive():
                    print(color("All tests passed.", fg=GOLD))
                    break

        finish_info()


if __name__ == '__main__':
    print(__version__)
    username = input("Type in your Instagram username: ")
    password = input("Type in your Instagram password: ")
    # target = input("Type in your Instagram target: ")
    os.system('cls')

    Scraper(username, password, username).start()
    # scraper2 = Scraper(username, password, username)
    # scraper3 = Scraper(username, password, username)
