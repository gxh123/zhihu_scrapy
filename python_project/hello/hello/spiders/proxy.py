# -*- coding: utf-8 -*-
import urllib2
import random
import time
# import lxml
import re



user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
]

count = 0

def Get_proxy_ip():
    headers = {
            'Host': 'www.xicidaili.com',
            'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'http://www.xicidaili.com/',
            }
    req = urllib2.Request('http://www.xicidaili.com/nn/', headers=headers)
    response = urllib2.urlopen(req)
    html = response.read().decode('utf-8')
    proxy_list = []
    ip_list = re.findall('\d+\.\d+\.\d+\.\d+',html)
    port_list = re.findall('<td>\d+</td>',html)
    for i in range(len(ip_list)):
        ip = ip_list[i]
        port = re.sub('<td>|</td>', '', port_list[i])
        proxy = '%s:%s' %(ip,port)
        proxy_list.append(proxy)
    return proxy_list

def Proxy_read(proxy_list, user_agent_list, i):
    proxy_ip = proxy_list[i]
    print('proxy_ip:%s' % proxy_ip)
    user_agent = random.choice(user_agent_list)
    print('user_agent:%s' % user_agent)
    sleep_time = random.randint(1,3)
    print('sleep_time:%s s'  % sleep_time)
    time.sleep(sleep_time)
    print('开始获取')
    headers = {
            'Host': 's9-im-notify.csdn.net',
            'Origin':'http://blog.csdn.net',
            'User-Agent': user_agent,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'http://blog.csdn.net/u010620031/article/details/51068703',
            }

    proxy_support = urllib2.ProxyHandler({'http':proxy_ip})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

    req = urllib2.Request('http://blog.csdn.net/u010620031/article/details/51068703',headers=headers)
    try:
        html = urllib2.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print('******打开失败！******')
    else:
        global count
        count +=1
        print('OK!总计成功%s次！'%count)

if __name__ == '__main__':
    proxy_list = Get_proxy_ip()
    for i in range(100):
        Proxy_read(proxy_list, user_agent_list, i)