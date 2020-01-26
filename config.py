# existing_session SLASH / is important
browser_connection_settings ={
    'new_session': './chromedriver',
    'existing_session':{'url' :'http://127.0.0.1:58009',
    'session_id' : 'd28a31196e5f99b0453a8af7e45beb0b'}
}
# TODO WHAAT IS THE ISSUE WITH IMPORTS
db_connection_settings = {'user': "postgres",
                       'password':"",
                       'host':"127.0.0.1",
                       'port':"5432",
                       "database":"db_for_py"
                          }
# todo add telegram users to database
telegram_settings =  {'token':'1026909428:AAGc5DDjJoMh2uM43V5gO6TbFfayPy4rHUg',
                      }

telegram_connection = {
    'phone_number' : '0661440698',
    'country' :'Ukraine',
    'chat_to_send_msgs' : 'saved messages',
    'texting_delay' : 1
}

# todo explain dictionary
host_features = {'jobs.dou.ua':{'class': 'Dou', 'more': 'Больше вакансий', 'block': '.vacancy', 'link': '.vt', 'company': '.company'},
                   'hh.ua':{'class': 'Headh','more':'//a[contains(text(),\'дальше\')]','block':'.vacancy-serp-item', 'link':'.HH-LinkModifier','company': '.bloko-link_secondary'},
                 'rabota.ua':{'class': 'Rabota','more':'//a[contains(text(),\'Следующая\')]','block':'.f-vacancylist-vacancyblock', 'link':'.f-visited-enable.ga_listing','company': '.f-text-dark-bluegray.f-visited-enable'},
                 'work.ua':{'class': 'Work','more':'.pagination li:last-child a','block':'.job-link', 'link':'h2 a','company': 'h2 + span'}
                 }