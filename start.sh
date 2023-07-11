#! /usr/bin/bash
FILE=/serverdata/serverfiles/dynamicconfig/dynamicconfig.ini
if [ ! -f $FILE ];then
cp /opt/scripts/dynamicconfig.ini /serverdata/serverfiles/dynamicconfig/dynamicconfig.ini
fi
FILE=/serverdata/serverfiles/dynamicconfig/steam.crontab
if [ ! -f $FILE ];then
cp /opt/scripts/steam.crontab /serverdata/serverfiles/dynamicconfig/steam.crontab
fi
echo -n > /serverdata/serverfiles/dynamicconfig/ARK-list.txt
IFS=',' read -ra ADDR <<< "$CONTAINER_NAMES"
for i in "${ADDR[@]}"; do
        echo $i >> /serverdata/serverfiles/dynamicconfig/ARK-list.txt
done
echo  "dynamicconfig" >> /serverdata/serverfiles/dynamicconfig/ARK-list.txt
FILE=/serverdata/serverfiles/dynamicconfig/BackupARK.sh
if [ ! -f $FILE ];then
cp /opt/scripts/BackupARK.sh /serverdata/serverfiles/dynamicconfig/BackupARK.sh
fi

echo $BACKUP_DAYS > /serverdata/serverfiles/dynamicconfig/BackupDays.txt


chown steam:users /serverdata/serverfiles/dynamicconfig
chown steam:users /serverdata/serverfiles/dynamicconfig/dynamicconfig.ini
chown steam:users /serverdata/serverfiles/dynamicconfig/steam.crontab
chown steam:users /serverdata/serverfiles/dynamicconfig/ARK-list.txt
chown steam:users /serverdata/serverfiles/dynamicconfig/BackupARK.sh
chown steam:users /serverdata/serverfiles/dynamicconfig/BackupDays.txt

if [[ $BACKUP_DAYS -eq 0 ]]
	then
		echo "backups disabled"
	else
		crontab -u steam /serverdata/serverfiles/dynamicconfig/steam.crontab
		cron
fi

python -m http.server -d /serverdata/serverfiles/dynamicconfig 80 &

python -u /opt/scripts/script.py
