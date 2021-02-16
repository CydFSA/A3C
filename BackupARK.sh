#!/bin/bash
DATE=$(date +%d-%m-%Y)
BACKUP_DIR="/serverdata/backup"
BACKUP_DAYS=`cat /serverdata/serverfiles/dynamicconfig/BackupDays.txt`
#To create a new directory in the backup directory location
mkdir -p $BACKUP_DIR/$DATE

for ark in `cat /serverdata/serverfiles/dynamicconfig/ARK-list.txt`
do
tar -zcpf $BACKUP_DIR/$DATE/$DATE-$ark.tar.gz /serverdata/serverfiles/$ark 2>/dev/null
done

#To delete files older than 10 days
find $BACKUP_DIR/* -mtime "+$BACKUP_DAYS" -exec rm {} \;
#prune empty directoies
find $BACKUP_DIR/ -type d -exec rmdir {} > /dev/null 2&>1 \;
