## Fixing HACS download problems

An issue with the HACS configuration file was introduced in release versions 1.2.4 and below, which prevents Versions from downloading correctly.

v1.2.5 fixes the issue, but if a previous version had been installed the following procuedure is required to add and remove the HACS install.

_NOTE:  Older versions have been re-built and re-released with the correct HACS configuration file to prevent ongoing issues (using 'v' prefix to the tags)_

### Remove any exisitng HA integrations

1. Goto Configuration/Integrations and remove any installed media player devices

![Step1](images/ar_step1.png)

a. For each Zidoo Media Player, Press the Menu icon and select Delete

### Remove and Re-Download the HACS Integration

2. Goto HACS/Integrations

![Step2](images/ar_step3.png) ![Step3](images/ar_step5.png) ![Step4](images/ar_step6.png)

a. Press the Menu icon in the Zidoo Media Player integration, and select Remove

b. Press the EXPLORE & DOWLOAD REPOSITORIES button

c. Search for Zidoo and select Zidoo Media Player

d. Press DOWNLOAD REPOSITORY WITH HACS

e.  Select the latest version and press Download

3. Goto Configuration/Server Controls and restart HA

a. Restart HA Server

### Add Media Player Devices

4.  Goto Configuration/Integrations

![Step5](images/ar_step7.png) ![Step6](images/ar_step8.png) ![Step7](images/ar_step9.png)

a.  Press the ADD INTEGRATION button

b.  Seach for Zidoo and select Zidoo

d.  Enter the IP address and Password (if applicable)



