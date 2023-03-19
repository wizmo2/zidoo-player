"""Zidoo trigger dispatcher."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.components.automation import (
    AutomationActionType,
    AutomationTriggerInfo,
)
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, Event, HassJob, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, EVENT_TURN_ON

TRIGGER_TYPES = {"turn_on"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device triggers for Zidoo devices."""
    registry = entity_registry.async_get(hass)
    triggers = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain == "media_player":
            triggers.append(
                {
                    CONF_PLATFORM: "device",
                    CONF_DEVICE_ID: device_id,
                    CONF_DOMAIN: DOMAIN,
                    CONF_ENTITY_ID: entry.entity_id,
                    CONF_TYPE: "turn_on",
                }
            )

    return triggers


@callback
def _attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    event_type,
    automation_info: AutomationTriggerInfo,
):
    trigger_data = automation_info["trigger_data"]
    job = HassJob(action)

    @callback
    def _handle_event(event: Event):
        if event.data[ATTR_ENTITY_ID] == config[CONF_ENTITY_ID]:
            hass.async_run_hass_job(
                job,
                {"trigger": {**trigger_data, **config, "description": event_type}},
                event.context,
            )

    return hass.bus.async_listen(event_type, _handle_event)


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: AutomationTriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    if config[CONF_TYPE] == "turn_on":
        return _attach_trigger(hass, config, action, EVENT_TURN_ON, automation_info)

    return lambda: None
