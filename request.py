import json

import aiohttp
import asyncio

import async_timeout

from .errors import InvalidAuth, GetListFailed
from .utils import get_request_data
from .const import accessToken, deviceBaseList, modifyDeviceAlarmStatus, controlMovePTZ, setDeviceSnapEnhanced, \
    setDeviceCameraStatus


class Request:
    def __init__(self):
        self.app_id = None
        self.app_secret = None
        self.base_url = 'https://openapi.lechange.cn/openapi/'
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession()

        self.token = None
        self.device_list = []

    async def _post(self, method, params):
        data = get_request_data(self.app_id, self.app_secret)
        data.update(params)
        async with self.session.post(self.base_url + method, json=data) as res:
            text = await res.text()
            json_data = json.loads(text)
            ok = json_data.get('result').get('code') == '0'
            msg = json_data.get('result').get('msg')
            res_data = json_data.get('result').get('data')
            return res_data, msg, ok

    async def accessToken(self):
        data, msg, ok = await self._post(accessToken, {'params': {}})
        if not ok:
            raise InvalidAuth(msg)
        self.token = data.get('accessToken')

    async def deviceBaseList(self):
        params = {
            'token': self.token,
            'bindId': 1,
            'limit': 128,
            'type': 'bind',
            'needApInfo': False
        }
        data, msg, ok = await self._post(deviceBaseList, {'params': params})
        if not ok:
            raise GetListFailed(msg)
        self.device_list = data.get('deviceList')
        return self.device_list

    async def modifyDeviceAlarmStatus(self, device_id, channel_id, enable):
        params = {
            'token': self.token,
            'deviceId': device_id,
            'channelId': channel_id,
            'enable': enable
        }
        data, msg, ok = await self._post(modifyDeviceAlarmStatus, {'params': params})

    async def closeCamera(self, device_id, channel_id, enable):
        params = {
            'token': self.token,
            'deviceId': device_id,
            'channelId': channel_id,
            'enableType': 'closeCamera',
            'enable': enable
        }
        data, msg, ok = await self._post(setDeviceCameraStatus, {'params': params})

    async def controlMovePTZ(self, device_id, channel_id, operation, duration=300):
        params = {
            'token': self.token,
            'deviceId': device_id,
            'channelId': channel_id,
            'operation': operation,
            'duration': duration
        }
        data, msg, ok = await self._post(controlMovePTZ, {'params': params})

    async def setDeviceSnapEnhanced(self, device_id, channel_id):
        params = {
            'token': self.token,
            'deviceId': device_id,
            'channelId': channel_id
        }
        data, msg, ok = await self._post(setDeviceSnapEnhanced, {'params': params})
        return data, msg, ok

    async def get_bytes(self, url: str) -> bytes:
        """Get information from the API. This will return the raw response and not process it"""
        response = None
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return await response.read()
        finally:
            if response is not None:
                response.close()

request = Request()
