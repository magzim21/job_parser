from urllib.request import urlopen
from bs4 import BeautifulSoup
from config import host_features, telegram_connection,  telegram_settings, db_connection_settings
# ETO NE KRUTO. Импортируй класс(как всегда) Но чтобы не прокидывать каждому обьекту подключение - сделай его свойством класса постфактум в version1.py
# from version1 import  db_connection_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import telegram
import smtplib
import psycopg2
import psycopg2.extras


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TelegramConnection:
    def __init__(self,driver):
        self.login_page = "https://web.telegram.org"
        self.phone_number = telegram_connection['phone_number']
        self.country = telegram_connection['country']
        self.chat_to_send_msgs = telegram_connection['chat_to_send_msgs']
        self.driver = driver
        self.texting_delay = telegram_connection['texting_delay']

    def connect(self):
        self.driver.get(self.login_page)
        # letting page to download
        time.sleep(3)
        # try block is for the case if we logged out. It is all about logging in.
        try:
            select_country_elem = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[1]/div/div[2]/div[2]/form/div[1]/div')
            select_country_elem.click()
            search_country_input = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[5]/div[2]/div/div/div[2]/div[1]/input')
            search_country_input.send_keys(self.country)
            ukraine_option = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[5]/div[2]/div/div/div[2]/div[2]/div/div[1]/ul/li/a')
            ukraine_option.click()
            phone_elem = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input')
            phone_elem.send_keys(self.phone_number)
            # just not hurry up (not acting like a bot)
            time.sleep(3)
            submit_btn = self.driver.find_element_by_xpath('//*[@id="ng-app"]/body/div[1]/div/div[2]/div[1]/div/a/my-i18n')
            submit_btn.click()
            confirm_mobnum_key = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[5]/div[2]/div/div/div[2]/button[2]/span')
            confirm_mobnum_key.click()
            time.sleep(2)
            too_many_tries_error = self.driver.find_element_by_css_selector('.error_modal_description')
            if too_many_tries_error:
                print('Too many attempts to connect! Try again later.')
                exit()
            pass_key = input('Enter Telegram auth key: ')
            pass_key_input = self.driver.find_element_by_xpath(
                '//*[@id="ng-app"]/body/div[1]/div/div[2]/div[2]/form/div[4]/input')
            pass_key_input.send_keys(pass_key)
            # if key correct auto fill fires
        except:
            print('Telegram connection logging in was failed')
            exit(1)

    def open(self):
        time.sleep(2)
        find_chat_input = self.driver.find_element_by_xpath(
            '//*[@id="ng-app"]/body/div[1]/div[2]/div/div[1]/div[1]/div/input')
        find_chat_input.clear()
        find_chat_input.send_keys(self.chat_to_send_msgs)
        time.sleep(1)
        our_chat_option = self.driver.find_element_by_css_selector('.im_dialog_wrap')
        our_chat_option.click()
        time.sleep(1)

    def send_message(self, text):
        enter_msg_input = self.driver.find_element_by_css_selector('.composer_rich_textarea')
        enter_msg_input.clear()
        enter_msg_input.send_keys(text)
        send_btn = self.driver.find_element_by_css_selector('.im_submit_send')
        send_btn.click()
        time.sleep(self.texting_delay)

# mailer = Gmail('smtp.gmail.com')
# class Gmail(smtplib.SMTP):
#     def __init__(self,smtp_service):
#         super().__init__(smtp_service)

class Dou(BeautifulSoup):
    def __init__(self, driver, page_url, target, user_id):
        self._host = 'jobs.dou.ua'
        self._url = page_url
        self._target = target
        self._vacancies = []
        self._user_id = user_id
        driver.get(self._url)
        # clicking "more" button as many times as possible to chow all vacancies
        try:
            while True:
                time.sleep(1.5)
                more_btn = driver.find_element(By.LINK_TEXT, host_features[self._host]['more'])
                more_btn.click()
        except Exception as e:
            # print('resource methods file:')
            # print(e)
            pass
        self._raw_html = driver.page_source
        super().__init__(self._raw_html,  "html.parser")
        # every host has own selector
        vacancy_divs = self.select(host_features[self._host]['block'])
        # print(vacancy_divs)
        for vacancy in vacancy_divs:
            # print(type(vacancy.select(selectors[host]['link'])))
            vacancy_url = vacancy.select_one(host_features[self._host]['link']).get('href')
            title = vacancy.select_one(host_features[self._host]['link']).getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one(host_features[self._host]['company']).getText().strip()
            except:
                company = 'not specified'
            # self._vacancies.append(Vacancy(self._host, vacancy_url, title, company, target))

            self.vacancies.append(Vacancy(self.host, vacancy_url, title, company, self.target,self.user_id))

    @property
    def url(self):
        return self._url
    @property
    def host(self):
        return self._host
    @property
    def vacancies(self):
        return self._vacancies
    @property
    def raw_html(self):
        return self._raw_htm
    @property
    def target(self):
        return self._target
    @property
    def user_id(self):
        return self._user_id


