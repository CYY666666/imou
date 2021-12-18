"""
Illuminator for for Dahua cameras that have white light illuminators.

See https://developers.home-assistant.io/docs/core/entity/light
"""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.components.camera import Camera, SUPPORT_STREAM
from homeassistant.helpers import entity_platform

from .request import Request, request
from .const import DOMAIN, CAMERA_ICON, SERVICE_CLOSE_CAMERA, SERVICE_ALARM_STATUS


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Setup light platform."""
    app_id = entry.data['app_id']
    app_secret = entry.data['app_secret']
    if not request.app_id:
        request.app_id = app_id
        request.app_secret = app_secret
    if not request.token:
        await request.accessToken()

    entities = []
    entities.append(ImouCamera(
        request,
        entry.data.get('channels')[0].get('channelName'),
        entry.data.get('channels')[0].get('channelId'),
        entry.data.get('deviceId')
    ))
    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_CLOSE_CAMERA,
        {
            vol.Required("enable"): bool,
        },
        'async_camera_status'
    )

    platform.async_register_entity_service(
        SERVICE_ALARM_STATUS,
        {
            vol.Required("enable"): bool,
        },
        'async_alarm_status'
    )


class ImouCamera(Camera):

    def __init__(self, request: Request, channel_name, channel_id, device_id):
        Camera.__init__(self)
        self.request = request
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.device_id = device_id

    @property
    def name(self):
        """Return the name of the light."""
        return self.channel_name

    @property
    def unique_id(self):
        """
        A unique identifier for this entity. Needs to be unique within a platform (ie light.hue). Should not be configurable by the user or be changeable
        see https://developers.home-assistant.io/docs/entity_registry_index/#unique-id-requirements
        """
        return '%s_%s' % (self.device_id, self.channel_id)

    @property
    def icon(self):
        return CAMERA_ICON

    async def async_camera_status(self, enable):
        await self.request.closeCamera(self.device_id, self.channel_id, enable)

    async def async_alarm_status(self, enable):
        await self.request.modifyDeviceAlarmStatus(self.device_id, self.channel_id, enable)

    async def async_move(self, direction):
        await self.request.controlMovePTZ(self.device_id, self.channel_id, direction)
    async def async_camera_image(self, width: int | None = None, height: int | None = None):
        """Return a still image response from the camera."""
        # Send the request to snap a picture and return raw jpg data
        data, msg, ok = await self.request.setDeviceSnapEnhanced(self.device_id, self.channel_id)
        if ok:
            url = data.get('url')
            return await self.request.get_bytes(url)

    @property
    def supported_features(self):
        """Return supported features."""
        return SUPPORT_STREAM

    async def stream_source(self):
        """Return the RTSP stream source."""
        return self._stream_source

    @property
    def motion_detection_enabled(self):
        """Camera Motion Detection Status."""
        return False

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        channel = self._coordinator.get_channel()
        await self._coordinator.client.enable_motion_detection(channel, True)
        await self._coordinator.async_refresh()

    async def async_disable_motion_detection(self):
        """Disable motion detection."""
        channel = self._coordinator.get_channel()
        await self._coordinator.client.enable_motion_detection(channel, False)
        await self._coordinator.async_refresh()

    async def async_set_infrared_mode(self, mode: str, brightness: int):
        """ Handles the service call from SERVICE_SET_INFRARED_MODE to set infrared mode and brightness """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_lighting_v1_mode(channel, mode, brightness)
        await self._coordinator.async_refresh()

    async def async_set_video_in_day_night_mode(self, config_type: str, mode: str):
        """ Handles the service call from SERVICE_SET_DAY_NIGHT_MODE to set the day/night color mode """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_video_in_day_night_mode(channel, config_type, mode)
        await self._coordinator.async_refresh()

    async def async_set_record_mode(self, mode: str):
        """ Handles the service call from SERVICE_SET_RECORD_MODE to set the record mode """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_record_mode(channel, mode)
        await self._coordinator.async_refresh()

    async def async_set_video_profile_mode(self, mode: str):
        """ Handles the service call from SERVICE_SET_VIDEO_PROFILE_MODE to set profile mode to day/night """
        channel = self._coordinator.get_channel()
        model = self._coordinator.get_model()
        # Some NVRs like the Lorex DHI-NVR4108HS-8P-4KS2 change the day/night mode through a switch
        if 'NVR4108HS' in model:
            await self._coordinator.client.async_set_night_switch_mode(channel, mode)
        else:
            await self._coordinator.client.async_set_video_profile_mode(channel, mode)

    async def async_set_enable_channel_title(self, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_CHANNEL_TITLE """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_enable_channel_title(channel, enabled)

    async def async_set_enable_time_overlay(self, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_TIME_OVERLAY  """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_enable_time_overlay(channel, enabled)

    async def async_set_enable_text_overlay(self, group: int, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_TEXT_OVERLAY """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_enable_text_overlay(channel, group, enabled)

    async def async_set_enable_custom_overlay(self, group: int, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_CUSTOM_OVERLAY """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_enable_custom_overlay(channel, group, enabled)

    async def async_set_enable_all_ivs_rules(self, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_ALL_IVS_RULES """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_all_ivs_rules(channel, enabled)

    async def async_enable_ivs_rule(self, index: int, enabled: bool):
        """ Handles the service call from SERVICE_ENABLE_IVS_RULE """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_ivs_rule(channel, index, enabled)

    async def async_vto_open_door(self, door_id: int):
        """ Handles the service call from SERVICE_VTO_OPEN_DOOR """
        await self._coordinator.client.async_access_control_open_door(door_id)

    async def async_set_service_set_channel_title(self, text1: str, text2: str):
        """ Handles the service call from SERVICE_SET_CHANNEL_TITLE to set profile mode to day/night """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_service_set_channel_title(channel, text1, text2)

    async def async_set_service_set_text_overlay(self, group: int, text1: str, text2: str, text3: str,
                                                 text4: str):
        """ Handles the service call from SERVICE_SET_TEXT_OVERLAY to set profile mode to day/night """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_service_set_text_overlay(channel, group, text1, text2, text3, text4)

    async def async_set_service_set_custom_overlay(self, group: int, text1: str, text2: str):
        """ Handles the service call from SERVICE_SET_CUSTOM_OVERLAY to set profile mode to day/night """
        channel = self._coordinator.get_channel()
        await self._coordinator.client.async_set_service_set_custom_overlay(channel, group, text1, text2)
