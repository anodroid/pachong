from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
import csv
import re

class TM_products(object):
    def __init__(self,brand):
        self.brand = brand
        datenum = datetime.now().strftime('%Y%m%d%H%M')
        self.filename = '{}_{}.csv'.format(self.brand, datenum)
        # self.url = 'https://kisscat.tmall.com/'
        self.url = 'https://{}.tmall.com'.format(brand)
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.browser = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.browser, 10)
        self.products = []
    
    def login(self):
        url_login = 'https://login.tmall.com/'
        self.browser.get(url_login)
        time.sleep(5)
        self.browser.switch_to_frame('J_loginIframe')
        self.browser.find_element_by_id('fm-login-id').send_keys('')
        self.browser.find_element_by_id('fm-login-password').send_keys('')
        time.sleep(10)
        self.browser.find_element_by_class_name('fm-submit').click()
        time.sleep(5)
        return
    
    def get_pagenum(self):
        time.sleep(1)
        url = 'https://{}.tmall.com/search.htm'.format(self.brand)
        self.browser.get(url)
        # total_page = browser.find_element_by_class_name('ui-page-s-len').text
        try:
            pagenum = int(self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-page-s-len'))).text.split('/')[-1])
        except Exception as e:
            print(e)
        print('total {} pages'.format(pagenum))
        return pagenum
    
    def get_page_item(self):
        time.sleep(1)
        items = self.browser.find_elements_by_class_name('item')[0:-8]
        for i in items:
            item = {}
            try:
                item['id'] = i.get_attribute('data-id')
                item['name'] = i.find_element_by_xpath('.//dd[@class="detail"]/a').text
                item['price'] = i.find_element_by_class_name('c-price').text
                item['sale_num'] = i.find_element_by_css_selector('.sale-num').text
                item['comment'] = re.search (r'\d+',i.find_element_by_xpath('.//dd[@class="rates"]/div[@class="title"]//span').text).group()
            except NoSuchElementException:
                pass
            except Exception as e:
                print(e)
            self.products.append(item)
            print('Now having {} items.'.format(len(self.products)))

    def page_next(self):
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'next'))).click()
        
        
    def page_prev(self):
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'prev'))).click()
        
    
    def swipe_down(self,second):
        time.sleep(1)
        for i in range(int(second/0.1)):
            js = "var q=document.documentElement.scrollTop=" + str(300+200*i)
            self.browser.execute_script(js)
            time.sleep(0.1)
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)
    
    def save_products(self):
        try:
            title = ['id', 'name', 'price', 'sale_num', 'comment']
            with open(self.filename, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=title)
                writer.writeheader()
                writer.writerows(self.products)
        except:
            print('Saving products Failure!')
    
    def main(self):
        self.login()
        pagenum = self.get_pagenum()
        for page in range(pagenum):
            print('Start geting page {} products'.format(page+1))
            self.get_page_item()
            self.swipe_down(2)
            if page == pagenum - 1:
                break
            self.page_next()
        self.save_products()


if __name__ == '__main__':
    brand = 'kisscat'
    tm = TM_products(brand)
    tm.main()
