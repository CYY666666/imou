"""Constants for the imou integration."""

DOMAIN = "imou"

accessToken = 'accessToken'
deviceBaseList = 'deviceBaseList'
modifyDeviceAlarmStatus = 'modifyDeviceAlarmStatus'
setDeviceCameraStatus = 'setDeviceCameraStatus'
controlMovePTZ = 'controlMovePTZ'
getKitToken = 'getKitToken'
setDeviceSnapEnhanced = 'setDeviceSnapEnhanced'

SERVICE_CLOSE_CAMERA = 'enable_close_camera'
SERVICE_ALARM_STATUS = 'enable_alarm_status'


CAMERA_ICON = 'mdi:camera'


class Operation:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    LEFT_UP = 4
    LEFT_DOWN = 5
    RIGHT_UP = 6
    RIGHT_DOWN = 7
    ENLARGE = 8
    ZOOM_OUT = 9
    STOP = 10