class Headh(BeautifulSoup):
    def __init__(self, driver, page_url, target, user_id):
        self._host = 'hh.ua'
        self._url = page_url
        self._target = target
        self._vacancies = []
        self._user_id = user_id
        driver.get(self._url)
        # super().__init__(self._raw_html, "html.parser")
        # clicking "more" button as many times as possible to chow all vacancies
        self._raw_html = ''
        try:
            while True:
                time.sleep(1.5)
                # collecting page source from all pagination
                self._raw_html += driver.page_source
                element = driver.find_element_by_class_name('saved-search-subscription-wrapper')
                driver.execute_script("arguments[0].style.visibility='hidden'", element)
                more_btn = driver.find_element_by_xpath(host_features[self._host]['more'])
                more_btn.click()

                # more_btn = driver.find_element(By.LINK_TEXT, host_features[self._host]['more'])
                # more_btn.click()
        except Exception as e:
            pass
            # print('resource methods file:')
            # print(e)

        super().__init__(self._raw_html, "html.parser")
        # every host has own selectors
        vacancy_divs = self.select(host_features[self._host]['block'])
        for vacancy in vacancy_divs:
            vacancy_url = vacancy.select_one(host_features[self._host]['link']).get('href')
            title = vacancy.select_one(host_features[self._host]['link']).getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one(host_features[self._host]['company']).getText().strip()
            except:
                company = 'not specified'
            self._vacancies.append(Vacancy(self.host, vacancy_url, title, company, self.target,self.user_id))

    @property
    def url(self):
        return self._url

    @property
    def host(self):
        return self._host

    @property
    def vacancies(self):
        return self._vacancies
    @property
    def raw_html(self):
        return self._raw_htm
    @property
    def target(self):
        return self._target
    @property
    def user_id(self):
        return self._user_id

class Rabota(BeautifulSoup):
    def __init__(self, driver, page_url, target, user_id):
        self._host = 'rabota.ua'
        self._url = page_url
        self._target = target
        self._vacancies = []
        self._user_id = user_id
        driver.get(self._url)
        # super().__init__(self._raw_html, "html.parser")
        # clicking "more" button as many times as possible to chow all vacancies
        self._raw_html = ''
        try:
            while True:
                time.sleep(1.5)
                # collecting page source from all pagination
                self._raw_html += driver.page_source
                # time.sleep(5)
                more_btn = driver.find_element_by_xpath(host_features[self._host]['more'])
                more_btn.click()

                # more_btn = driver.find_element(By.LINK_TEXT, host_features[self._host]['more'])
                # more_btn.click()
        except Exception as e:
            pass
            # print('resource methods file:')
            # print(e)

        super().__init__(self._raw_html, "html.parser")
        # every host has own selectors
        vacancy_divs = self.select(host_features[self._host]['block'])
        for vacancy in vacancy_divs:
            vacancy_url = self._host + vacancy.select_one(host_features[self._host]['link']).get('href')
            title = vacancy.select_one(host_features[self._host]['link']).getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one(host_features[self._host]['company']).getText().strip()
            except:
                company = 'not specified'
            self._vacancies.append(Vacancy(self.host, vacancy_url, title, company, self.target,self.user_id))

    @property
    def url(self):
        return self._url

    @property
    def host(self):
        return self._host

    @property
    def vacancies(self):
        return self._vacancies
    @property
    def raw_html(self):
        return self._raw_htm
    @property
    def target(self):
        return self._target
    @property
    def user_id(self):
        return self._user_id


