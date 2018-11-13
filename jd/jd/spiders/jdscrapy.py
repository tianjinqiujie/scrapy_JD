# -*- coding: utf-8 -*-
'''
shop_name: 商品名称
shop_url: 商品链接
shop_id: 商品ID
cate_id: 分类ID（能扒到就扒）
cate_name: 分类名称
shop_image_url: 商品图片
shop_price: 商品价格
shop_voucher: 优惠券（暂时不用）
shop_buy_num: 销量
shop_buy_comment: 评论总和数量
shop_store_name: 店铺
store_describe: 店家描述
store_service: 店家服务
store_logistics: 店家物流
shop_type: 网站数据-小写拼音
shop_address: 商家地址
cate_name: 类名

'''
import json
import scrapy
import requests
import urllib
import random

from jd.items import JDSaveItem
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor

class ProxyMiddleware(object):
   def get_ip(self):
       ret = requests.get("http://proxy.httpdaili.com/apinew.asp?text=true&noinfo=true&sl=10&ddbh=gs921302&tdsourcetag=s_pctim_aiomsg")  # 你需要的网址
       ret.encoding = "UTF-8"
       return ret.text

   def verification(self, ip):
       ret = requests.get('http://www.baidu.com', timeout=3,
                          proxies={"https": "https://{}".format(ip)})

       if ret.status_code == 200:
           return ip
   def process_request(self):
       ret = self.get_ip().split("\r\n")
       ret_ip = random.choice(ret)
       ret_ip = self.verification(ret_ip)
       if ret_ip:
           return ret_ip

proxyclass = ProxyMiddleware()


