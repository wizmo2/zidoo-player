## Services

### Search

The Search Media service can be used in conjunction with the SEARCH shortcut to display filtered results in the Media Browser based on a keyword.

Use the query_string field to set the keywork seach for the entity.  Use the Media SEARCH shortcut to display the results.

NOTE:  With a combination of helpers and scripts, it is possible to automate this function using the current lovalace versions, but this is essentially a development project for when a search function is incoperated into the Media Browser standard functions.  
- Use a Text Input and automation to set the keyword seach using the  Search Media service.
- Use a button control or Browser-Mod custom component to navigate to /media-browser/<media_player>/video%2Csearch.

In HA version 2022 and above, the url http://<ip_address>:>port>/media-browser/media_player.zidoo_z9s/video%2Csearch=<keyword> can be used to display results of the search directly.

