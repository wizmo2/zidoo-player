# Zidoo Power On

## Wake-on-Lan
The Zidoo-Player integration supports power on natively when the device supports it.  The Home-Assistant server sends a magic packet to the device using it's mac address.  

If this does not work then.

- Verify sure your device supports WOL.  Note:  Earier zidoo devices such as the Z9S are not supported.
- WOL only works over the LAN connection. WOL over Wifi is not supported.
- Magic UDP packets are not routed outside your local area network.  The Home-Assistant Server and the Device must be on the same sub-net
- If you have Home-Assistant installed in a docker, you either need to configure the container with the '--net=host' argument, or have some type of WOL gateway setup to forward the packets from inside the container ([see this post](https://community.home-assistant.io/t/wake-on-lan-for-those-running-home-assistant-in-docker/189376/)).


## IR Blaster
If you have a IR Blaster or Broadlink, you can power on the Zidoo by sending the correct code using a script.

```
zidoo_turn_on:
  icon: mdi:radio-tower   
  sequence:
  - condition: state
    entity_id: media_player.zidoo
    state: 'off'
  - service: remote.send_command
    data:
      entity_id: remote.rm3mini_remote
      command: b64:JgB4AAABI5MTEhMSEhITEhMSExITNhMSExITERMSExITEhMSEjcTEhM2ExITNxM2ExITEhM2ExITEhM3EhITEhM2FDYTEhM2EwAGCAABJksTAAxWAAEoSRMADFYAASdJEwAMVgABKEgTAAxaAAEkSRMADFYAASdJEwANBQ==
```

This can be integrated into the media player controls using an automation (when working with devices, it's easier to use the automation editor to get the right device_id)

```
alias: media_zidoo_turn_on
trigger:
  - platform: device
    device_id: <device_id>
    domain: zidoo
    entity_id: media_player.zidoo
    type: turn_on
action:
  - service: script.zidoo_turn_on
mode: single
```

## HDMI-CES

Some device combinations support power on through the HDMI connection.  Check you TV/Reciever manual for specific details.
