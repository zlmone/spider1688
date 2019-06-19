import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from spider1688.items import CompanyItem
from spider1688.items import PetBedItem
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time
import random

class PetBed1688Spider(scrapy.Spider):
    name = "pet_bed_1688"

    allowed_domains = ['1688.com']
    custom_settings = {
        'MONGO_URL': 'mongodb://localhost:27017/',
        'MONGO_DATABASE':'1688'
    }
    i = 0
    start_urls = [
        'https://s.1688.com/selloffer/offer_search.htm?keywords=%B3%E8%CE%EF%B9%B7%CE%D1&button_click=top&earseDirect=false&n=y&netType=1%2C11&sug=1_0'
    ]

    # js控制浏览器滚动到底部js
    js = """
    function sleep()
    {

    }
    function scrollToBottom() {
        var Height = document.body.clientHeight,  //文本高度
            screenHeight = window.innerHeight,  //屏幕高度
            INTERVAL = 300,  // 滚动动作之间的间隔时间
            delta = 300,  //每次滚动距离
            curScrollTop = 0;    //当前window.scrollTop 值
        console.info(Height)
        var scroll = function () {
            //curScrollTop = document.body.scrollTop;
            curScrollTop = curScrollTop + delta;
            window.scrollTo(0,curScrollTop);
            console.info("偏移量:"+delta)
            console.info("当前位置:"+curScrollTop)
        };
        var timer = setInterval(function () {
            var curHeight = curScrollTop + screenHeight;
            var Height = document.body.clientHeight;
            if (curHeight >= Height){   //滚动到页面底部时，结束滚动
                clearInterval(timer);
                window.isdone="yes";
            }
            scroll();
        }, INTERVAL);
    };
    scrollToBottom();
    """

    def __init__(self, chrome_path):
        self.driver = webdriver.Chrome(chrome_path)
    
    def closed(self, spider):
        self.driver.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(chrome_path=crawler.settings.get("CHROME_LOCATION"))
    
    def scroll_until_loaded(self):
        check_height = self.driver.execute_script("return document.body.scrollHeight;")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.wait.until(lambda driver: self.driver.execute_script("return document.body.scrollHeight;") > check_height)
                check_height = self.driver.execute_script("return document.body.scrollHeight;")
            except TimeoutException:
                break

    def parse_store(self, response):
        # 1688上卖宠物狗窝的店
        company = CompanyItem()
        company['item_id'] = "1688_store"
        name = response.css('div.nameArea a.name::text')
        company['company_name'] = name.get()
        company['run_years'] = response.css('span.year-number::text').get()
        company['seller_name'] = response.css('div.contactSeller a.name::text').get()
        company['busyness_mode'] = response.css('span.biz-type-model::text').get().strip()
        company['company_address'] = response.css('div.address span.disc::text').get()
        company['url_in1688'] = response.css('div.detail div.base-info a::attr(href)').get()
        # 货描
        hm_higher_or_lower = response.css("div.description-show-hm[style='display: block;'] span::attr(class)").get()
        hm_value = response.css("div.description-show-hm[style='display: block;'] span::text").get()
        if hm_higher_or_lower is None:
            company['real_vs_descripiton'] = ''
        elif "higher" in hm_higher_or_lower:
            hm_higher_or_lower = "higher:"
            company['real_vs_descripiton'] = hm_higher_or_lower + hm_value
        else:
            hm_higher_or_lower = "lower:"
            company['real_vs_descripiton'] = hm_higher_or_lower + hm_value

        # 响应
        xy_higher_or_lower = response.css("div.description-show-xy[style='display: block;'] span::attr(class)").get()
        xy_value = response.css("div.description-show-xy[style='display: block;'] span::text").get()
        if xy_higher_or_lower is None:
            company['reply_speed'] = ""
        elif "higher" in xy_higher_or_lower:
            xy_higher_or_lower = "higher:"
            company['reply_speed'] = xy_higher_or_lower + xy_value
        else:
            xy_higher_or_lower = "lower:"
            company['reply_speed'] = xy_higher_or_lower + xy_value

        # 发货
        fh_higher_or_lower = response.css("div.description-show-fh[style='display: block;'] span::attr(class)").get()
        fh_value = response.css("div.description-show-fh[style='display: block;'] span::text").get()
        if fh_higher_or_lower is None:
            company['delivery_speed'] = ''
        elif "higher" in fh_higher_or_lower:
            fh_higher_or_lower = "higher:"
            company['delivery_speed'] = fh_higher_or_lower + fh_value
        else:
            fh_higher_or_lower = "lower:"
            company['delivery_speed'] = fh_higher_or_lower + fh_value
      
        company['buy_again'] = response.css("span.description-show-ht[style='display: block;']::text").get()

        return company

    def parse_ped_bed(self, response):
        pet_bed = PetBedItem()
        pet_bed['item_id'] = "pet_bed"
        de_features = response.css('div.obj-content td.de-feature::text').getall()
        de_values = response.css('div.obj-content td.de-value::text').getall()
        size_values = response.css('table.table-sku td.name span::text').getall()
        size_prices = response.css('table.table-sku td.price span em.value::text').getall()
        good_images = response.css('ul.nav.fd-clr li.tab-trigger::attr(data-imgs)').getall()
        bargain_number = response.css('p.bargain-number a em.value::text').get()

        pet_bed['product_name'] = response.css('h1.d-title::text').get()
        # 开始设值
        size_price_map = dict()
        min_len = min(len(size_values), len(size_prices))
        for i in range(0, min_len):
            size_price_map[size_values[i]] = size_prices[i]
        
        pet_bed['size_prices'] = size_price_map
        pet_bed['product_image'] = good_images
        
        if '材质' in de_features:
            material_index = de_features.index('材质')
            pet_bed['material'] = de_values[material_index]
        if '产地' in de_features:
            address_index = de_features.index('产地')
            pet_bed['product_address'] = de_values[address_index]
        if '是否进口' in de_features:
            import_index = de_features.index('是否进口')
            pet_bed['is_import'] = de_values[import_index]
        if '产品类别' in de_features:
            type_index = de_features.index('产品类别')
            pet_bed['product_type'] = de_values[type_index]
        if '货号' in de_features:
            hh_index = de_features.index('货号')
            pet_bed['product_number'] = de_values[hh_index]
        if '是否专利货源' in de_features:
            patent_index = de_features.index('是否专利货源')
            pet_bed['patent_source'] = de_values[patent_index]
        if '颜色' in de_features:
            color_index = de_features.index('颜色')
            pet_bed['product_color_text'] = de_values[color_index]
        if '规格' in de_features:
            size_index = de_features.index('规格')
            pet_bed['product_specification'] = de_values[size_index]
        if '主要下游平台' in de_features:
            downstream_index = de_features.index('主要下游平台')
            pet_bed['downstream_platform'] = de_values[downstream_index]
        if '是否跨境货源' in de_features:
            cross_index = de_features.index('是否跨境货源')
            pet_bed['cross_border'] = de_values[cross_index]

        return pet_bed


    def parse(self, response):
        # until_ele = WebDriverWait(self.driver,10).until(EC.presence_of_element_located(By.ID, 'sm-maindata'))
        time.sleep(random.randint(10,15))
        ele = self.driver.find_element_by_class_name('s-overlay-close')
        if ele:
            ele.click()
        input_ele = self.driver.find_element_by_css_selector('input.sm-widget-input')
        action =  ActionChains(self.driver)
        action.move_to_element(input_ele).perform()
        time.sleep(random.randint(1, 2))
        self.driver.find_element_by_css_selector('input.sm-widget-input').clear()
        self.driver.find_element_by_css_selector('input.sm-widget-input').send_keys("宠物狗窝")
        time.sleep(random.randint(1,2))
        self.driver.find_element_by_css_selector('input.sm-widget-input').send_keys(Keys.RETURN)
        
        while True:
            self.driver.execute_script(self.js)
            isdone = self.driver.execute_script("return window.isdone")
            while  isdone != "yes":
                isdone = self.driver.execute_script("return window.isdone")
            self.driver.execute_script("window.isdone = 'no'")
            # 回到顶部
            self.driver.execute_script('window.scrollTo(0, 0)')
            next_page = self.driver.find_element_by_css_selector("a.fui-next")
            responseText = self.driver.page_source
            urls = Selector(text=responseText).css('div.sm-offer ul.fd-clr li a.sm-offer-photoLink::attr(href)').getall()
            js_new_tab = "window.open('', '_blank');"
            self.driver.execute_script(js_new_tab)
            for url in urls:
                if "dj.1688.com" in url:
                    continue
                # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
                
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(url)
                time.sleep(random.randint(5,10))
                html = self.driver.page_source
                detail = Selector(text=self.driver.page_source)
                yield self.parse_store(detail)
                yield self.parse_ped_bed(detail)
                time.sleep(random.randint(5, 10))
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(random.randint(5,10))
            try:
                time.sleep(10)
                next_page.click()
            except Exception as e:
                print("done")


        