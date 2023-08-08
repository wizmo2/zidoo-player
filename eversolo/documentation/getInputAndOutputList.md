http://<ip>:9529/ZidooMusicControl/v2/getInputAndOutputList
```json
{
  "status": 200,
  "inputData": [
    {
      "name": "Internal player",
      "tag": "XMOS",
      "index": 0,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=XMOS.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=XMOS_select.png"
    },
    {
      "name": "Bluetooth In",
      "tag": "BT",
      "index": 1,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=BT.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=BT_select.png"
    },
    {
      "name": "USB-C In",
      "tag": "USB",
      "index": 2,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=USB.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=USB_select.png"
    },
    {
      "name": "Optical In",
      "tag": "SPDIF",
      "index": 3,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=SPDIF.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=SPDIF_select.png"
    },
    {
      "name": "Coaxial In",
      "tag": "RCA",
      "index": 4,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=RCA.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=RCA_select.png"
    }
  ],
  "inputIndex": 0,
  "outputData": [
    {
      "name": "BAL-XLR",
      "tag": "XLR",
      "enable": true,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_XLR.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_XLR_select.png"
    },
    {
      "name": "Analog-RCA",
      "tag": "RCA",
      "enable": true,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_RCA0.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_RCA0_select.png"
    },
    {
      "name": "XLR/RCA",
      "tag": "XLRRCA",
      "enable": true,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_XLR_RCA.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_XLR_RCA_select.png"
    },
    {
      "name": "HDMI",
      "tag": "HDMI",
      "enable": true,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_HDMI.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_HDMI_select.png"
    },
    {
      "name": "SPDIF",
      "tag": "SPDIF",
      "enable": true,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_SPDIF.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_SPDIF_select.png"
    },
    {
      "name": "USB DAC",
      "tag": "USB",
      "enable": false,
      "icon": "/SystemSettings/getItemSettingIcon?iconName=out_USB.png",
      "selecticon": "/SystemSettings/getItemSettingIcon?iconName=out_USB_select.png"
    }
  ],
  "outputInfo": {
    "vidPid": "",
    "name": "",
    "format": "PCM 32bit,MQA,DSD512",
    "sampleRate": "768000 Hz",
    "isConnect": true,
    "setUrl": "/SystemSettings/audioSettings/getXlrOutputOption",
    "title": "XLR/RCA output"
  },
  "outputIndex": 1
}
```