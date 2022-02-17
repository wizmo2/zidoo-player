## Development

### Search

The Search Media service can be used in conjunction with the SEARCH shortcut to display filtered results in the Media Browser based on a keyword.

* Set the query_string keyword search string for a Zidoo-Player entity using a Service call.
* Navigate to the Media Browser SEARCH shortcut to display the results. (enable the SEARCH shortcut in the Integration configuration card to access). 

The url `http://<ip_address>:<port>/media-browser/media_player.zidoo_z9s/video,*<keyword>` can be used to display results of the search directly.

NOTE:  this is essentially a development project for when a search function is incoperated into the Media Browser standard functions although it is possible to use the current lovalace version with a combination of helpers, scripts, and button control actions (or [browser-mod navigate](https://github.com/thomasloven/hass-browser_mod)). 

Lovelace card example:
```
type: entities
entities:
  - entity: input_text.zidoo_search
    tap_action:
      action: navigate
      navigation_path: /media-browser/media_player.zidoo_z9s/video%2C*
```
Automation example:
```
- id: set_zidoo_search
  alias: set_zidoo_search
  trigger:
  - platform: state
    entity_id: input_text.zidoo_search
  condition: []
  action:
  - service: zidoo.search
    data:
      query_string: '{{ states(''input_text.zidoo_search'') }}'
    target:
      entity_id: media_player.zidoo_z9s
  mode: single
```


