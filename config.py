import os
browser_connection_settings ={
    'new_session': os.path.dirname(os.path.realpath(__file__)) + '/' + 'chromedriver',
    'existing_session':{'url' :'http://127.0.0.1:58009',
    'session_id' : 'd28a31196e5f99b0453a8af7e45beb0b'}
}

db_connection_settings = {'user': os.environ['JP_DB_USERNAME'],
                       'password':os.environ['JP_DB_PASSWORD'],
                       'host':os.environ['JP_DB_HOST'],
                       'port':os.environ['JP_DB_PORT'],
                       "database":os.environ['JP_DB_DBNAME']
                          }

# todo explain dictionary
host_features = {'jobs.dou.ua':{'class': 'Dou', 'more': 'Больше вакансий', 'block': '.vacancy', 'link': '.vt', 'company': '.company'},
                   'hh.ua':{'class': 'Headh','more':'//a[contains(text(),\'дальше\')]','block':'.vacancy-serp-item', 'link':'.HH-LinkModifier','company': '.bloko-link_secondary'},
                 'rabota.ua':{'class': 'Rabota','more':'//a[contains(text(),\'Следующая\')]','block':'.f-vacancylist-vacancyblock', 'link':'.f-visited-enable.ga_listing','company': '.f-text-dark-bluegray.f-visited-enable'},
                 'work.ua':{'class': 'Work','more':'.pagination li:last-child a','block':'.job-link', 'link':'h2 a','company': 'h2 + span'}
                 }