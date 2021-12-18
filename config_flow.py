"""Config flow for imou integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .request import request
from .errors import CannotConnect, InvalidAuth
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("app_id", default=''): str,
        vol.Required("app_secret", default=''): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, app_id: str, app_secret: str) -> None:
        """Initialize."""
        self.app_id = app_id
        self.app_secret = app_secret

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = PlaceholderHub(data["app_id"], data["app_secret"])

    if not await hub.authenticate():
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for imou."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self.hass.data.setdefault(DOMAIN, {})
        self.hass.data[DOMAIN].setdefault('devices', [])
        self.hass.data[DOMAIN].setdefault('secret', {})
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        request.app_id = user_input.get('app_id')
        request.app_secret = user_input.get('app_secret')
        try:
            await request.accessToken()
            self.hass.data[DOMAIN]['devices'] = await request.deviceBaseList()
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return await self.async_step_list()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_list(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        device_list = {}
        for device in request.device_list:
            device_list[device.get('deviceId')] = device.get('channels')[0].get('channelName')
        STEP_LIST_DATA_SCHEMA = vol.Schema(
            {
                vol.Required("devices", default=[]): cv.multi_select(device_list)
            }
        )
        if user_input is None:
            return self.async_show_form(
                step_id="list", data_schema=STEP_LIST_DATA_SCHEMA
            )
        for device in user_input['devices']:
            for device_info in self.hass.data[DOMAIN]['devices']:
                if device == device_info['deviceId']:
                    device_info['app_id'] = request.app_id
                    device_info['app_secret'] = request.app_secret
                    await self.hass.async_add_job(self.hass.config_entries.flow.async_init(
                        DOMAIN, context={"source": "batch_add"}, data=device_info
                    ))
                    break
        return self.async_abort(reason="success")

    async def async_step_batch_add(self, info):
        return self.async_create_entry(title=info['channels'][0]['channelName'], data=info)
