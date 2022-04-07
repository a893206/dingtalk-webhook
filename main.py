import base64
import datetime
import hashlib
import hmac
import logging
import time
import urllib.parse
from configparser import ConfigParser

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from chinese_calendar import is_workday


def get_timestamp_and_sign(section: str):
    # https://open.dingtalk.com/document/robots/customize-robot-security-settings
    timestamp = str(round(time.time() * 1000))
    secret = cp.get(section, 'secret')
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def drink_water():
    if is_workday(datetime.date.today()):
        section = drink_water.__name__
        timestamp, sign = get_timestamp_and_sign(section)
        requests.post(
            cp.get(section, 'webhook') + '&timestamp={}&sign={}'.format(timestamp, sign), json={
                "msgtype": "markdown",
                "markdown": {
                    "title": "喝水时间到！",
                    "text": "#### 喝水时间到！\n > ![笑对万事](https://raw.githubusercontent.com/a893206/dingtalk-webhook/main/img/love&peace.jpg)"
                },
            })


if __name__ == '__main__':
    cp = ConfigParser()
    cp.read('config.setting')

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler = BlockingScheduler()
    scheduler.add_job(drink_water, CronTrigger.from_crontab(cp.get('scheduler', 'crontab')))
    scheduler.start()
