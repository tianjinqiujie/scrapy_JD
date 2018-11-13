# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JDSaveItem(scrapy.Item):
#    cate_name = scrapy.Field()
#    cate_x_name = scrapy.Field()
#    shop_url = scrapy.Field()
#    shop_id = scrapy.Field()
#    shop_name = scrapy.Field()
#    shop_price = scrapy.Field()
#    shop_image_url = scrapy.Field()
#    shop_buy_comment = scrapy.Field()
#    shop_buy_num = scrapy.Field()
#    shop_type = scrapy.Field()
#    shop_store_name = scrapy.Field()
#    store_praise = scrapy.Field()
#    store_review = scrapy.Field()
#    store_bad = scrapy.Field()
#    shop_address = scrapy.Field()

    goods_cate_name = scrapy.Field()
    goods_detail_url = scrapy.Field()
    goods_product_id = scrapy.Field()
    goods_name = scrapy.Field()
    goods_price = scrapy.Field()
    goods_image = scrapy.Field()
    goods_sale_num = scrapy.Field()
    platform = scrapy.Field()
    shop_name = scrapy.Field()
    goods_total_score = scrapy.Field()
    
	 

