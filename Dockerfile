# Base image
FROM joyzoursky/python-chromedriver:3.6-xvfb-selenium

WORKDIR  /usr/workspace
# Installing dependencies
RUN  pip install beautifulsoup4 psycopg2 python-telegram-bot 
# Downloading linux Chrome Driver
RUN wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip && unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip


ARG buildtime_variable=default_value
ARG buildtime_variable=default_value
ARG buildtime_variable=default_value
ARG buildtime_variable=default_value
ARG buildtime_variable=default_value


# Setting environment vars
ARG JP_DB_USERNAME=HIDDEN
ARG JP_DB_PASSWORD=HIDDEN
ARG JP_DB_HOST=HIDDEN
ARG JP_DB_PORT=HIDDEN
ARG JP_DB_DBNAME=HIDDEN
ARG TELEGRAM_TOKEN=HIDDEN

ENV JP_DB_USERNAME=$JP_DB_USERNAME
ENV JP_DB_PASSWORD=$JP_DB_PASSWORD
ENV JP_DB_HOST=$JP_DB_HOST
ENV JP_DB_PORT=$JP_DB_PORT
ENV JP_DB_DBNAME=$JP_DB_DBNAME
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN


# Set time
ENV TZ Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Exposing any port (Elastic Beanstalk requirement)
EXPOSE 1111 1111

COPY . . 
CMD ["/usr/local/bin/python", "./version2.py"] 





