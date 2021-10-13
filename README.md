# Custom home-assistant component for Zidoo media players
HA media-player and api wrapper.

NOTE: This is a dirty functioning solution for controlling my Zidoo media player on Home assistant.  Tested on a Z9S (as its the only one I got!)

ZidooRC will eventually need to be released as a python library per HA requirements.  Version 1.1 now has Media Browse support with favorites

Dev is tested up to 2021.10 and uses cover-flow step. 
Release 1.1 is tested from 2021.1 up to 2021.10, and requires manual integration (Cover-flow in the works)


## Installation
1. Copy zidoo folder to \config\custom_components (create folder if this is yuor first custom integration)
2. Restart HA
for version 1.2:
3. Add Zidoo Integration using IP address of player

for version 1.1:
3. Edit your /config/configuration.yaml with

```
media_player:
  - platform: zidoo
    name: Zidoo
    host: 192.168.1.11
```

4. Restart HA

If you have issues connecting with the device, it may be an authorization issue.  
> 1. Try opening the 'Control Center' app and retry. 
> 2. Try turning off validation using the button in the app.   





