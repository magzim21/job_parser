from selenium import webdriver
import time, os, datetime, psycopg2.extras
from config import host_features, browser_connection_settings, telegram_settings
# Do NOT delete this import.
from resource_methods import bcolors, Work, Dou, Headh, Rabota


# DB connection
try:
    db_connection_settings = {'user': os.environ['RDS_USERNAME'],
                              'password': os.environ['RDS_PASSWORD'],
                              'host': os.environ['RDS_HOSTNAME'],
                              'port': os.environ['RDS_PORT'],
                              "database": os.environ['RDS_DB_NAME']
                              }
    connection = psycopg2.connect(**db_connection_settings)
    cur = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    print(bcolors.OKGREEN+"DB CONNECTED"+ bcolors.ENDC)
except (Exception, psycopg2.Error) as error:
    print(bcolors.FAIL+"Error while connecting to PostgreSQL" + bcolors.ENDC +"\n"+ error)
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
    print("localhost:port" + url + ";  session_id" + session_id)
    #  todo avoid opening unwanted extra 'data' window
    driver = webdriver.Remote(command_executor=url, desired_capabilities={})
    driver.session_id = session_id
    driver.get('https://www.google.com/')
    print('continued on previous session')
    # todo Define custom exception MaxRetryError
except Exception as e:
    print(e)
    try:
        print("Trying to start new session")
        # todo make Chrome dynamic by get getattr
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        print()
        driver = webdriver.Chrome(executable_path=browser_connection_settings['new_session'], options=chrome_options)
        print(bcolors.OKGREEN+"New Chrome session started" + bcolors.ENDC)
        url = driver.command_executor._url
        session_id = driver.session_id
        update_config_query = 'UPDATE configs SET value = %(url)s WHERE param = \'url\';' \
                              'UPDATE configs SET value = %(session_id)s WHERE param = \'session_id\';'
        substitution = {"url" : url,"session_id":  session_id}
        cur.execute(update_config_query,substitution)
        connection.commit()
        #todo auto-update current session
        print('Web driver info:\nurl(port): {} , session_id: {}'.format(driver.command_executor._url, driver.session_id))
    except Exception as e:
        print(e)
        print(bcolors.FAIL + "Chrome driver failed to start" + bcolors.ENDC)
        exit(1)


#testing establishing connection
# exit()

def main(interval):
    # Telegram connection for notifications
    # telegram = TelegramConnection(driver)
    # print(telegram.connect())
    # print("Telegram connected successfully")

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
                    print(host_features[row['host']]['class'])
                    source = globals()[host_features[row['host']]['class']](driver, row['url'], row['target'], user['user_id'])
                    print(row['host'],row['target'], len(source.vacancies))
                    for vacancy in source.vacancies:
                        results = vacancy.insert_to_db(cur)
                        checked += results[0]
                        inserted += results[1]
                        # if vacancy is new
                        if results[1] and not user['is_new']:
                            print('notification about {}'.format(vacancy.title))
                            vacancy.send_notification(user_telegram_id, cur)
                    connection.commit()
                    #todo print time

                if user['is_new']:
                    set_not_new = 'UPDATE "users" SET "is_new" = false WHERE "user_id" = {};'.format(user['user_id'])
                    cur.execute(set_not_new)
                    connection.commit()
                # todo print Ukrainan time
                print(datetime.datetime.now())
                print("user_name", user['user_name'],"; checked ",checked, "; inserted ",inserted)
        # break
        # todo print next iteration time
        print('waiting...')
        time.sleep(60*15)
    # cur.close()
    # connection.close()



if __name__ == "__main__":
    main(10)