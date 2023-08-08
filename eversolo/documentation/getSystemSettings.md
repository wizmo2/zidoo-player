http://<ip>:9529/SystemSettings/getSystemSettings
```json
{
  "status": 200,
  "settings": [
    {
      "title": "Audio",
      "items": [
        {
          "title": "XLR/RCA output",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_xlr_xxxhdpi.png",
          "option": 3,
          "tag": "SettingsItemTagXLROutput",
          "url": "/SystemSettings/audioSettings/getXlrOutputOption",
          "selectTitle": ""
        },
        {
          "title": "HDMI output",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_hdmi_xxxhdpi.png",
          "option": 3,
          "tag": "SettingsItemTagHDMIOutput",
          "url": "/SystemSettings/audioSettings/getHDMIOutputOption",
          "selectTitle": ""
        },
        {
          "title": "SPDIF output",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_coaxial_xxxhdpi.png",
          "option": 3,
          "tag": "SettingsItemTagSpdifOutput",
          "url": "/SystemSettings/audioSettings/getSpdifOutputOption",
          "selectTitle": ""
        },
        {
          "title": "USB DAC output",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_usbdac_xxxhdpi.png",
          "option": 3,
          "tag": "SettingsItemTagUsbDacOutput",
          "url": "/SystemSettings/audioSettings/getUsbDacOutputOption",
          "selectTitle": ""
        },
        {
          "title": "Fixed sampling rate output",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_caiyanglv_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemTagSamplerateOutput",
          "url": "/SystemSettings/audioSettings/getSamplerateOutputList",
          "selectTitle": "Original sampling rate",
          "itemDescription": "Effective when outputting PCM2.0"
        },
        {
          "title": "Analog volume limit",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_analog_xxxhdpi.png",
          "option": 6,
          "tag": "SettingsItemTagAlongVolumeLimit",
          "url": "/SystemSettings/audioSettings/setAlongVolumeLimit?index=",
          "selectTitle": "0 dB",
          "currentValue": 80,
          "maxValue": 80,
          "minValue": 0
        },
        {
          "title": "Digital volume limit",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_digital_xxxhdpi.png",
          "option": 6,
          "tag": "SettingsItemTagDegiteVolumeLimit",
          "url": "/SystemSettings/audioSettings/setDegiteVolumeLimit?index=",
          "selectTitle": "15",
          "currentValue": 15,
          "maxValue": 15,
          "minValue": 5
        },
        {
          "title": "Volume passthrough mode",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_volume_xxxhdpi.png",
          "option": 0,
          "tag": "SettingsItemTagVolumePassthrough",
          "isSwitchOpenHint": true,
          "contentTips": "The maximum output volume of the system cannot be adjusted.Do not turn it on, if the backend device does not support volume adjustment, when XLR/RCA analog output.\nAre you sure to turn on?",
          "url": "/SystemSettings/audioSettings/setVolumePassthrough?switch=",
          "switchStatus": true,
          "itemDescription": "The maximum output volume of the system cannot be adjusted"
        },
        {
          "title": "Eversolo Original sampling-rate audio engine",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_audio_icon_eos_xxxhdpi.png",
          "option": 0,
          "tag": "SettingsItemTagEOSEngine",
          "isShowTips": true,
          "contentTips": "Eversolo Original Sampling-Rate Audio Engine, also known as the EOS engine, is the underlying audio engine independently created by Eversolo. It enables the global original sampling rate of the system, Direct output, floating-point data from third-party applications; The DSD and PCM audio VU processing and local music files gapless play. A seamless and high-fidelity music experience is supported. Please try to disable this engine if you encounter individual third-party application sound anomalies.",
          "url": "/SystemSettings/audioSettings/setEOSEngine?switch=",
          "switchStatus": true,
          "isLastList": true,
          "itemDescription": "System global raw sample rate output"
        }
      ]
    },
    {
      "title": "Display",
      "items": [
        {
          "title": "Screen brightness",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_pmld_xxxhdpi.png",
          "option": 6,
          "tag": "SettingsItemTagScreenBrightness",
          "url": "/SystemSettings/displaySettings/setScreenBrightness?index=",
          "selectTitle": "100%",
          "currentValue": 115,
          "maxValue": 115,
          "minValue": 0
        },
        {
          "title": "Knob brightness",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_xnld_xxxhdpi.png",
          "option": 6,
          "tag": "SettingsItemTagKnobBrightness",
          "url": "/SystemSettings/displaySettings/setKnobBrightness?index=",
          "selectTitle": "15%",
          "currentValue": 40,
          "maxValue": 255,
          "minValue": 0
        },
        {
          "title": "Screensaver",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_pb_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemTagScreensaver",
          "url": "/SystemSettings/displaySettings/getScreensaverList",
          "selectTitle": "2 hours",
          "itemDescription": ""
        },
        {
          "title": "Screensaver mode",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_pmms_xxxhdpi.png",
          "option": 5,
          "tag": "SettingsItemTagScreenMode",
          "url": "/SystemSettings/displaySettings/getScreenModeList",
          "selectTitle": "Classic Clock",
          "itemDescription": ""
        },
        {
          "title": "VU meter",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_vu_xxxhdpi.png",
          "option": 5,
          "tag": "SettingsItemTagVUMode",
          "url": "/SystemSettings/displaySettings/getVUModeList",
          "selectTitle": "VU meter 1",
          "isLastList": true,
          "itemDescription": ""
        },
        {
          "title": "Theme mode",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_layout_xxxhdpi.png",
          "option": 5,
          "tag": "SettingsItemTagPlayMode",
          "url": "/SystemSettings/displaySettings/getPlayModeList",
          "selectTitle": "Theme 2",
          "isLastList": true,
          "itemDescription": ""
        },
        {
          "title": "Display playback details background image",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_screen_icon_bg_xxxhdpi.png",
          "option": 0,
          "tag": "SettingsItemTagShowPlayBg",
          "isSwitchOpenHint": false,
          "contentTips": "",
          "url": "/SystemSettings/displaySettings/setShowPlayBg?switch=",
          "switchStatus": true,
          "itemDescription": ""
        }
      ]
    },
    {
      "title": "General",
      "items": [
        {
          "title": "Language",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_language_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemTagLanguage",
          "url": "/SystemSettings/geneicSettings/getLanguageList",
          "selectTitle": "English (United States)",
          "itemDescription": ""
        },
        {
          "title": "Input method",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_srf_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemTagKeyboard",
          "url": "/SystemSettings/geneicSettings/getKeyboardList",
          "selectTitle": "Android Keyboard (AOSP)",
          "itemDescription": ""
        },
        {
          "title": "USB-OTG port",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_usbotg_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemTagUsbotg",
          "url": "/SystemSettings/geneicSettings/getUsbotgList",
          "selectTitle": "External storage device",
          "itemDescription": ""
        },
        {
          "title": "Power Mode",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_dyms_xxxhdpi.png",
          "option": 1,
          "tag": "SettingsItemPowerMode",
          "url": "/SystemSettings/geneicSettings/getPowerModeList",
          "selectTitle": "Standby after power plug in",
          "itemDescription": ""
        },
        {
          "title": "Factory reset",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_hfcc_xxxhdpi.png",
          "option": 4,
          "tag": "SettingsItemTagResetFactory",
          "url": "/SystemSettings/geneicSettings/factoryReset",
          "selectTitle": ""
        },
        {
          "title": "About",
          "icon": "/SystemSettings/getItemSettingIcon?iconName=setting_tongyong_icon_about_xxxhdpi.png",
          "option": 4,
          "tag": "SettingsItemTagAbout",
          "url": "/ControlCenter/getModel",
          "selectTitle": "",
          "isLastList": true
        }
      ]
    }
  ]
}
```