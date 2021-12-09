## Fixing HACS download problems

An issue with the HACS configuration file was introduced in release versions 1.2.4 and below, which prevents versions from down loading correctly.

v1.2.5 fixes the issue, but if a previous version has been installed, then the following procuedure is required to add and remove the HACS install

### Remove any exisitng HA integrations

1. Goto Configuration/Integrations and remove any installed media player devices

a. For each Zidoo Media Player, Press the Menu icon and select Delete

### Remove and Re-Download the HACS Integration

2. Goto HACS/Integrations

a. Press the Menu icon in the Zidoo Media Player integration, and select Remove

b. Press the EXPLORE & DOWLOAD REPOSITORIES button

c. Search for Zidoo and select Zidoo Media Player

d. Press DOWNLOAD REPOSITORY WITH HACS

e.  Select the latest version and press Download

3. Goto Configuration/Server Controls and restart HA

a. Restart HA Server

### Add Media Player Devices

4.  Goto Configuration/Integrations

a.  Press the ADD INTEGRATION button

b.  Seach for Zidoo and select Zido Media Player

d.  Enter the IP address and Password


