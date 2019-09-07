from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import re
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
def search():
    try:
        browser.get('https://product.pconline.com.cn/cpu/')
        #input = wait.until(
        #    EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        #)
        #submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ksSeach > div > span > input.ksSubmit')))
        #input.send_keys('CPU')
        #submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#Jpager > em > i')))
        get_products()
        return total.text
    except TimeoutError:
        return search()

def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#page-transform-number'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#page-confirm')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#Jpager > span.page-current'), str(page_number)))
        get_products()
    except TimeoutError:
        next_page(page_number)

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#JlistItems')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#JlistItems .item').items()
    for item in items:
        product = {
            'image': item.find('.item-pic .pic').attr('src'),
            'price': item.find('.price').text(),
            'title': item.find('.item-title .item-title-name').text(),
            #'apraisal': items.find('.rela').text(),
        }
        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGO成功', result)
    except Exception:
        print('存储到MONGODB失败', result)

def main():
    total = search()
    total = int(re.compile('(\d+)').search(total).group(1))
    print(total)
    for i in range(2, total + 1):
        next_page(i)
    browser.close()



if __name__ == '__main__':
    main()