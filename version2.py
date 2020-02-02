from selenium import webdriver
import time,datetime, os, sys, logging, psycopg2.extras
from config import host_features, browser_connection_settings, db_connection_settings
# Do NOT delete this import.
from resource_methods import bcolors, Work, Dou, Headh, Rabota
from  inspect import currentframe

# TODO Change color of evey message log level
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s')
logger = logging.getLogger(' Job Parser')

# TODO  main
# if __name__ == '__main__':
    # invoke_the_real_code()
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
    config_query  =  "SELECT * FROM  configs WHERE param = 'url' LIMIT 1 ;"
    cur.execute(config_query)
    url  = cur.fetchone()['value']
    config_query = "SELECT * FROM  configs WHERE param = 'session_id' LIMIT 1 ;"
    cur.execute(config_query)
    session_id = cur.fetchone()['value']
    logger.info(bcolors.OKGREEN +  "Cotinued session on: " + url + ";  session_id: " + session_id  + bcolors.ENDC)
    #  todo avoid opening unwanted extra 'data' window
    driver = webdriver.Remote(command_executor=url, desired_capabilities={})
    driver.session_id = session_id
    driver.get('https://www.google.com/')
    logger.info('continued on previous session')
    # todo Define custom exception MaxRetryError
except Exception as e:
    logger.info(e)
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


#testing establishing connection
# exit()

def main(interval):
    # Telegram connection for notifications
    # telegram = TelegramConnection(driver)
    # logger.info(telegram.connect())
    # logger.info("Telegram connected successfully")

    # bot = telegram.Bot(token=telegram_settings['token'])


    while True:
        # setting up counters


        get_users_query = 'SELECT * FROM users;'
        cur.execute(get_users_query)
        users_rows = cur.fetchall()
        for user in users_rows:
            if user['active']:
                user_telegram_id = user['telegram_id']
                checked = 0
                inserted = 0
                get_urls_query = 'SELECT * FROM urls WHERE user_id = {};'.format(user['user_id'])
                cur.execute(get_urls_query)
                urls_rows = cur.fetchall()
                # getting info from pages
                # we have url host func etc
                for row in urls_rows:
                    # calling specific class based on host name
                    logger.info(bcolors.OKBLUE + "Current resource parsing: " + str([row['host']][0])+ bcolors.ENDC)
                    source = globals()[host_features[row['host']]['class']](driver, row['url'], row['target'], user['user_id'])
                    logger.info("{} vacancies found on '{}' regarding '{}'.".format(str(len(source.vacancies)), row['host'], row['target']))
                    for vacancy in source.vacancies:
                        results = vacancy.insert_to_db(cur)
                        checked += results[0]
                        inserted += results[1]
                        # if vacancy is new
                        if results[1] and not user['is_new']:
                            logger.info('notification about {}'.format(vacancy.title))
                            vacancy.send_notification(user_telegram_id, cur)
                    connection.commit()
                    #todo logger time

                if user['is_new']:
                    set_not_new = 'UPDATE "users" SET "is_new" = false WHERE "user_id" = {};'.format(user['user_id'])
                    cur.execute(set_not_new)
                    connection.commit()
                # todo logger Ukrainan time
                logger.info(datetime.datetime.now())

                logger.info("User {} ; checked: {} , inserted: {}.".format(user['user_name'], checked, inserted))
        # break
        # todo logger next iteration time
        logger.info(bcolors.UNDERLINE +'waiting...' + bcolors.ENDC)
        time.sleep(60*15)
    # cur.close()
    # connection.close()



if __name__ == "__main__":
    main(10)