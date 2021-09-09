# -*- coding: utf-8 -*-

import requests
import pandas as pd
from lxml import etree
import json

url = 'http://useragentstring.com/pages/useragentstring.php?typ=Mobile%20Browser'

header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)'
    }

response = requests.get(url,
                        headers=header,
                        timeout=60
                        )

tree = etree.HTML(response.text)
browsers = tree.xpath('//ul/li/a/text()')
browsers = [browser for browser in browsers if len(browser)>80]

with open('userAgents', 'w') as f:
    f.write(json.dumps(browsers))
print(browsers)
print(len(browsers))

df = pd.DataFrame({'id':range(1,len(browsers)+1), 'ua':browsers})
print(df)

# df.to_csv('user_agents.csv', index=False)