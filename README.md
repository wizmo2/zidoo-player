# Home-assistant component for Zidoo media players
HA media-player and api wrapper.

This is a functioning solution for controlling my Z9S Zidoo media player on Home-Assistant.  Based on the Zidoo rest api, it should work on other devices (feedback/PRs welcome)

ZidooRC will eventually need to be released as a python library per HA requirements.  

Includes Media Browse support with favorites (although the latter is work-in-progress - currently hard-coded into media_player)

Dev is tested up to HA version 2021.10 and uses cover-flow.   
Release 1.1 is tested from HA versions 2021.1 up to 2021.10, and requires manual integration.


## Installation
1. Copy zidoo folder to \config\custom_components (create folder if this is yuor first custom integration)
2. Restart HA

for latest version:

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





