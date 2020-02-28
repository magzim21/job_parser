from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
import time, psycopg2.extras


# todo add user class (include positions, urls, user_telegram_id)
# todo method should use inner attributes: _example

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Link(BeautifulSoup):
    _driver: type  # Chrome
    _old_vacancies: set # known vacancies
    def __init__(self, raw_html):
        if not hasattr(self, 'driver'):
            raise AttributeError('Chrome is not set')
        self._vacancies = []
        super().__init__(raw_html, "html.parser")

    @property
    def driver(self): # database cursor
        return self._driver
    @driver.setter
    def driver(self, value):
        self._driver = value
    @property
    def old_vacancies(self): # database cursor
        return self._old_vacancies
    @old_vacancies.setter
    def old_vacancies(self, value):
        self._old_vacancies = value
    @property
    def url(self): # example "https://www.work.ua/jobs-kyiv-devops/"
        return self._url
    @property
    def host(self): # example "work.ua"
        return self._host
    @property
    def vacancies(self): # example [<class Vacancy>, <class Vacancy>, <class Vacancy>...]
        return self._vacancies
    @property
    def raw_html(self): # example "<!DOCTYPE html><html><body><p>This is a jobpars..."
        return self._raw_html
    @property
    def target(self): # example "devops"
        return self._target
    @property
    def user_id(self): # user's telegram id who is tied up with link. Example 123456789.
        return self._user_id
    @property
    def prev_links(self): # all vacancy links found for this user
        return self._prev_links


class User:
    def __init__(self, id: int, user_name: str, telegram_id: int, active: bool, is_new: bool) -> object:
        self._id = id
        self._user_name = user_name
        self._telegram_id = telegram_id
        self._active = active
        self._is_new = is_new
        self._links = []

    
    
    
    @property
    def id(self):
        return self._id
    @property
    def user_name(self):
        return self._user_name
    @property
    def telegram_id(self):
        return self._telegram_id
    @property
    def active(self):
        return self._active
    @property
    def is_new(self):
        return self._is_new
    @property
    def links(self):
        return self._links
        
        
        


class Dou(Link):
    def __init__(self, page_url, target, user_id):
        self._host = 'jobs.dou.ua'
        self._url = page_url
        self._target = target
        self._user_id = user_id
        self.driver.get(self._url)
        # clicking "more" button as many times as possible to chow all vacancies
        try:
            while True:
                time.sleep(1.5)
                more_btn = self.driver.find_element(By.LINK_TEXT, 'Больше вакансий')
                more_btn.click()
        except Exception as e:
            pass
        self._raw_html = self.driver.page_source
        super().__init__(self._raw_html)
        vacancy_divs = self.select('.vacancy')
        for vacancy in vacancy_divs:
            vacancy_url = vacancy.select_one('.vt').get('href')
            title = vacancy.select_one('.vt').getText().strip()
            try:
                company = vacancy.select_one('.company').getText().strip()
            except:
                company = 'not specified'  # company name may not be specified
            self.vacancies.append(Vacancy(self._host, vacancy_url, title, company, self._target, self))


class Rabota(Link):
    def __init__(self, page_url, target, user_id):
        self._host = 'rabota.ua'
        self._url = page_url
        self._target = target
        self._user_id = user_id
        self.driver.get(self._url)
        self._raw_html = ''
        # clicking "more" button as many times as possible to show all vacancies
        try:
            while True:
                time.sleep(1.5)
                self._raw_html += self.driver.page_source # collecting page source from all pagination
                more_btn = self.driver.find_element_by_xpath('//a[contains(text(),\'Следующая\')]')
                more_btn.click()
        # todo exception is too broad
        except Exception as e:
            pass # pages ended
        super().__init__(self._raw_html)
        vacancy_divs = self.select('.f-vacancylist-vacancyblock')
        for vacancy in vacancy_divs:
            vacancy_url = self._host + vacancy.select_one('.f-visited-enable.ga_listing').get('href')
            title = vacancy.select_one('.f-visited-enable.ga_listing').getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one('.f-text-dark-bluegray.f-visited-enable').getText().strip()
            except:
                company = 'not specified'

            self._vacancies.append(Vacancy(self._host, vacancy_url, title, company, self._target, self))


