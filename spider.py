from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import re
import time
from config import *
import pymongo
import requests

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#listing-4col .inner_blank .artbox')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#listing-4col .inner_blank .artbox').items()
    for item in items:
        product = {
            'title': item.find('.producttitles .ProductTitle').text(),
            'price': item.find('.price').text(),
        }
        print(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("存储到MONGODB成功", result)
    except Exception:
        print("存储到MONGODB失败", result)



def next_page(page_number):
    try:
        goods = 'motherboards'
        start_url = 'https://www.overclockers.co.uk/pc-components/' + goods
        url = start_url + '?p=' + str(page_number)
        browser.get(url)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#categoryListingActionsBottom > div > div > div > a.navi.on'), str(page_number)))
        get_products()
    except TimeoutError:
        next_page(page_number)

def main():
    for i in range(1, 9):
        next_page(i)
    browser.close()

if __name__ == '__main__':
    main()