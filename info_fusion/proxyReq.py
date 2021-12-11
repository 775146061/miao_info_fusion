# 请求工具

import logging
from miao_info_fusion.exceptions import BusinessException
import requests
import json
from info_fusion.constants import USER_AGENT_COUNT, userAgents
import random

log = logging.getLogger('log')
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

TIMEOUT = 10 # 10秒超时时间

def try_proxy(proxy) -> bool:
    try:
        requests.get('https://www.baidu.com/', proxies=proxy, timeout=TIMEOUT)
        return True
    except Exception as e:
        log.info(f'代理: {proxy} 不可用!')
        return False

def get_proxy_ip():
    global proxies
    if proxyUseCount < 10 and proxies:
        return proxies

    while True:
        resOfProxy = requests.get('http://106.52.164.139:90/get/?type=https', timeout=TIMEOUT)
        proxy = json.loads(resOfProxy.content)
        p = proxy.get('proxy', None)
        if not p:
            raise(BusinessException('代理池没有代理ip了!'))
        proxies = {'https': f'https://{p}'}
        flag = try_proxy(proxies)
        if flag:
            break
        requests.get(f'http://106.52.164.139:90/delete?proxy={p}')

    return proxies

def requestGet(url: str, *args, **kargs):
    proxies = get_proxy_ip()
    headers['User-Agent'] = userAgents[random.randrange(0, USER_AGENT_COUNT)]
    log.info(f'请求url：{url}')
    log.info(f'请求代理：{proxies}')
    res = requests.get(url, *args, **kargs, proxies=proxies, headers=headers, timeout=TIMEOUT)
    return (res, proxies, headers['User-Agent'])
