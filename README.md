# A3C (Ark Cluster Companion container)
A companion container for ich777's ark-ae server container that has three functions:

Creates daily backups of server ark data. 

Provides a simple http service that the servers can use to address dynamicconfig.ini by using python module http.server

Keeps the server files and mods up to date.

It does this by finding all of the .mod files in the folder and checking their modified time against [this steam api](https://steamapi.xpaw.me/#ISteamRemoteStorage/GetPublishedFileDetails) and comparing the version.txt to http://arkdedicated.com/version.

If a mod or server has a newer version externally, the designated Ark servers will be warned that updated mods are going to trigger a restart.  The primary server on the cluster will be used to update the mods, and then the other servers will be started again once the first is working.

This has been built for personal use on a cluster for friends.  No promises of support if things do not work, but feel free to make PRs or use anything you find here for yourself.

# Configuration

### Auto Managed Mods
This container assumes that the first server in the list for RCON ports and image name is the one setup with `-automanagedmods` included in the ExtraParameters the rest should not .

Using the [ich777/steamcmd](https://hub.docker.com/r/ich777/steamcmd) server container on Unraid, adding these volume mapping will fix up the built in ark-se automodmanager:
* /serverdata/serverfiles/Engine/Binaries/ThirdParty/SteamCMD/Linux <> /mnt/user/appdata/steamcmd
* /serverdata/Steam/steamapps <> /mnt/cache/appdata/steamcmd/steamapps
* /serverdata/serverfiles/Engine/Binaries/ThirdParty/SteamCMD/Linux/steamapps <> /mnt/cache/appdata/steamcmd/steamapps

### RCON
Additionally, any RCON must be setup correctly which means you need these parameters in your startup command line: `?RCONPort=<SomePort>?RCONEnabled=True?ServerAdminPassword=<YourServerAdminPassword>`.  The server password must be here and not just in your GameUserSettings.ini for RCON to work.

### Volumes
This container uses the following container mounts:
* /serverdata/serverfiles <> /mnt/cache/appdata/ark-se
  * This is the same base directory that ich777's container uses for the base game server files. This is where the container will check if mods or server files
* /var/run/docker.sock <> /var/run/docker.sock
   * This provides the docker socket api to start/stop/get containers
* /serverdata/serverfiles/dynamicconfig/backup <> /mnt/user/backup
   * This is where the backups of the ARKdata folders are put, I made a share on the array and mounted it there so that is the cache drive goes poof there will be something to salvage.

> **The observent will notice an extra Volume mapping in the XML templates to ich777's ark:se container, those allow each instance of server in the cluster to maintain its own "Saved" directory so that each server can be configured independantly as the ShooterGameServer loves to write back to its config files seemingly randomly. This prevents instances from writing over echother as well as makes it easier to restore if nessicary. 

### Variables
The following environment variables are also needed:
* MCRCON_HOST=\<ServerHostIP> or list of hosts
   * This can either be a single host (likely your server IP), or a list of csv of hosts that match with the RCON ports and container names
* MCRCON_PASS=\<YourServerAdminPassword>
* RCON_PORTS= csv list of ports for all servers in the cluster (or single server)
   * for example my cluster of 10 maps this is `27025,27026,27027,27028,27029,27030,27031,27032,27033,27034`
   * This is the list of ports to notify that the server is shutting down when a mod update is detected
* CONTAINER_NAMES= csv list of docker containers names for the servers
   * for example my cluster of 10 maps this is `ARK1-TheIsland,ARK2-ScorchedEarth_P,ARK3-Aberration_P,ARK4-TheCenter,ARK5-Ragnarok,ARK6-Valguero_P,ARK7-CrystalIsles,ARK8-Extinction,ARK9-Genesis,ARK10-DangerIsland`
   * The first server in this list will be restarted (so mods can be updated), and all other servers will be stopped and then started once the first is back online (checked via RCON command)
* BACKUP_DAYS= 10
   * The number of days wou with to keep backups of the "Saved" folder of the servers in the cluster

> **It is important that RCON_PORTS, MCRCON_HOST, and CONTAINER_NAMES have the same number of servers and are in the same order.  eg the first host, port, and container name line up, and the second of each line up, etc.**

> **GameModIds can be listed in the GUS.ini under [ServerSettings] (ActiveMods=ModID1,ModID2,ect) or included on the command line by entering them in the "Game Parameters" as "?GameModIds=ModID1,ModID2" ether way the server(container) responcible for updateing the mods must include all mods wanted in the cluster, others may use any subset or all of the mods downloaded my the first server, but they must be told which mods to use ether in the GUS.ini or on the comand line. 

# Container
The container image is available on dockerhub as: `cydfsa/companion:arkse`

# Unraid
Example XML flis in git repository, customise to your preferances and you should have an ARK:SE cluster hammered together in no time.

Good Luck and Happy hunting!