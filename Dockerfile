FROM ubuntu:20.04

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3.8 \
    python-is-python3 \
    python3-pip \
    cron \
    nano
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
WORKDIR /

ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

# add the steam user and set up the crontab for backing up the arks
RUN useradd -u 99 -g 100 -d /serverdata -s /bin/bash steam
ADD steam.crontab /steam.crontab

# Add script and grant execution rights
ADD script.py /opt/scripts/script.py
ADD start.sh /opt/scripts/start.sh
ADD BackupARK.sh /opt/scripts/BackupARK.sh
ADD steam.crontab /opt/scripts/steam.crontab
ADD dynamicconfig.ini /opt/scripts/dynamicconfig.ini
# compiled on 2/13/2021 from https://github.com/Tiiffi/mcrcon.git
ADD mcrcon /usr/local/bin/mcrcon
RUN chmod +x /opt/scripts/script.py /opt/scripts/start.sh /opt/scripts/BackupARK.sh /usr/local/bin/mcrcon

# Run the command on container startup
CMD ["/opt/scripts/start.sh"]