class Work(BeautifulSoup):
    def __init__(self, driver, page_url, target, user_id):
        self._host = 'work.ua'
        self._url = page_url
        self._target = target
        self._vacancies = []
        self._user_id = user_id
        driver.get(self._url)
        # super().__init__(self._raw_html, "html.parser")
        # clicking "more" button as many times as possible to chow all vacancies
        self._raw_html = ''
        try:
            while True:
                # collecting page source from all pagination
                time.sleep(1.5)
                self._raw_html += driver.page_source
                # time.sleep(5)
                # breakpoint()
                more_btn = driver.find_element_by_css_selector  (host_features[self._host]['more'])
                more_btn.click()

                # more_btn = driver.find_element(By.LINK_TEXT, host_features[self._host]['more'])
                # more_btn.click()
        except Exception as e:
            # print(e)
            pass
            # print('resource methods file:')
            # print(e)

        super().__init__(self._raw_html, "html.parser")
        # every host has own selectors
        vacancy_divs = self.select(host_features[self._host]['block'])
        for vacancy in vacancy_divs:
            vacancy_url = self._host + vacancy.select_one(host_features[self._host]['link']).get('href')
            title = vacancy.select_one(host_features[self._host]['link']).getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one(host_features[self._host]['company']).getText().strip()
            except:
                company = 'not specified'
            self._vacancies.append(Vacancy(self.host, vacancy_url, title, company, self.target, self.user_id))

    @property
    def url(self):
        return self._url

    @property
    def host(self):
        return self._host

    @property
    def vacancies(self):
        return self._vacancies
    @property
    def raw_html(self):
        return self._raw_htm
    @property
    def target(self):
        return self._target
    @property
    def user_id(self):
        return self._user_id

class Vacancy:
    # todo class properties лучше задавать в version1
    bot =  telegram.Bot(token=telegram_settings['token'])
    connection = psycopg2.connect(**db_connection_settings)
    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    def __init__(self, host, url, title, company, target, user_id):
        self._host = host
        self._url = url
        self._title = title
        self._applied = False
        self._company = company
        self._target = target
        self._user_id = user_id

        check_querry = 'SELECT * FROM "positions" WHERE "url" = \'{url}\' AND "user_id" = \'{user_id}\';'.format(
            url=self.url, user_id=self.user_id)
        self.cur.execute(check_querry)
        result = self.cur.fetchall()
        if result:
            self._new = False
        else:
            self._new = True


    @property
    def host(self):
        return self._host
    @property
    def url(self):
        return self._url
    @property
    def title(self):
        return self._title
    @property
    def applied(self):
        return self._applied
    @property
    def company(self):
        return self._company
    @property
    def target(self):
        return self._target
    @property
    def user_id(self):
        return self._user_id
    @property
    def new(self):
        return self._new

    def insert_to_db(self, cur):
        checked = 1
        inserted = 0
        if self.new:
            insert_query = 'INSERT INTO "public"."positions" ("host", "url", "title", "company", "target", "user_id")' \
                 ' VALUES (%(host)s, %(url)s,%(title)s, %(company)s, %(target)s, %(user_id)s) ;'
            substitution = {"host": self.host, "url": self.url, "title": self.title, "company": self.company, "target": self.target, "user_id": self.user_id }
            cur.execute(insert_query, substitution)
            inserted = 1

        else:
            pass
            # print(check_querry)
        return checked, inserted

    def apply(self):
        pass

    def send_notification(self, user_telegram_id, cur):
        notifivation_msg = 'Опубликована новая вакансия на {host}.\nНазвание: {title}\nКомпания: {company}\nСсылка: {url}' \
            .format(host=self.host, title=self.title, company=self.company, url=self.url)
        try:
            self.bot.send_message(chat_id=str(user_telegram_id), text = notifivation_msg)
        except Exception as exception:
            # assert type(exception).__name__ == 'NameError'
            # assert exception.__class__.__name__ == 'NameError'
            print(exception)
            print('Could not notify about : ' + notifivation_msg)

        else:
            update_notified_querry = 'UPDATE "positions" SET "notified" = TRUE WHERE ("user_id" = \'{}\' AND "url" = \'{}\');'.format(
                self.user_id, self.url)
            cur.execute(update_notified_querry)

        
        
