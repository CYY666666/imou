import time
import uuid
from hashlib import md5

def get_sign(content):
    return str(md5(content.encode('utf-8')).hexdigest())

def get_request_data(app_id, app_secret):
    t = int(time.time())
    nonce = str(uuid.uuid4())
    content = 'time:%s,nonce:%s,appSecret:%s' % (t, nonce, app_secret)
    data = {
        "system": {
            "ver": "1.0",
            "appId": app_id,
            "sign": get_sign(content),
            "time": t,
            "nonce": nonce
        },
        "id": str(uuid.uuid4())
    }
    return data