class JdscrapySpider(scrapy.Spider):
    name = 'jdscrapy'
    allowed_domains = ['jd.com']
    start_urls = ['https://www.jd.com/allSort.aspx']

    header = {
        'Host': 'club.jd.com',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    list_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'list.jd.com',
        'If-Modified-Since': 'Mon, 22 Jan 2018 06:23:20 GMT',
        'Upgrade-Insecure-Requests': '1'
    }
    info_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'item.jd.com',
        'If-Modified-Since': 'Mon, 22 Jan 2018 06:23:20 GMT',
        'Upgrade-Insecure-Requests': '1'
    }

    def parse(self, response):
        '''
        解析首页并获取分类链接
        :param response:
        :return:
        '''
        # 解析list链接
        pattern = "https://list\.jd\.com/list\.html\?cat=.*"
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        # print("发现list页面共：【%s】" % len(links))

        for i in links:
            # print("-------------------->%s" % i.url)
            yield scrapy.Request(i.url, callback=self.next_page)

    def next_page(self, response):
        '''
        获取下一页地址
        :param response:
        :return:
        '''
        # 获取page total
        page_total = int(response.css('span.fp-text i::text').extract_first())
        # print("开始获取下一页...")
        for page in range(1, page_total + 1):
        # for page in range(1, 21):
            page_url = "%s&page=%s" % (response.url, page)
            # print("获取list：【%s】，第【%s】页。" % (response.url, page))
            yield SplashRequest(page_url, args={'wait': 0.5, 'images': 0}, callback=self.parse_shop,
                                splash_headers=self.header)

    def parse_shop(self, response):
        '''
        商品列表页面，进一步跳转商品详细页面
        :param response:
        :return:
        '''
        sel_list = response.xpath('//div[@id="plist"]').xpath('.//li[@class="gl-item"]')
        for sel in sel_list:
            # 商品URL
            url = "http:%s" % sel.css(".p-name a::attr('href')").extract_first()
            # 商品ID
            shop_id = url.split("/")[-1].split(".")[0]

            # 商品名称
            title = sel.css(".p-name a em::text").extract_first().strip("\n").strip(" ")
            session = requests.Session()
            comment_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={shop_id}&score=0&sortType=5&page={page_num}&pageSize=10&isShadowSku=0&fold=1".format(
                shop_id=shop_id, page_num=0)
            html = session.get(comment_url, headers=self.header)
            # 获取商品评价页 json
            try:
                comment_json = json.loads(html.text)
            except:
                return
            # 获取评价信息
            public_comment = comment_json['productCommentSummary']
            # 评价数
            comment_num = public_comment['commentCount']
            # 获取好评率
            good_comment_rate = public_comment['goodRate']
            # 好评数
            good_comment = public_comment['goodCount']
            # 中评数
            general_count = public_comment['generalCount']
            # 差评
            poor_count = public_comment['poorCount']
            # print("---------------------------------->", good_comment_rate, good_comment, general_count, poor_count)
            # 中评率
            try: 
                general_comment_rate = (general_count / (good_comment + general_count + poor_count)) 
            except ZeroDivisionError as e:
                general_comment_rate = 0 

            # 差评率
            try: 
                poor_comment_rate = (poor_count / (good_comment + general_count + poor_count))
            except ZeroDivisionError as e:
                poor_comment_rate = 0 





            # 默认好评
            # default_comment_num = public_comment['defaultGoodCount']
            # 获取热评信息
            # hot_comment = comment_json['hotCommentTagStatistics']
            # if len(hot_comment) == 0:
            #     hot_comment_dict = "Null"
            # else:
            #     hot_comment_dict = {}
            #     for i in hot_comment:
            #         hot_comment_dict[i['id']] = {'name': i['name'], 'count': i['count']}
            #     hot_comment_dict = json.dumps(hot_comment_dict)

            shop_info = {
                'url': url,
                'shop_id': shop_id,
                'title': title,
                'comment_num': comment_num,
                "good_comment_rate": good_comment_rate,
                "general_comment_rate": general_comment_rate,
                "poor_comment_rate": poor_comment_rate
            }
            yield scrapy.Request(url, meta=shop_info, headers=self.info_header, callback=self.shop_info)

    def shop_info(self, response):
        '''
        解析商品详细页面，获取商品价格，
        :param response:
        :return:
        '''

        shop_id = response.meta.get("shop_id")
        url = response.meta.get("url")  # 商品URL
        title = response.meta.get("title")
        comment_num = response.meta.get("comment_num")
        good_comment_rate = response.meta.get("good_comment_rate")
        general_comment_rate = response.meta.get("general_comment_rate")
        poor_comment_rate = response.meta.get("poor_comment_rate")

        # 分类
        classification = response.css('.first > a:nth-child(1)::text').extract_first()
        # 二级分类
        classification2 = response.css('.crumb > div:nth-child(3) > a:nth-child(1)::text').extract_first()

        # 获取价格
        price_url2 = 'https://p.3.cn/prices/mgets?skuIds=J_' + shop_id + 'pdtk=&type=1&area=1_72_4137_0&pdtk=&pduid=1541308714181321549998&pdpin=&pin=null&pdbp=0&'
        price_url1 = "https://c.3.cn/recommend?&methods=accessories&sku=%s&cat=670,677,678" %shop_id
        # # 获取地址
        price_url = urllib.request.Request(price_url1)
         

        # # 打开连接
        price_response = urllib.request.urlopen(price_url)
        # content = json.loads(price_response.read())[0].get("p")
        # content = eval(str(price_response.read(), encoding="UTF-8"))

        try:
            try:
                content = json.loads(price_response.read().decode("gbk")).get("accessories").get("data").get("wMaprice")
            except UnicodeDecodeError as e:
                content = json.loads(price_response.read().decode("gb2312")).get("accessories").get("data").get("wMaprice")
        except AttributeError as e:
            price_url = urllib.request.Request(price_url2)
            # # 打开连接
            price_response = urllib.request.urlopen(price_url)
            content = json.loads(price_response.read().decode("UTF-8"))[0].get("p")
        if not content:
            return
        # print("*" * 20, content, type(content))
        price = content
        # 图片连接
        imgs = response.css(".spec-items > ul > li > img::attr(src)").extract_first()
        # 优惠券
        # coupon = response.css("span.quan-item:nth-child(1) > span::text").extract()
        # 店铺名称

        shop_store_name = response.css(
            ".popbox-inner > div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)::text").extract_first()

        # 店家描述,服务，物流
        # store_describe = response.css(
        #     "div.score-part:nth-child(1) > span:nth-child(2) > em:nth-child(1)::text").extract_first()
        # store_service = response.css(
        #     "div.score-part:nth-child(2) > span:nth-child(2) > em:nth-child(1)::text").extract_first()
        # store_logistics = response.css(
        #     "div.score-part:nth-child(3) > span:nth-child(2) > em:nth-child(1)::text").extract_first()

        if not shop_store_name:
            shop_store_name = "京东自营"
	
        shop_address = response.css("#summary-service:nth-child(2)::text").extract_first()
        if not shop_address:
            shop_address = 0
        shop_info = {
            "cate_name": classification,
            "cate_x_name": classification2,
            'shop_url': url,
            'shop_id': shop_id,
            'shop_name': title,
            'shop_price': price,
            'shop_image_url': imgs,
            'shop_buy_comment': comment_num,
            "shop_buy_num": comment_num,
            "shop_type": 3,
            "shop_store_name": shop_store_name,
            "shop_address": shop_address,
            "good_comment_rate": good_comment_rate,
            "general_comment_rate": general_comment_rate,
            "poor_comment_rate": poor_comment_rate

        }

        print("----->", shop_info)
        '''
        cate_id: 分类ID（能扒到就扒）
        shop_voucher: 优惠券（暂时不用）
        '''

        '''
        数据的存储
        '''
        JDItem = JDSaveItem()
        JDItem["goods_cate_name"] = shop_info.get("cate_name")                # 商品分类名称
        #JDItem["cate_x_name"] = shop_info.get("cate_x_name")
        JDItem["goods_detail_url"] = shop_info.get("shop_url")                # 商品详情链接
        JDItem["goods_product_id"] = shop_info.get("shop_id")                 # 第三方平台ID
        JDItem["goods_name"] = shop_info.get("shop_name")                     # 商品名称
        JDItem["goods_price"] = shop_info.get("shop_price")                   # 价格
        JDItem["goods_image"] = shop_info.get("shop_image_url")               # 商品图片链接
        #JDItem["shop_buy_comment"] = shop_info.get("shop_buy_comment")
        JDItem["goods_sale_num"] = shop_info.get("shop_buy_num")              # 销售量
        JDItem["platform"] = shop_info.get("shop_type")                       # 平台名称  3
        JDItem["shop_name"] = shop_info.get("shop_store_name")                # 店铺名称
        JDItem["goods_total_score"] = shop_info.get("good_comment_rate")      # 评分
        #JDItem["store_review"] = shop_info.get("general_comment_rate")
        #JDItem["store_bad"] = shop_info.get("poor_comment_rate")
        #JDItem["shop_address"] = shop_info.get("shop_address")

        yield JDItem

        # #获取评价其他信息
        # page_num = (comment_num + 9) // 10
        # if page_num >= 100:
        #     page_num = 100
        # # print("【%s】评价页面共计【%s】" % (title, page_num))
        # for page in range(0, page_num):
        #     comment_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={shop_ids}&score=0&sortType=5&page={page_nums}&pageSize=10&isShadowSku=0&fold=1".format(
        #         shop_ids=shop_id, page_nums=page)
        #     # print("yield评价第%s页" % page)
        #     yield scrapy.Request(comment_url, meta=shop_info, headers=self.header, callback=self.parse_comment)

    '''
    def parse_comment(self, response):
        \'''
        解析商品更多评价，暂时不需要

        :param response:
        :return:
        \'''
        # print("开始解析评价")
        shop_id = response.meta.get("shop_id")
        url = response.meta.get("url")
        title = response.meta.get("title")
        price = response.meta.get("price")
        comment_num = response.meta.get("comment_num")
        # good_comment_rate = response.meta.get("good_comment_rate")
        # good_comment = response.meta.get("good_comment")
        # general_count = response.meta.get("general_count")
        # poor_c\ount = response.meta.get("poor_count")
        # hot_comment_dict = response.meta.get("hot_comment_dict")
        # default_comment_num = response.meta.get("default_comment_num")
        try:
            comment_json = json.loads(response.text)
        except:
            shop_info = {
                'url': url,
                'shop_id': shop_id,
                'title': title,
                'price': price,
                'comment_num': comment_num,
                # 'good_comment_rate': good_comment_rate,
                # 'good_comment': good_comment,
                # 'general_count': general_count,
                # 'poor_count': poor_count,
                # 'hot_comment_dict': hot_comment_dict,
                # 'default_comment_num': default_comment_num,
            }

            yield scrapy.Request(response.url, meta=shop_info, headers=self.header, callback=self.parse_comment)
        else:
            comment_info = comment_json['comments']
            for comment in comment_info:
                # JDItem = JDAllItem()
                # 主键 评论ID
                comment_id = comment['id']
                comment_context = comment['content']
                comnent_time = comment['creationTime']
                # 用户评分
                comment_score = comment['score']
                # 来源
                comment_source = comment['userClientShow']
                if comment_source == []:
                    comment_source = "非手机端"
                # 型号
                try:
                    produce_size = comment['productSize']
                except:
                    produce_size = "None"
                # 颜色
                try:
                    produce_color = comment['productColor']
                except:
                    produce_color = "None"
                # 用户级别
                user_level = comment['userLevelName']
                try:
                    append_comment = comment['afterUserComment']['hAfterUserComment']['content']
                    append_comment_time = comment['afterUserComment']['created']
                except:
                    append_comment = "无追加"
                    append_comment_time = "None"
                # 用户京享值
                user_exp = comment['userExpValue']
                # 评价点赞数
                comment_thumpup = comment['usefulVoteCount']
                # 店铺回复
                try:
                    comment_reply = comment['replies']
                except:
                    comment_reply = []
                if len(comment_reply) == 0:
                    comment_reply_content = "Null"
                    comment_reply_time = "Null"
                else:
                    comment_reply_content = comment_reply[0]["content"]
                    comment_reply_time = comment_reply[0]["creationTime"]
                # JDItem["shop_id"] = shop_id
                # JDItem["url"] = url
                # JDItem["title"] = title
                # JDItem["price"] = price
                # JDItem["comment_num"] = comment_num
                # # JDItem["good_comment_rate"] = good_comment_rate
                # # JDItem["good_comment"] = good_comment
                # # JDItem["general_count"] = general_count
                # # JDItem["poor_count"] = poor_count
                # # JDItem["hot_comment_dict"] = hot_comment_dict
                # # JDItem["default_comment_num"] = default_comment_num
                # JDItem["comment_id"] = comment_id
                # JDItem["comment_context"] = comment_context
                # JDItem["comnent_time"] = comnent_time
                # JDItem["comment_score"] = comment_score
                # JDItem["comment_source"] = comment_source
                # JDItem["produce_size"] = produce_size
                # JDItem["produce_color"] = produce_color
                # JDItem["user_level"] = user_level
                # JDItem["user_exp"] = user_exp
                # JDItem["comment_thumpup"] = comment_thumpup
                # JDItem["comment_reply_content"] = comment_reply_content
                # JDItem["comment_reply_time"] = comment_reply_time
                # JDItem["append_comment"] = append_comment
                # JDItem["append_comment_time"] = append_comment_time
                # print("yield评价")
                # yield JDItem
            '''
