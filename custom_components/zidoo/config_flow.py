""" Config Flow for ZidoMedia Players. """
import requests.exceptions
import voluptuous as vol

from .zidooaio import ZidooRC

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_MAC
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    _LOGGER,
    DOMAIN,
    CONF_POWERMODE,
    CONF_SHORTCUT,
    ZSHORTCUTS,
    ZDEFAULT_SHORTCUTS,
)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_HOST): str, vol.Optional(CONF_PASSWORD): str}
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    try:
        player = ZidooRC(data[CONF_HOST])
        response = await player.connect()
        await player.disconnect()
    except requests.exceptions.ConnectionError:
        raise CannotConnect
    except RuntimeError:
        raise UnknownError

    if response is not None:
        mac_id = response.get("net_mac")
        name = response.get("model")

        return {"title": name, "mac": mac_id}

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

    async def async_step_user(self, user_input=None):
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
                unique_id = str(f"{DOMAIN}-{validated['mac']}")
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                user_input[CONF_MAC] = validated["mac"]
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
        _LOGGER.debug("Import user_info: %s", user_input)
        return await self.async_step_user(user_input)


class ZidooOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.shortcut_list: dict[str, str] = {
            item["path"]: item["name"] for item in ZSHORTCUTS
        }

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        shortcuts = [
            item
            for item in self.config_entry.options.get(CONF_SHORTCUT, ZDEFAULT_SHORTCUTS)
            if item in self.shortcut_list
        ]

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD, "")
                ): str,
                vol.Optional(CONF_SHORTCUT, default=shortcuts): cv.multi_select(
                    self.shortcut_list
                ),
                vol.Optional(
                    CONF_POWERMODE,
                    default=self.config_entry.options.get(CONF_POWERMODE, False),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
