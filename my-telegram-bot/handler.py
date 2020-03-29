import sys
import json
import os
import re
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='line:%(lineno)d %(levelname)s - %(message)s')
logger = logging.getLogger(' Telegram bot')

# here = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(here + '/packages')

# import requests
import psycopg2, psycopg2.extras
from urllib.parse import urlparse
# parsed_link = urlparse('https://rabota.ua/zapros/office-manager/киев')
# logger.info(parsed_link)

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message


def Find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
db_connection_settings = {'user': os.environ['JP_DB_USERNAME'],
                       'password':os.environ['JP_DB_PASSWORD'],
                       'host':os.environ['JP_DB_HOST'],
                       'port':os.environ['JP_DB_PORT'],
                       "database":os.environ['JP_DB_DBNAME']
                          }
try:
    BOT = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
except Exception as e:
    logger.info("Bad telegram Token", e)


def hello(event, context):

    # connection = psycopg2.connect(**db_connection_settings)
    # cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # get_users_query = 'SELECT * FROM users;'
    # cur.execute(get_users_query)
    # users=cur.fetchall()
    # logger.info(users)
    # logger.info(users[1]['user_name'])

    #todo save all messages somewhere



    try:
        # CONNECTING TO DATABASE --- START
        try:
            connection = psycopg2.connect(**db_connection_settings)
            connection.autocommit = True
            cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception as e:
            # send_data = {"text": "База Данных временно не доступна. Сори.", "chat_id": chat_id}
            raise Exception("Could not connect to the database")
        # CONNECTING TO DATABASE --- END

        received_data = json.loads(event["body"])
        logger.debug(received_data)
        print(received_data)
        # REPLACE
        # received_data={'update_id': 143930183, 'message': {'message_id': 19164, 'from': {'id': 777990555, 'is_bot': False, 'first_name': 'MAKSYM', 'last_name': 'O', 'username': 'magzim21', 'language_code': 'en'}, 'chat': {'id': 777990555, 'first_name': 'MAKSYM', 'last_name': 'O', 'username': 'magzim21', 'type': 'private'}, 'date': 1585496529, 'text': 'https://kiev.hh.ua/search/vacancy?area=115&st=searchVacancy&text=devops', 'entities': [{'offset': 0, 'length': 71, 'type': 'url'}]}}
        # received_data structure differs depending on whether it was message or button click. "message" or "callback_query"
        # breakpoint()
        if "message" in received_data:
            logger.info("message")
            chat_id = received_data["message"]["chat"]["id"]
            first_name = received_data["message"]["chat"]["first_name"]
            user_name = received_data['message']['chat']['username']

            original_message = received_data["message"]["text"]
            # original_message = 'https://www.work.ua/asdf/sf?df=df'  # REPALCE

            logger.info(original_message)
            if "/start" in original_message:
                response = "{}, Выбери, !" \
                           "Это чат бот по поиску работы" \
                           "".format(first_name)
                keyboard = [[InlineKeyboardButton("Добавить ссылку", callback_data='/add_link'),
                             InlineKeyboardButton("Удалить ссылку", callback_data='/del_link')],
                            [InlineKeyboardButton("Про этот бот", callback_data='/about')],
                            [InlineKeyboardButton("Приостановить", callback_data='/suspend')]
                            ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                send_data = {"text": response, "chat_id": chat_id, 'reply_markup': reply_markup}
            elif Find(original_message):
                parsed_link = urlparse(original_message)
                logger.info(parsed_link)
                host = parsed_link.netloc
                logger.info(host)
                host = host.replace('www.','')
                host = host[host.find('hh.ua'):] # replacing kiev/kharkiv.hh.ua subdomain
                if host != 'work.ua' and host != 'jobs.dou.ua' and 'hh.ua' not in host  and host != 'rabota.ua':
                    send_data = {"text": "Ссылка не распознана", "chat_id": chat_id}
                    # raise Exception(host + ' - such host does not exist - error')
                else:

                    #  ---  THIS WiLL GET USER's id FROM DATABASE --- START
                    try:
                        insert_user_query = f'INSERT INTO USERS ("user_name", "telegram_id", "active", "is_new")  VALUES (\'{user_name}\',\'{chat_id}\',FALSE, TRUE );'
                        cur.execute(insert_user_query)
                    except Exception as e:
                        logger.info('User already exists')
                    finally:
                        get_user_query = f'SELECT * FROM USERS WHERE "telegram_id" = \'{chat_id}\' ;'
                        cur.execute(get_user_query)
                        user_id = cur.fetchall()[0]['user_id']
                    #  ---  THIS WiLL GET USER's id FROM DATABASE --- END
                    insert_url_query = f'INSERT INTO URLS ("url", "host", "target", "user_id") VALUES (\'{original_message}\', \'{host}\', \'empty100line\', \'{user_id}\');' # sql injection threat here
                    try:
                        cur.execute(insert_url_query)
                        send_data = {"text": "Я буду присылать самые свежие вакансии из этой ссылки.", "chat_id": chat_id}
                    except Exception as e:
                        print(e)
                        send_data = {"text": "Такая ссылка уже добавлена",
                                     "chat_id": chat_id}
                    # connection.commit()

            else:
                response = "Привет, {}, я мгновенно уведомляею о новых вакансиях. Достаточно дать ссылку где их искть. \n Нажми /start, чтобы начать.".format(first_name)
                send_data = {"text": response, "chat_id": chat_id}
                
        # PROCESSING BUTTONS  --- START
        elif "callback_query" in received_data:
            logger.info("callback_query")
            chat_id = received_data["callback_query"]["from"]["id"]
            first_name = received_data["callback_query"]["from"]["first_name"]
            callback_query_data = received_data["callback_query"]["data"]
            logger.info(callback_query_data)
            if callback_query_data.startswith("/add_link"):
                keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                             InlineKeyboardButton("Option 2", callback_data='2')],
                            [InlineKeyboardButton("Option 3", callback_data='3')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                send_data = {"text": 'Пришлите ссылку сообщением.\nПоддерживаемые сайты: hh.ua, jobs.dou.ua, work.ua, rabota.ua', "chat_id": chat_id}
                BOT.send_photo(chat_id=chat_id, photo=open('images/img1_help.png', 'rb'))
            # DELETE LINK FROM DATABASE --- START
            elif callback_query_data.startswith("/del_link"):
                if callback_query_data.startswith("/del_link/del/"):
                    link_del = callback_query_data.replace('/del_link/del/','')
                    print(link_del)
                    query_del_link = f'DELETE FROM URLS WHERE "url_id" = \'{link_del}\';'
                    cur.execute(query_del_link)
                    if cur.rowcount == 1:
                        send_data = {"text": "Ссылка удалена.", "chat_id": chat_id}
                    else:
                        send_data = {"text": "Ссылка не удалена тк не найдена.", "chat_id": chat_id}
                else:
                    print(f'trying to get links list (delete) for chat_id  {chat_id}')
                    get_user_urls = f'SELECT * FROM URLS WHERE "user_id" = (SELECT "user_id" FROM USERS WHERE "telegram_id"= \'{chat_id}\');'
                    print(get_user_urls)
                    keyboard = []
                    cur.execute(get_user_urls)
                    urls = cur.fetchall()
                    for url in urls:
                        keyboard.append([InlineKeyboardButton(url["url"], callback_data=f'/del_link/del/{url["url_id"]}')])
                    if keyboard:
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        send_data = {"text": "Выберите какую ссылку удалить", "chat_id": chat_id, 'reply_markup': reply_markup}
                    else:
                        send_data = {"text": "Похоже, вы не добавляли ссылки ранее", "chat_id": chat_id}
            # DELETE LINK FROM DATABASE --- END

            elif callback_query_data.startswith("/about"):
                send_data = {"text": "Это чудо!", "chat_id": chat_id}
            else:
                send_data = {"text": "unknown option", "chat_id": chat_id}
        else:
            raise Exception('UNKNOWN MESSAGE ERROR')
        # PROCESSING BUTTONS  --- END




    except Exception as e:
        # breakpoint()
        logger.error(e)
    else:
        try:
            BOT.send_message(**send_data)
        except Exception as e:
            logger.error('check for ERRORS')
            logger.error(e)
    finally:
        # is good decision?
        return {"statusCode": 200}

test_event = {'resource': '/my-custom-url', 'path': '/my-custom-url', 'httpMethod': 'POST', 'headers': {'Accept-Encoding': 'gzip, deflate', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-Country': 'GB', 'Content-Type': 'application/json', 'Host': 'qx2vlrfg80.execute-api.eu-central-1.amazonaws.com', 'Via': '1.1 c334b6410f9d489eb2a951a4371f3d18.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'X-bjEs0LU_BRwBRYPetts2DFl4jWfPXvqHgNuJx0fx19r1qmOo_o8Q==', 'X-Amzn-Trace-Id': 'Root=1-5e5650dc-a8205a38d93513a0dfab298d', 'X-Forwarded-For': '91.108.6.82, 70.132.46.168', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept-Encoding': ['gzip, deflate'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['GB'], 'Content-Type': ['application/json'], 'Host': ['qx2vlrfg80.execute-api.eu-central-1.amazonaws.com'], 'Via': ['1.1 c334b6410f9d489eb2a951a4371f3d18.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['X-bjEs0LU_BRwBRYPetts2DFl4jWfPXvqHgNuJx0fx19r1qmOo_o8Q=='], 'X-Amzn-Trace-Id': ['Root=1-5e5650dc-a8205a38d93513a0dfab298d'], 'X-Forwarded-For': ['91.108.6.82, 70.132.46.168'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'zvygzq', 'resourcePath': '/my-custom-url', 'httpMethod': 'POST', 'extendedRequestId': 'IgGSiEb2liAFeHg=', 'requestTime': '26/Feb/2020:11:05:00 +0000', 'path': '/dev/my-custom-url', 'accountId': '249446252531', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': 'qx2vlrfg80', 'requestTimeEpoch': 1582715100974, 'requestId': '8eab1ab6-d5f2-499e-86fe-0b519630a90b', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '91.108.6.82', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': None, 'user': None}, 'domainName': 'qx2vlrfg80.execute-api.eu-central-1.amazonaws.com', 'apiId': 'qx2vlrfg80'}, 'body': '{"update_id":222389959,\n"callback_query":{"id":"3341443992397849721","from":{"id":777990555,"is_bot":false,"first_name":"MAKSYM","last_name":"O","username":"magzim21","language_code":"en"},"message":{"message_id":1157,"from":{"id":902397373,"is_bot":true,"first_name":"jp_dev","username":"jp_dev_bot"},"chat":{"id":777990555,"first_name":"MAKSYM","last_name":"O","username":"magzim21","type":"private"},"date":1582714915,"text":"Please /start, MAKSYM","entities":[{"offset":7,"length":6,"type":"bot_command"}],"reply_markup":{"inline_keyboard":[[{"text":"Option 1","callback_data":"1"},{"text":"Option 2","callback_data":"2"}],[{"text":"Option 3","callback_data":"3"}]]}},"chat_instance":"5193848306760861775","data":"3"}}', 'isBase64Encoded': False}
test_context = None
# breakpoint()
# hello(test_event, test_context) # REPLACE



# url = BASE_URL + "/sendMessage"
# requests.post(url, data)


# def router(func):
#     def wrapper(locator):
#         if data.startswith(locator):
#             func()
#     return wrapper
#
# @router('/add_resource/')
# def fu():
#     pass

# if '/add_resource/' in data:
#     if '/add_resource/dfsf' in data:
#         if ...