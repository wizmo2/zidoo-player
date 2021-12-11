""" Config Flow for ZidoMedia Players. """
import requests.exceptions
import voluptuous as vol

from .zidoorc import ZidooRC

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.components import ssdp
from urllib.parse import urlparse

from .const import (
    _LOGGER,
    DOMAIN,
    CLIENTID_PREFIX,
    CLIENTID_NICKNAME,
    CONF_SHORTCUT,
)

SUPPORTED_MANUFACTURERS = ["Zidoo", "ZIDOO", "Plutinosoft LLCL"]
IGNORED_MODELS = []

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PASSWORD): str
    }
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    try:
        player = ZidooRC(data[CONF_HOST])
        response = await hass.async_add_executor_job(
            player.connect, CLIENTID_PREFIX, CLIENTID_NICKNAME
        )
    except requests.exceptions.ConnectionError:
        raise CannotConnect
    except RuntimeError:
        raise UnknownError

    if response is not None:
        unique_id = str(f"{DOMAIN}-{response.get('net_mac')}")
        name = response.get("model")

        return {"title": name, "unique_id": unique_id}

    raise CannotConnect


@config_entries.HANDLERS.register(DOMAIN)
class ZidooFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    ZidooFlowHandler configuration method.

    The schema version of the entries that it creates
    Home Assistant will call your migrate method if the version changes
    (this is not implemented yet)
    """

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the zidoo flow."""
        self.discovery_schema = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return flow options."""
        return ZidooOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None, confirm=False):
        """
        Manage device specific parameters.
        """
        errors = {}
        if user_input is not None:
            try:
                validated = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "auth_failure"
            except CannotConnect:
                errors["base"] = "timeout_error"
            except UnknownError:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                await self.async_set_unique_id(validated["unique_id"])
                self._abort_if_unique_id_configured()

                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.discovery_schema or DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, user_input):
        """Handle import."""
        return await self.async_step_user(user_input)

    async def async_step_ssdp(self, discovery_info):
        """Handle a discovered Harmony device."""
        _LOGGER.debug("SSDP discovery_info: %s", discovery_info)

        parsed_url = urlparse(discovery_info[ssdp.ATTR_SSDP_LOCATION])
        friendly_name = discovery_info[ssdp.ATTR_UPNP_FRIENDLY_NAME]

        self._async_abort_entries_match({CONF_HOST: parsed_url.hostname})

        self.context["title_placeholders"] = {"name": friendly_name}

        user_input = {
            CONF_HOST: parsed_url.hostname,
            CONF_NAME: friendly_name,
        }

        _LOGGER.debug("SSDP discovery_info: %s", user_input)

        errors = {}
        if user_input is not None:
            try:
                validated = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "auth_failure"
            except CannotConnect:
                errors["base"] = "timeout_error"
            except UnknownError:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                await self.async_set_unique_id(validated["unique_id"])
                self._abort_if_unique_id_configured()

                self._set_confirm_only()
                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

            return self.async_step_link(user_input)

    async def async_step_link( self, user_input: None):
        """Allow the user to confirm adding the device."""
        if user_input is not None:
            return await self.async_step_connect()

        self._set_confirm_only()
        return self.async_show_form(
            step_id="link",
            description_placeholders={
                CONF_HOST: user_input[CONF_NAME],
                CONF_NAME: user_input[CONF_HOST],
                CONF_PASS: None,
            },
        )
        return self.async_show_form(step_id="confirm")

class ZidooOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SHORTCUT,
                    default=self.config_entry.options.get(CONF_SHORTCUT),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
