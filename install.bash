#!/bin/sh

if [ -z "$1" ]
then
    echo "Correct usage: ./install.sh <watchdog_settings_id>"
    exit 1
fi

pwdesc=$(echo $PWD | sed 's_/_\\/_g')
watchdog_module=$pwdesc
python_exec=$pwdesc\\/venv\\/bin\\/python


touch ./watchdog.service
cat ./watchdog.service.template > ./watchdog.service
sed -i -e "s/{module}/$watchdog_module/g" ./watchdog.service
sed -i -e "s/{python}/$python_exec/g" ./watchdog.service
sed -i -e "s/{id}/$1/g" ./watchdog.service
sed -i -e "s/{AWS_REGION}/$(echo $AWS_REGION | sed 's_/_\\/_g')/g" ./watchdog.service
sed -i -e "s/{AWS_ACCOUNT_ID}/$(echo $AWS_ACCOUNT_ID | sed 's_/_\\/_g')/g" ./watchdog.service
sed -i -e "s/{AWS_ACCESS_KEY_ID}/$(echo $AWS_ACCESS_KEY_ID | sed 's_/_\\/_g')/g" ./watchdog.service
sed -i -e "s/{AWS_SECRET_ACCESS_KEY}/$(echo $AWS_SECRET_ACCESS_KEY | sed 's_/_\\/_g')/g" ./watchdog.service
sed -i -e "s/{AWS_WATCHDOG_TABLE}/$(echo $AWS_WATCHDOG_TABLE | sed 's_/_\\/_g')/g" ./watchdog.service
sed -i -e "s/{AWS_WATCHDOG_SNS_TOPIC}/$(echo $AWS_WATCHDOG_SNS_TOPIC | sed 's_/_\\/_g')/g" ./watchdog.service

cp ./watchdog.service /etc/systemd/system/watchdog.service