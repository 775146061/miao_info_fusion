from info_fusion.utils import date_auto_completion
from typing import Text
from info_fusion.models import MiaoModel
from django.shortcuts import render
from urllib import parse

# Create your views here.

from info_fusion.scheduler import scheduler
from info_fusion.constants import provinceMap
import logging
import json
import random
import time
from .proxyReq import requestGet
from multiprocessing import Queue

log = logging.getLogger('log')

JIUJIA = 1 # 1 九价
SIJIA = 2  # 2 四价

PLATFORM_ZHIMIAO = 1 # 知苗易约平台

def traverse_req(queue: Queue):
    '''
    遍历请求url队列，并对请求结果做重试处理
    '''
    res_list = []
    while(not queue.empty()):
        urlItem = queue.get()
        try:
            (response, proxies, userAgents) = requestGet(urlItem['url'])
        except Exception as e:
            log.info(f'请求异常: {e}')
            log.info(f'重试次数{urlItem["requestCount"]}')
            log.debug(f'队列是否为空: {queue.empty()}')
            if urlItem['requestCount'] < 5:
                urlItem['requestCount'] = urlItem['requestCount'] + 1
                queue.put(urlItem)
                log.debug(f'队列是否为空: {queue.empty()}')
                continue
            else:
                log.error(f'url: {urlItem["url"]}一直重试失败，最终放弃重试! 使用的代理是{proxies},useragent是{userAgents}')
                continue

        log.info(f'状态码: {response.status_code}')
        if response.status_code == 501 or response.status_code == 403:
            if urlItem['requestCount'] < 5:
                urlItem['requestCount'] = urlItem['requestCount'] + 1
                queue.put(urlItem)
                continue
            else:
                log.error(f'url: {urlItem["url"]}一直重试失败，最终放弃重试! 使用的代理是{proxies},useragent是{userAgents}')
                continue

        res = json.loads(response.content)
        if res['status'] != 200:
            log.error(f'url: {urlItem["url"]}一直重试失败，最终放弃重试! 使用的代理是{proxies},useragent是{userAgents}')
            continue

        log.info(f'请求结果: {res}')
        res_list.append(res)
    
    return res_list

@scheduler.scheduled_job('cron', id='info_fusion', name='hold_session', hour='*/17')
def info_fusion_job():
    common_url = 'https://cloud.cn2030.com/sc/wx/HandlerSubscribe.ashx'
    # 构建九价和四价的url列表
    jiujia_province_url_queue = Queue(maxsize=100)
    sijia_province_url_queue = Queue(maxsize=100)
    for key in provinceMap:
        city = parse.quote(f'["{key}","",""]')
        # todo 加了经纬度，后期可以考虑动态生成，避免被封的风险
        jiujia_province_url_queue.put({
            'url': f'{common_url}?act=CustomerList&city={city}&id=0&cityCode={provinceMap[key]}&product={JIUJIA}&lat=22.532732009887695&lng=113.9706802368164',
            'requestCount': 0
        })
        sijia_province_url_queue.put({
            'url': f'{common_url}?act=CustomerList&city={city}&id=0&cityCode={provinceMap[key]}&product={SIJIA}&lat=22.532732009887695&lng=113.9706802368164',
            'requestCount': 0
        })
        
    # 获取可预约医院
    hospitalres_list = traverse_req(jiujia_province_url_queue)
    hos_list = []
    for item in hospitalres_list:
        hos_list.extend(item['list'])

    jiujia_hos_url_queue = Queue(maxsize=len(hos_list))
    for item in hospitalres_list:
        for hos in item['list']:
            log.info(f'tags: {hos["tags"]}')
            if '可预约' in hos['tags']:
                jiujia_hos_url_queue.put({
                    'url': f'{common_url}?act=CustomerProduct&id={hos["id"]}&lat=22.532732009887695&lng=113.9706802368164',
                    'requestCount': 0
                })
    # 获取疫苗信息
    miao_list = traverse_req(jiujia_hos_url_queue)
    for item in miao_list:
        for miao in item['list']:
            log.debug(f'疫苗信息: {miao}')
            if not miao['enable']: # 可预约
                continue
            is_jiujia = miao['text'].find('九价')
            if is_jiujia == -1: # 不是九价
                continue
            
            log.debug(f'上面打印的疫苗可预约!')
            date_list = miao['date'].split('至')
            start_date = date_auto_completion(date_list[0])
            end_date = date_auto_completion(date_list[1])
            # 去重
            model = MiaoModel(title=miao['text'], type=JIUJIA, address=item['addr'], hosptal=item['cname'],
                starttime=start_date, endtime=end_date, platform=PLATFORM_ZHIMIAO)
            model.save()

    log.info(f'疫苗信息搜集完成!')
