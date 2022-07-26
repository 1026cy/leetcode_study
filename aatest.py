# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
@Time    : 2022/3/25 14:50
@Author  : Jql
@File    : 产业政策大数据.py
"""

import random
from copy import deepcopy

import execjs
# import redis
import requests
import time
import pymysql
import datetime
import json
from urllib import parse
from concurrent.futures import ThreadPoolExecutor
from queue import Queue




def paramsEncode(a,b):
    def js_from_file(file_name):
        """
        读取js文件
        :return:
        """
        with open(file_name, 'r', encoding='UTF-8') as file:
            result = file.read()

        return result
    # 编译加载js字符串
    context1 = execjs.compile(js_from_file('./产业政策大数据.js'))
    aa = context1.call("paramsEncode", a, b)
    print(aa)
    print(chr(1))
    print(chr(0x00001))
    data = ''.join([chr(i) for i in aa['data']])
    return data



def get_ip():
    return None



def to_time(y):
    if isinstance(y, int):
        t = y / 1000
        time_array = time.localtime(t)
        # other_s_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        other_s_time = time.strftime("%Y-%m-%d", time_array)
        return other_s_time
    else:
        return y


def get_total_content(content_id):
    a, b = 10, 24
    # print(chr(a), chr(b))
    content_id = chr(a)+chr(b) + content_id
    try:
        url = f'http://www.spolicy.com/info_api/policyInfo/getPolicyInfo'
        headers = {
            'Host': 'www.spolicy.com',
            'Proxy-Connection': 'keep-alive',
            'Content-Length': '26',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'Content-Type': 'application/octet-stream',
            'Origin': 'http://www.spolicy.com',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-GB-oxendict;q=0.6,zh-HK;q=0.5',
            'Cookie': 'JSESSIONID=7F89789FFDE8A33129B64D631993A18F',
        }
        resp = requests.post(url, headers=headers, data=content_id, verify=False)
        # print(resp.content.decode(resp.apparent_encoding))
        jjj = resp.json()
        return jjj['data']['rows']['content']
    except Exception as e:
        print(e.__traceback__.tb_lineno, e)
        return ''


class ChanYeZhengCe:

    def __init__(self):
        self.host = '192.168.1.77'
        self.user = 'root'
        self.pwd = '798236031'
        self.db = '舆情监测'
        self.city = '产业政策大数据_1'
        self.table_name = '产业政策大数据_1'
        self.url_queue = Queue()
        self.url_detail_queue = Queue()
        self.target_data = Queue()
        self.headers = {
            'Host': 'www.spolicy.com',
            'Proxy-Connection': 'keep-alive',
            'Content-Length': '26',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'Content-Type': 'application/octet-stream',
            'Origin': 'http://www.spolicy.com',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-GB-oxendict;q=0.6,zh-HK;q=0.5',
            'Cookie': 'JSESSIONID=7F89789FFDE8A33129B64D631993A18F',
        }
        self.url = 'http://www.spolicy.com/'
        self.columns = ['policy_type', 'title', 'issuing_agency', 'technical_field', 'pub_date', 'content', 'file_path',
                        'content_path', 'spider_time', 'url']

    def get_res(self, url, headers, data=None, json_data=None, params=None, flag='', method='get'):
        for i in range(12):
            try:
                proxies = get_ip()
                if method == 'get':
                    response = requests.get(url, proxies=proxies, params=params, headers=headers, timeout=60)
                else:
                    response = requests.post(url, proxies=proxies, data=data, json=json_data, headers=headers,
                                             timeout=60)
                return response
            except Exception as e:
                print(e.__traceback__.tb_lineno, e)
                time.sleep(5)
                if i == 11:
                    self.write_error(e, 'get_res')
        return '错误'

    def write_error(self, e, func_name, url=''):
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file = r'%s错误.txt' % self.city
        error_rows = str(e.__traceback__.tb_lineno)
        content = '%s错误:' % func_name + str(e) + '时间：' + str(cur_time) + '行数： ' + error_rows + \
                  '  href: ' + str(url)
        with open(file, 'a+') as f:
            f.write(content + '\n', )

    def save_table(self):
        while True:
            if self.target_data.empty():
                for i in range(60):
                    if self.target_data.empty():
                        time.sleep(1)
                    else:
                        break
                if self.target_data.empty() and self.url_queue.empty():
                    break
            else:
                data = self.target_data.get()

                try:
                    con = pymysql.connect(host=self.host, user=self.user, password=self.pwd, db=self.db)
                    cursor = con.cursor()
                    sel_sql = 'select title from %s where title="%s";' % (self.table_name, data["title"])
                    # print(sel_sql)
                    cursor.execute(sel_sql)
                    res = cursor.fetchall()
                    # 为空
                    if not res:
                        spider_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data['spider_time'] = spider_time
                        insert_sql = f'insert into {self.table_name} values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                        params = [data[k] for k in self.columns]
                        cursor.execute(insert_sql, params)
                        print('success')
                    else:
                        print('已有')
                    con.commit()
                    cursor.close()
                    con.close()
                except Exception as e:
                    self.write_error(e, 'save_table')

    def get_all_url(self):
        type_d = {
            '政策通知':'2',
            '政策文件':'4',
            '公示公告':'6',
            '政策要闻':'3',
            '政策解读':'5'
        }

        page_d = {
            '政策通知':'2',
            '政策文件':'4',
            '公示公告':'6',
            '政策要闻':'3',
            '政策解读':'5'
        }
        page_li = []
        for type_ in type_d:
            for page in range(1, 11):
                data = paramsEncode(page, type_d[type_])
                # data必须用这种方式生成，
                # print(data)
                page_li.append((data, type_))


        for data, policy_type in page_li:

            self.url_queue.put((data, policy_type))

        print('url 装载成功')

    def visit_url(self):
        while True:
            if self.url_queue.empty():
                break
            else:
                data, policy_type = self.url_queue.get()
                print(data, policy_type)
                try:
                    url = 'http://www.spolicy.com/info_api/policyType/showPolicyType'
                    res = self.get_res(url, self.headers, data=data, method='post')
                    print(res.text)
                    if res != '错误':
                        dt = json.loads(res.text)
                        rows = dt['data']['rows']
                        for dic in rows:
                            issuing_agency = dic['releaseOrganization']
                            technical_field = dic['industryName']
                            pub_date = dic['time']
                            content = dic['content']
                            content_id = dic['id']
                            total_content = get_total_content(content_id)
                            print(dic)
                            title = dic['title']
                            # file_path = ''
                            # if '附件' in content:
                            #     d_res = self.get_res(dic['url'], self.headers)
                            #
                            data_dic = {}
                            for k in self.columns:
                                data_dic[k] = ''
                            data_dic['issuing_agency'] = issuing_agency
                            data_dic['technical_field'] = technical_field
                            data_dic['pub_date'] = pub_date
                            data_dic['content'] = total_content
                            data_dic['policy_type'] = policy_type
                            data_dic['title'] = title
                            data_dic['content_path'] = dic['url']
                            data_dic['url'] = content_id

                            self.target_data.put(data_dic)
                    else:
                        print('get_url error')

                except Exception as e:
                    print(e, e.__traceback__.tb_lineno)

    def go_to(self):
        print(datetime.datetime.now())
        thread_pool_num = 1
        self.get_all_url()

        pool3 = ThreadPoolExecutor(max_workers=thread_pool_num)
        for i in range(thread_pool_num * 2):
            do = pool3.submit(self.visit_url)

        pool1 = ThreadPoolExecutor(max_workers=thread_pool_num)
        for i in range(thread_pool_num * 2):
            do = pool1.submit(self.save_table)
        pool3.shutdown(wait=True)
        pool1.shutdown(wait=True)


def run():
    chanye = ChanYeZhengCe()
    chanye.go_to()

'''
    policyList,
    refresh,
    nextPage,
    isLast,
    loading,
    pageNum,
    total,
    getList,
    requestTimes,
centralId: ""
city: ""
downtown: ""
garden: ""
pageNum: 2
pageSize: 20
policyType: 2
province: ""
sort: 0
'''

if __name__ == '__main__':
    # run()
    a = paramsEncode(1, '2')
    b = '2"*28@äÿH'
    b = '2"*28@H'
    b = '2"*28@H'

    print(a == b)
    print(b)
    print(a)
    time.sleep(2)
    headers = {
        'Host': 'www.spolicy.com',
        'Proxy-Connection': 'keep-alive',
        'Content-Length': '26',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Content-Type': 'application/octet-stream',
        'Origin': 'http://www.spolicy.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-GB-oxendict;q=0.6,zh-HK;q=0.5',
        'Cookie': 'JSESSIONID=3F817357772CA1368E3CBB1665BC98F9',
    }
    resp = requests.post('http://www.spolicy.com/info_api/policyType/showPolicyType', data=a, headers=headers)
    print(resp.text)




