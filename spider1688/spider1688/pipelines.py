# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class Spider1688Pipeline(object):
    def process_item(self, item, spider):
        return item

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import urllib.request
import os
import concurrent.futures
import socket
import logging
import ast
from scrapy.utils.log import configure_logging
from scrapy.exceptions import DropItem

class MediaPipeline(object):
    def __init__(self, *args, **kwargs):
        # configure_logging(install_root_handler=False)
        logging.basicConfig(
            filename='/mnt/e/pipeline_log.txt',
            format='%(levelname)s: %(message)s',
            level=logging.ERROR
        )
        self.e = concurrent.futures.ThreadPoolExecutor(max_workers=6)
        socket.setdefaulttimeout(30)

    def auto_download(self, url, file_path):
        try:
            self.e.submit(urllib.request.urlretrieve,url, file_path)
        except socket.timeout:
            count = 1
            while count < 10:
                try:
                    self.e.submit(urllib.request.urlretrieve,url, file_path)
                    break
                except socket.timeout:
                    err_info = 'Reloading for %d time' %count if count == 1 else 'Reloading for %d times'%count
                    logging.error(err_info)
                    count += 1
            if count == 10:
                logging.error('downloading picture failed!')

    def process_item(self, item, spider):
        if item['item_id'] == 'pet_bed':
            root_folder = '/mnt/e/spider-download/' + spider.name +'/image/' + item['product_number'] + '/'
            pre_img_folder = root_folder + 'pre_images/'
            origin_img_folder = root_folder + 'original_images/'
            try:
                if not os.path.exists(pre_img_folder):
                    os.makedirs(pre_img_folder, mode=0o777)
                if not os.path.exists(origin_img_folder):
                    os.makedirs(origin_img_folder, mode=0o777)
            except OSError as e:
                print("mkdir error" + e.strerror)

            preview_images = []
            original_images = []
            for image in item['product_image']:
                preview_images.append(ast.literal_eval(image).get('preview'))
                original_images.append(ast.literal_eval(image).get('original'))
            # 400 X 400的预览图
            for pre_img_url in preview_images:
                img_hash = str(abs(hash(pre_img_url)) % (10**8)) + '.jpg'
                self.auto_download(pre_img_url, pre_img_folder  + img_hash) 
            # 原始大图
            for origin_img_url in original_images:
                img_hash = str(abs(hash(origin_img_url)) % (10**8)) + '.jpg'
                self.auto_download(origin_img_url, origin_img_folder + img_hash) 

        return item

class MongoPipeline(object):
    petBd_collection = 'pet_bed'
    company_1688_collection = 'ped_bed_store'

    def __init__(self,  mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE', 'noname')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        


    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if item['item_id'] == '1688_store':
            self.db[self.company_1688_collection].insert_one(dict(item))
        elif item['item_id'] == 'pet_bed':
            self.db[self.petBd_collection].insert_one(dict(item))
        return item


