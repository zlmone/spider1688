# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Spider1688Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CompanyItem(scrapy.Item):
    # item 标识
    item_id = scrapy.Field()
    # 卖家公司名称
    company_name = scrapy.Field()
    # 经营年数
    run_years = scrapy.Field()
    # 联系卖家
    seller_name = scrapy.Field()
    # 经营模式
    busyness_mode = scrapy.Field()
    # 1688上的地址
    url_in1688 = scrapy.Field()
    # 所在地区
    company_address = scrapy.Field()
    # 货描
    real_vs_descripiton = scrapy.Field()
    # 响应
    reply_speed = scrapy.Field()
    # 发货
    delivery_speed = scrapy.Field()
    # 回头率
    buy_again = scrapy.Field()


class PetBedItem(scrapy.Item):
    # item 标识
    item_id = scrapy.Field()
    # 产品名称
    product_name = scrapy.Field()
    product_store = scrapy.Field()
    # 材质
    material = scrapy.Field()
    # 产品类别
    product_type = scrapy.Field()
    # 产地
    product_address = scrapy.Field()
    # 货号
    product_number = scrapy.Field()
    # 是否专利货源
    patent_source = scrapy.Field()
    # 不同颜色产品图片
    product_color = scrapy.Field()
    # 有的商家没有颜色图片,只有文字描述
    product_color_text = scrapy.Field()
    # 品牌
    product_brand = scrapy.Field()
    # 每种规格价钱不一样
    # S 7.00
    # M 9.5
    # L 12.00
    # XL 19.00
    size_prices = scrapy.Field()
    product_specification = scrapy.Field()
    # 是否进口
    is_import = scrapy.Field()
    # 主要下游平台
    downstream_platform = scrapy.Field()
    # 主要销售地区
    sell_area = scrapy.Field()
    # 是否跨境货源
    cross_border = scrapy.Field()
    # 一系列图片
    product_image = scrapy.Field()
    # 30天内成交量
    bargain_number = scrapy.Field()


