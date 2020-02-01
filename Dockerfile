# Base image
FROM joyzoursky/python-chromedriver:3.6-xvfb-selenium

# Change timezone 
RUN  timedatectl set-timezone Europe/Kiev
# Installing dependencies
RUN  pip install beautifulsoup4 psycopg2 python-telegram-bot 
# Downloading linux Chrome Driver
RUN wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip && unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip

WORKDIR  /usr/workspace
# DataBase connection environment vars
ENV  JP_DB_USERNAME=$JP_DB_USERNAME JP_DB_PASSWORD=$JP_DB_PASSWORD JP_DB_HOST=$JP_DB_HOST JP_DB_PORT=$JP_DB_PORT JP_DB_DBNAME=$JP_DB_DBNAME
# Telegram token connection environment var
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
LABEL project=job_parser
# EXPOSE 5432 5432
COPY . . 
CMD ["/usr/bin/python3", "./version2.py"] 





