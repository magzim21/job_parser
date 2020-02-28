from selenium import webdriver
import time,datetime, sys, logging, psycopg2.extras, telegram, os
from config import host_features, browser_connection_settings, db_connection_settings
from classes import bcolors,Link, User, Work, Dou, Headh, Rabota,Vacancy

# TODO Change color of evey message log level
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s')
logger = logging.getLogger(' Job Parser')

# TODO  main

# DB connection
try:
    connection = psycopg2.connect(**db_connection_settings)
    cur = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    logger.info(bcolors.OKGREEN+"DB CONNECTED"+ bcolors.ENDC)
except (Exception, psycopg2.Error) as error:
    logger.info(bcolors.FAIL+"Error while connecting to PostgreSQL" + bcolors.ENDC +"\n"+ str(error))
    exit()

# according to module features, better to initialize browser outside functions.
# This will prevent browser from quiting after program ends.
# todo figure out which location work.ua determines for aws


try:
    logger.info("Trying to start new session")
    # todo make Chrome dynamic by get getattr
    chrome_options = webdriver.ChromeOptions()
    # This lines are makes chrome able to run as a service (also in a Docker file)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path=browser_connection_settings['new_session'], options=chrome_options)
    driver.set_page_load_timeout(5) # this will stop page ever loading
    logger.info(bcolors.OKGREEN+"New Chrome session started" + bcolors.ENDC)
    url = driver.command_executor._url
    session_id = driver.session_id
    update_config_query = 'UPDATE configs SET value = %(url)s WHERE param = \'url\';' \
                          'UPDATE configs SET value = %(session_id)s WHERE param = \'session_id\';'
    substitution = {"url" : url,"session_id":  session_id}
    cur.execute(update_config_query,substitution)
    connection.commit()
    #todo auto-update current session
    logger.info(bcolors.OKGREEN + 'Web driver info:\nurl(port): {} , session_id: {}'.format(driver.command_executor._url, driver.session_id) + bcolors.ENDC)
except Exception as e:
    logger.info(e)
    logger.info(bcolors.FAIL + "Chrome driver failed to start" + bcolors.ENDC)
    exit(1)

def main(interval):
    Link.driver = driver  # setting up a class property that gives chrome driver access to it's instances
    cur.execute('SELECT "url" FROM "positions";')
    Link.old_vacancies = set(i[0] for i in cur.fetchall()) # saving all previously found positions for comparing. Using set type for a faster search.
    Vacancy.cursor = cur  # setting up a class property that gives database access to it's instances
    Vacancy.bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])  # setting up a class property that gives Telegram connection to it's instances
    while True:
        # Creating users instances
        get_users_query = 'SELECT * FROM users;'
        cur.execute(get_users_query)
        users_rows = cur.fetchall()
        users = []
        for user in users_rows:
            users.append(User(user['user_id'], user['user_name'],user['telegram_id'],user['active'],user['is_new']))

        for user in users:
            if user.active:
                just_counter, checked, inserted = 0, 0, 0 # counters
                get_urls_query = 'SELECT * FROM urls WHERE user_id = {};'.format(user.id)
                cur.execute(get_urls_query)
                urls_rows = cur.fetchall()
                for row in urls_rows:
                    # logger.info(bcolors.OKBLUE + "Current resource parsing: " + str([link.host][0]) + bcolors.ENDC)
                    link = globals()[host_features[row['host']]['class']](row['url'], row['target'], user.id)
                    user.links.append(link)
                    logger.info("{} vacancies found on '{}' regarding '{}'.".format(str(len(link.vacancies)), link.host, link.target))
                for link in user.links:
                    for vacancy in link.vacancies:
                        results = vacancy.insert_to_db()
                        just_counter +=1
                        checked += results[0]
                        inserted += results[1]
                        if results[1] and not user.is_new:
                            logger.info('notification about {}'.format(vacancy.title))
                            vacancy.send_notification(user.telegram_id)
                    connection.commit() # do i need this?
                if user.is_new:
                    set_not_new = 'UPDATE "users" SET "is_new" = false WHERE "user_id" = {};'.format(user.id)
                    cur.execute(set_not_new)
                    connection.commit()
                logger.info(datetime.datetime.now())

                logger.info("User {} ; checked: {} , inserted: {}.".format(user.user_name, checked, inserted))
                logger.info(str(just_counter))
        logger.info(bcolors.UNDERLINE +'waiting...' + bcolors.ENDC)
        time.sleep(60*15)
    # cur.close()
    # connection.close()



if __name__ == "__main__":
    main(10)