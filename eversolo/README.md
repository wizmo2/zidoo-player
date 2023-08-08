# Eversolo branch

The Eversolo DMR-A6 is a Hifi audio oriented player based on zidoo technology.

This branch will attempt to encompass the DMR into the Zidoo integration to support HA media player and media browsing.

## API Support
Initially, it looks like the majority of the Zidoo API has been migrated, although there are some variances around limitations with the origional (v1) commands.  

Please bare in mind that I do not have access to one of these units so am relying on assitance on development and code testing.

Thanks to: @MichaelSGreen,

## Streaming
The Eversolo is using 'airable' as the API engine for all stream services.  From what I can tell this an official rebrand of TuneIn.  They have a tight grip on the technolgy, so dont expect any support for thier hosted services.

It does look like it support upnp, so hopefully, the existing code for playing media can be made to work.