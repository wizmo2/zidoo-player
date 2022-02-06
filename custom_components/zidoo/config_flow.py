""" Config Flow for ZidoMedia Players. """
import requests.exceptions
import voluptuous as vol

from .zidoorc import ZidooRC

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_UNIQUE_ID
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.components import ssdp
from urllib.parse import urlparse

from .const import (
    _LOGGER,
    DOMAIN,
    CLIENTID_PREFIX,
    CLIENTID_NICKNAME,
    CONF_SHORTCUT,
    ZSHORTCUTS,
    ZDEFAULT_SHORTCUTS,
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
        self.discovery_config = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return flow options."""
        return ZidooOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None, confirm=False):
        """
        Manage device specific parameters.
        """
        # _LOGGER.debug("User user_info: %s", user_input)
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
                _LOGGER.debug("User Create user_info: %s", user_input)
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PASSWORD): str
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input):
        """Handle import."""
        _LOGGER.debug("Import user_info: %s", user_input)
        return await self.async_step_user(user_input)

    async def async_step_ssdp(self, discovery_info):
        """Handle a discovered Harmony device."""
        #_LOGGER.debug("SSDP discovery_info: %s", discovery_info)

        parsed_url = urlparse(discovery_info.ssdp_location)
        friendly_name = discovery_info.upnp[ssdp.ATTR_UPNP_FRIENDLY_NAME]

        self._async_abort_entries_match({CONF_HOST: parsed_url.hostname})

        self.context["title_placeholders"] = {"name": friendly_name}

        self.discovery_config = {
            CONF_HOST: parsed_url.hostname,
            CONF_NAME: friendly_name,
            CONF_PASSWORD: None,
        }
        _LOGGER.debug("SSDP config: %s", self.discovery_config)

        # verify we can connect
        errors = {}
        try:
            validated = await validate_input(self.hass, self.discovery_config)
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

            # self.discovery_config[CONF_NAME] = validated["title"]
            return await self.async_step_link()

    async def async_step_link( self, user_input=None):
        """Allow the user to confirm adding the device."""
        #_LOGGER.debug("Link user_info: %s", user_input)
        if user_input is not None:
            # Add name and host to config
            user_input[CONF_NAME] = self.discovery_config[CONF_NAME]
            user_input[CONF_HOST] = self.discovery_config[CONF_HOST]
            _LOGGER.debug("Link Create config: %s", user_input)
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=user_input
            )

        self._set_confirm_only()

        return self.async_show_form(
            step_id="link",
            description_placeholders={
                CONF_HOST: self.discovery_config[CONF_HOST],
                CONF_NAME: self.discovery_config[CONF_NAME],
            },
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PASSWORD): str
                }
            ),
        )


class ZidooOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.shortcut_list: dict[str, str] = {item["path"]: item["name"] for item in ZSHORTCUTS}

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        shortcuts = [item for item in self.config_entry.options.get(CONF_SHORTCUT, ZDEFAULT_SHORTCUTS) if item in self.shortcut_list]

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD,"")): str,
                vol.Optional(
                    CONF_SHORTCUT, default=shortcuts
                ): cv.multi_select(self.shortcut_list)
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""

class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
