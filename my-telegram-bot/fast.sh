#! /bin/bash

zip -r9 ./function.zip ./handler.py
zip -ur ./function.zip ./images/*
cd ./packages
zip -ur ../function.zip *
cd ../

aws lambda update-function-code --function-name  my-telegram-bot-dev-hello   --zip-file fileb://function.zip
#aws lambda create-alias   --function-name my-telegram-bot-dev-hello --name alias-name --function-version $1  --description " "
#echo "SUCCESS"


# BETTER EXAMPLE
# $ aws lambda create-alias   --function-name my-function --name alias-name --function-version version-number  --description " "