class Headh(Link):
    def __init__(self, page_url, target, user_id):
        self._host = 'hh.ua'
        self._url = page_url
        self._target = target
        self._user_id = user_id
        self.driver.get(self._url)
        self._raw_html = ''
        # clicking "more" button as many times as possible to chow all vacancies
        try:
            while True:
                time.sleep(1.5)
                self._raw_html += self.driver.page_source # collecting page source from all pagination
                self.driver.execute_script("window.stop();")
                element = self.driver.find_element_by_class_name('saved-search-subscription-wrapper')
                self.driver.execute_script("arguments[0].style.visibility='hidden'", element)
                more_btn = self.driver.find_element_by_xpath('//a[contains(text(),\'дальше\')]')
                more_btn.click()
        # todo exception is too broad. If selectors change, I will know about that.
        except Exception as e:
            pass # Pages ended
        super().__init__(self._raw_html)
        vacancy_divs = self.select('.vacancy-serp-item')
        for vacancy in vacancy_divs:
            vacancy_url = vacancy.select_one('.HH-LinkModifier').get('href')
            title = vacancy.select_one('.HH-LinkModifier').getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one('.bloko-link_secondary').getText().strip()
            except:
                company = 'not specified'
            self._vacancies.append(Vacancy(self._host, vacancy_url, title, company, self._target, self))


class Work(Link):
    def __init__(self, page_url, target, user_id):
        self._host = 'work.ua'
        self._url = page_url
        self._target = target
        self._user_id = user_id
        self.driver.get(self._url)
        # clicking "more" button as many times as possible to chow all vacancies
        self._raw_html = ''
        try:
            while True:
                time.sleep(1.5)
                self._raw_html += self.driver.page_source   # collecting page source from all pagination
                more_btn = self.driver.find_element_by_css_selector('.pagination li:last-child a')
                more_btn.click()
        # todo too broad exception
        except Exception as e:
            pass

        super().__init__(self._raw_html)
        vacancy_divs = self.select('.job-link')
        for vacancy in vacancy_divs:
            vacancy_url = self._host + vacancy.select_one('h2 a').get('href')
            title = vacancy.select_one('h2 a').getText().strip()
            # company name may not be specified
            try:
                company = vacancy.select_one('.job-link img').get('alt').strip()
            except:
                company = 'not specified'
            self._vacancies.append(Vacancy(self._host, vacancy_url, title, company, self._target, self))


class Vacancy:
    _bot: type  # Telegram connection
    _cursor: type  # Connected Data Base's cursor

    def __init__(self, host, url, title, company, target, link_parrent):
        if not hasattr(self, 'cursor'):
            raise AttributeError('Database cursor is not set')
        if not hasattr(self, 'bot'):
            raise AttributeError('Telegram connnection is not set')

        self._host = host # example: 'jobs.dou.ua'
        self._url = url # example: 'https://jobs.dou.ua/vacancies/?city=Kyiv&search=devops'
        self._title = title # example: 'DevOps Engineer'
        self._applied = False # for future use
        self._company = company # example: 'epam'
        self._target = target # example: 'devops'
        self._link_parrent = link_parrent # it is a kind of conditional inheritance

        # checking if position is new one
        if self._url in self.link_parrent.old_vacancies:
            self._new = False
        else:
            self._new = True

    @property
    def bot(self):
        return self._bot
    @bot.setter
    def bot(self,value):
        self._bot=value
    @property
    def cursor(self):
        return self.cursor
    @cursor.setter
    def cursor(self,connection):
        self.cursor=connection.cursor(cursor_factory = psycopg2.extras.DictCursor) # todo rewrite - make it easier
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
    def new(self):
        return self._new
    @property
    def link_parrent(self):
        return self._link_parrent

    def insert_to_db(self):
        checked = 1
        inserted = 0
        if self.new:
            insert_query = 'INSERT INTO "public"."positions" ("host", "url", "title", "company", "target", "user_id")' \
                           ' VALUES (%(host)s, %(url)s,%(title)s, %(company)s, %(target)s, %(user_id)s) ;'
            substitution = {"host": self.host, "url": self.url, "title": self.title, "company": self.company,
                            "target": self.target, "user_id": self.link_parrent.user_id}
            self.cursor.execute(insert_query, substitution)
            inserted = 1
        else:
            pass
        return checked, inserted

    def apply(self):
        # todo auto apply button
        pass

    def send_notification(self, user_telegram_id):
        notifivation_msg = 'Опубликована новая вакансия на {host}.\nНазвание: {title}\nКомпания: {company}\nСсылка: {url}' \
            .format(host=self.host, title=self.title, company=self.company, url=self.url)
        try:
            self.bot.send_message(chat_id=str(user_telegram_id), text=notifivation_msg)
        except Exception as exception:
            print(exception)
            print('Could not notify about : ' + notifivation_msg) # # todo high priority log

        else: # this block executes if no exception was raised
            update_notified_querry = 'UPDATE "positions" SET "notified" = TRUE WHERE ("user_id" = \'{}\' AND "url" = \'{}\');'.format(
                self.link_parrent.user_id, self.url)
            self.cursor.execute(update_notified_querry)





