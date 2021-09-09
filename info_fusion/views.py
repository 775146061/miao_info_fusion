from django.shortcuts import render

# Create your views here.

from info_fusion.scheduler import scheduler
from info_fusion.constants import provinceMap
import requests
import logging
import json

log = logging.getLogger('log')

# @scheduler.scheduled_job('cron', id='hold_session', name='hold_session', minute='*/1')
def info_fusion_job():
    headers = {
        'Host': 'cloud.cn2030.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx2c7f0f3c30d99445/73/page-frame.html',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,compress,br,deflate'
    }
    proxyUseCount = 1
    proxies = None
    def get_proxy():
        resOfProxy = requests.get('http://106.52.164.139:90/get/?type=https')
        proxy = json.loads(resOfProxy.content)
        proxies = {'https': proxy['proxy']}
    get_proxy()
    for key in provinceMap:
        url = f'https://cloud.cn2030.com/sc/wx/HandlerSubscribe.ashx?act=CustomerList&city=["{key}","",""]&id=0&cityCode={provinceMap[key]}&product=0'
        log.info(f'url: {url}')
        if proxyUseCount > 10:
            get_proxy()
            proxyUseCount = 1

        res = requests.get(url, headers=headers, proxies=proxies)
        log.info(f'状态码: {res.status_code}')
        log.info(f'proxyUseCount: {proxyUseCount}')
        proxyUseCount = proxyUseCount + 1