import os
import sys
import subprocess
import time
# https://docker-py.readthedocs.io/en/stable/containers.html#
import docker
import json
import requests
import re
from distutils.version import StrictVersion
from datetime import datetime

print("Ark Mod Update Detection Started")

os.chdir('/')

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

containersToRestart = os.getenv('CONTAINER_NAMES').split(',')
print(f'Containers to restart: {containersToRestart}')
ports = os.getenv('MCRCON_PORTS').split(',')
print(f'RCON ports: {ports}')

hosts = os.getenv('MCRCON_HOST').split(',')
print(f'RCON hosts: {hosts}')

__containers_that_were_runnning = []

def sendToArk(port, host, container_name, command):
    print(f'Sending command to ARK image "{container_name}" on {host}:{port}: {command}')
    result = ansi_escape.sub('', subprocess.run(f'mcrcon -H "{host}" -P {port} "{command}"', shell=True, capture_output=True, text=True).stdout)
    print(result)
    return result


def sendToAllServersAndWait(command, wait):
    for i in range(len(ports)):
        host = hosts[0]
        if (len(hosts) > 1):
            host = hosts[i]
        sendToArk(ports[i], host, containersToRestart[i], command)
    time.sleep(wait)


def restartIfRunning(name, client):
    try:
        container = client.containers.get(name)
        if (container.status == 'running'):
            print(f'Restarting container {name}')
            container.restart()
    except:
        e = str(sys.exc_info()[0])
        print(f'Failed to restart container {name} {e}')

def stopIfRunning(name, client):
    try:
        container = client.containers.get(name)
        if (container.status == 'running'):
            print(f'Stopping container {name}')
            __containers_that_were_runnning.append(name)
            container.stop()
    except:
        e = str(sys.exc_info()[0])
        print(f'Failed to stop container {name} {e}')

def start(name, client):
    try:
        container = client.containers.get(name)
        print(f'Starting container {name}')
        container.start()
    except:
        e = str(sys.exc_info()[0])
        print(f'Failed to start container {name} {e}')

def waitForServerActive(name, client):
    time.sleep(15) # make sure server is shutdown
    timeout = time.time() + 60*5   # 5 minutes from now
    container = client.containers.get(name)
    while True:
        if time.time() > timeout:
            print(f'Waiting for {name} to start failed, starting other servers normally')
            break
        if 'Server received, But no response!!' in sendToArk(ports[0], hosts[0], containersToRestart[0], "broadcast Checking if server is live."):
            print(f'Container {name} successfully started')
            break
        time.sleep(15)


# if a mod was updated
def restartTheContainers():
    # sendToAllServersAndWait("broadcast Mods updated, restarting server in 10 minutes.", 300)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 5 minutes.", 60)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 4 minutes.", 60)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 3 minutes.", 60)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 2 minutes.", 60)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 1 minute.", 30)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 30 seconds.", 15)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 15 seconds.", 10)
    sendToAllServersAndWait("broadcast Mods updated, restarting server in 5 seconds.", 5)
    sendToAllServersAndWait("broadcast Saving Server", 0)
    sendToAllServersAndWait("saveworld", 15)

    first, rest = containersToRestart[0], containersToRestart[1:]

    client = docker.from_env()
    restartIfRunning(first, client)
    # shut down all others
    for name in rest:
        stopIfRunning(name, client)
    if len(__containers_that_were_runnning) > 0:
        running = str(__containers_that_were_runnning)
        print(f'Stopped containers: {running}')

    # wait for first to be online
    waitForServerActive(first, client)

    # start what ones were running
    if len(__containers_that_were_runnning) > 0:
        running = str(__containers_that_were_runnning)
        print(f'Starting previously stopped containers: {running}')
    for name in __containers_that_were_runnning:
        start(name, client)

    __containers_that_were_runnning.clear()



def get_mod_info(mod_ids):
    if len(mod_ids) == 0:
        return None

    json_dict = {'itemcount': len(mod_ids)}
    x = 0
    for mod in mod_ids:
        json_dict['publishedfileids[' + str(x) + ']'] = mod
        x += 1

    # https://steamapi.xpaw.me/#ISteamRemoteStorage/GetPublishedFileDetails
    response = requests.post('https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/',
        data=json_dict)

    if response.status_code == 200:
        data = response.json()
        mod_info = data['response']['publishedfiledetails']
        return mod_info

    return None



def server_ver_check():
    with open('/serverdata/serverfiles/version.txt') as lfile:
        lversion = lfile.read().strip()
    with requests.get('http://arkdedicated.com/version') as rfile:
        rversion = rfile.text.strip()
    print("local version:",lversion,"arkdedicated version:",rversion)
    return StrictVersion(rversion) > StrictVersion(lversion)



while True:
    print("Update Checked At: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    try:
        # list .mod files in mod folder
        mod_files = [ f.name for f in os.scandir(r"/serverdata/serverfiles/ShooterGame/Content/Mods") if not f.is_dir() ]
        mods_updated = 0
        force_update = os.getenv('FORCE_UPDATE')
        if force_update == 'true':
            mods_updated += 1
            print('Update forced')

        if server_ver_check():
            mods_updated += 1
            print('Server revision change, queueing update')

        modIds = [x.replace('/serverdata/serverfiles/ShooterGame/Content/Mods/', '').replace('.mod', '') for x in mod_files]
        modIds.remove('111111111') # the default mod does not need to be queried and the result is missing info anyway

        print(f'Mod Ids to check: {modIds}')

        mods = get_mod_info(modIds)

        if mods is not None:
            for mod in mods:
                modId = mod['publishedfileid']
                modName = mod['title']
                updatedTime = os.path.getmtime(f'/serverdata/serverfiles/ShooterGame/Content/Mods/{modId}.mod')
                remoteUpdateTime = mod['time_updated']
                requires_update = updatedTime < remoteUpdateTime
                print(f'Mod "{modName}" ID {modId} updated locally {updatedTime} remote {remoteUpdateTime}.  Requires Update: {requires_update}')
                # determine if a mod updated and increment
                if requires_update:
                    mods_updated += 1

        print(f'{mods_updated} mods updated')
        if (mods_updated > 0):
            restartTheContainers()
    except:
        e = str(sys.exc_info()[0])
        print(f'Failed to check update {e}')

    time.sleep(300)