# -*- coding: utf-8 -*-






import scrapy

from scrapy.http import Request
from items import GetNewFromSinaItem
import random

from urllib import request
import urllib
import demjson
from bs4 import BeautifulSoup
import html5lib
import time


def create_random_float():
    r = random.randint(0, 9999999999999999)
    return r * 0.0000000000000001


head_pages = {'Accept': '*/*',
              'Accept-Encoding': 'gzip, deflate',
              'Accept-Language': 'zh-CN,zh;q=0.9',
              'Connection': 'keep-alive',
              'Cookie':'SINAGLOBAL=172.16.118.87_1536741469.36880; U_TRS1=0000002e.80df77bc.5ba48c21.f218c2b3; UOR=blog.sina.com.cn,blog.sina.com.cn,; td_cookie=97312674; Apache=222.178.225.46_1539139882.596267; ULV=1539139958211:4:2:2:222.178.225.46_1539139882.596267:1539139882434; lxlrttp=1538731187; U_TRS2=0000002e.2b3c6eae.5bbd6a99.0e401565; SUB=_2AkMs4eWTf8NxqwJRmfgVy23mbY52yA3EieKavRRIJRMyHRl-yD83qlULtRB6B2HLfAesxhS4e4NkykralyGRmJxnL22C; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W53_SYeMqIWEOsxgfCklhM9; UM_distinctid=1665cdcf2fd1ff-0f8cb4b2e77bff-54103515-100200-1665cdcf2fe484',
              'Host': 'roll.news.sina.com.cn',
              'Referer': 'http://roll.news.sina.com.cn/s/channel.php?ch=01'}

headers_news = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Cookie': 'SINAGLOBAL=172.16.118.87_1536741469.36880; U_TRS1=0000002e.80df77bc.5ba48c21.f218c2b3; UOR=blog.sina.com.cn,blog.sina.com.cn,; Apache=222.178.225.46_1539139882.596267; ULV=1539139958211:4:2:2:222.178.225.46_1539139882.596267:1539139882434; Hm_lvt_35ddcac55ce8155015e5c5e313883b68=1539140239; lxlrttp=1538731187; U_TRS2=0000002e.2b3c6eae.5bbd6a99.0e401565; SUB=_2AkMs4eWTf8NxqwJRmfgVy23mbY52yA3EieKavRRIJRMyHRl-yD83qlULtRB6B2HLfAesxhS4e4NkykralyGRmJxnL22C; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W53_SYeMqIWEOsxgfCklhM9; CNZZDATA1264476941=1883597795-1539137307-%7C1539137307; CNZZDATA5581074=cnzz_eid%3D1302347415-1539137312-%26ntime%3D1539137312; CNZZDATA5581080=cnzz_eid%3D960431519-1539138976-%26ntime%3D1539138976; Hm_lpvt_35ddcac55ce8155015e5c5e313883b68=1539155226; UM_distinctid=1665cccf9a1257-0114cb4415115a-54103515-100200-1665cccf9a24ee; CNZZDATA5399792=cnzz_eid%3D1603665311-1539137871-http%253A%252F%252Fsports.sina.com.cn%252F%26ntime%3D1539154071; CNZZDATA5661630=cnzz_eid%3D1266904705-1539140010-http%253A%252F%252Fsports.sina.com.cn%252F%26ntime%3D1539149863',
                'If-Modified-Since': 'Wed, 10 Oct 2018 06:56:19 GMT',
                'Upgrade-Insecure-Requests': 1,
                }


class GetSinaNews(scrapy.Spider):
    name = "get_news"

    url_begin = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page="
    page_index = 35

    def start_requests(self):
        yield Request(url=self.url_begin + str(self.page_index), headers=head_pages, callback=self.parse)

    def parse(self, response):
        page_data = response.body.decode('gbk')
        page_data = page_data.rstrip(';')
        json_str_list = page_data.split('=')
        json_str = json_str_list[1]
        json_data = demjson.decode(json_str)
        totalcount = json_data['count']
        page_count = int(totalcount / 60) + 1
        news_list = json_data['list']

        for news_dict in news_list:

            channel_title = news_dict['channel']['title']
            channel_title_id = news_dict['channel']['id']
            title = news_dict['title']
            url = news_dict['url']
            #time.sleep(3)
            yield Request(url=url, meta={'channel_title': channel_title,
                                         'channel_title_id': channel_title_id,
                                         'title': title,
                                          }, callback= self.new_call_back)

        self.page_index = self.page_index + 1
        if self.page_index <= page_count:
            #time.sleep(3)
            print(self.url_begin + str(self.page_index))
            yield Request(url=self.url_begin + str(self.page_index), headers=head_pages, callback=self.parse)

    def new_call_back(self, response):
        data_items = GetNewFromSinaItem()
        data_items['news_type'] = response.meta['channel_title']

        text = response.body.decode('utf-8')

        bs_object = BeautifulSoup(text,"html5lib")

        article_node = bs_object.find_all("div", class_="article", id="artibody")
        if len(article_node) > 0:
            all_p = article_node[0].find_all('p')
            contents = ""
            for p in all_p:
                if (p is not None) and (p.string is not None):
                    contents = contents + p.string.strip()

            data_items['news_content'] = contents

            yield data_items
        # for child_node in article_node[0].children:
        #     print(child_node)





if __name__ == "__main__":
    req = request.Request(url='http://sports.sina.com.cn/g/pl/2018-10-10/doc-ihkvrhpt4914181.shtml')
    res = request.urlopen(req)
    print(res.read().decode('utf-8'))