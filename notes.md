# Application Notes
The following are application notes based on feedback from other users.

## Rapid Update
The integration uses `local polling` with the Zidoo REST API to access data.  The standard polling time within HA may result in slow updates of status.

The HA dev team have depreciated support of adjusting polling times within integrations.  The current recommended method is to create automations to activate the `homeassistant.update_entity' service.

For example:
```
alias: Zidoo Rapid Update
description: ''
trigger:
  - platform: time_pattern
    seconds: '*'
condition:
  - condition: state
    entity_id: media_player.zidoo
    state: playing
action:
  - service: homeassistant.update_entity
    data: {}
    target:
      entity_id: media_player.zidoo
mode: single
```

_NOTE: You can disable the default polling from within the Integration settings._

## Using Additional Attributes (dev)
In addition to the native media player attributes, support for extra attributes is availble in the `main` beta release when the zidoo video or audio player is playing.

The list as of 4/23 includes
- "media_uri" - the file reference,
- "media_height" - the source video height
- "media_width" - the source video height
- "media_zoom" - the current player zoom mode,
- "media_tag" - the movie tag-line from the HT db
- "media_date" - the movie release date from th HT db
- "media_bitrate" - the video reported bitrate
- "media_fps" - the video reported frames per second
- "media_audio" - the source audio format
- "media_video" - the source video format

### Getting aspect ratio
An example of using a template sensor to return the aspect-ratio

```
template:
  - sensor:
      - unique_id: zidoo_aspect_ratio
        name: Zidoo Aspect Ratio
        state: >
          {% set width = state_attr('media_player.zidoo', 'media_width')|float(0) %}
          {% set height = state_attr('media_player.zidoo', 'media_height')|float(1) %}
          {% set ratio = (width / height)|round(2) %}
          {% if ratio >= 2.35 %}
            2.35:1
          {% elif ratio >= 1.9 %}
            1.90:1
          {% elif ratio >= 1.77 %}
            16:9
          {% else -%}
            4:3
          {% endif %}
'''
You can customize the state to acheive the desired result based on your requirements. NOTE: 'media_zoom' may also be needed
