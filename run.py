import requests
import logging
import re
import time
import math

from bs4 import BeautifulSoup as BS
from threading import Thread

import db
import settings as const

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger('wb')

class Client(object):
	def __init__(self):
		# self.session = requests.Session()
		# self.headers = {
		# 	'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
		# }
		self.params = {} 

	def load_page( self , url: str):
		time.sleep(const.CATALOGS_GET_TIMEOUT)
		# res = self.session.get(url=url)
		res = requests.get(url=const.SITE_URL + url)
		res.raise_for_status()
		return res.text

	def load_product_page( self , url: str):
		time.sleep(const.PRODUCTS_CART_GET_TIMEOUT)
		# res = self.session.get(url=url)
		res = requests.get(url=url)
		res.raise_for_status()
		return res.text

	def parse_catalog_page( self, text: str , catalog_url: str):
		html = BS(text, 'lxml')
		for product in html.select('div.j-products-container'):
			links = product.select('a.ref_goods_n_p')
			for link in links[:const.GET_PRODUCT_ON_PAGE]:
				product_check = self.check_product(url=link.get('href'))
				if not product_check:
					logger.info("Alredy exists " + str(link.get('href')))
					logger.info(product_check)
				else:
					self.parse_block(url=link.get('href'), catalog_url = catalog_url)

	
	def parse_block( self, url: str, catalog_url: str):
		logger.info(url)
		logger.info('=' * 100)
		product = self.load_product_page(url = url)
		self.save_product_info(catalog= str(catalog_url), url=str(url), status="Ok")
		self.parse_product_page(text = product)

	def parse_product_page( self, text: str ):
		html = BS(text, 'lxml')
		for param in html.select('div.pp'):
			tag = re.search(r'b>(.*)<\/b.*n>(.*)<\/s',str(param))
			tag_name = tag.group(1)
			tag_value = tag.group(2).strip()
			self.save_tags_info(name = str(tag_name), value = str(tag_value))
	
	#Save process
	def save_to_file(self, name: str, text: str):
		with open(name, 'w', encoding='utf-8') as file:
			file.write(text)

	def save_product_info(self, catalog: str, url: str, status: str):
		query = (
        	'INSERT INTO products'
        	' (catalog,url,status)'
        	' VALUES (%s,%s,%s)')
		db.dbh(query,"do",str(catalog),str(url),str(status))

	def check_product(self, url: str):
		query = (
        	'SELECT * FROM products'
        	' WHERE url = %s;')
		response = db.dbh(query,"query",url)
		logger.info(response)
		if len(response):
			return 0
		return 1

	def get_catalogs(self):
		query = (
        	'SELECT c.*, t.c as amount FROM catalogs c'
        	' LEFT JOIN ( SELECT catalog, count(id) as c FROM products GROUP BY catalog) as t ON t.catalog = c.url '
			' WHERE pid > 0 '
			' AND id NOT IN (SELECT pid FROM catalogs) AND ( t.c < 1000 OR t.c IS NULL ) ')
		response = db.dbh(query,"query")
		return response

	def save_tags_info(self, name: str, value: str):
		query = (
        	'INSERT INTO tags'
        	' (name,value)'
        	' VALUES (%s,%s) ON DUPLICATE KEY UPDATE updated=NOW() ')
		db.dbh(query,"do",name,value)

	def run(self, event):
		catalogs = self.get_catalogs()
		if event:
			if event == "even":
				catalogs = [ item for item in catalogs if not int(item['id']) % 2 ]
			elif event == "odd":
				catalogs = [ item for item in catalogs if not ( int(item['id']) - 1 ) % 2 ]
		for catalog in catalogs:
			text = self.load_page(url = catalog['url'])
			html = BS(text, 'lxml')
			goods_amount = html.select('span.goods-count')
			goods_amount = re.search(r'([0-9]+)',str(goods_amount[0].text))
			goods_amount = goods_amount.group(1)
			pages = int(goods_amount) / const.ALL_PRODUCT_ON_PAGE
			pages = math.ceil(pages)
			if pages > const.PAGE_LIMIT:
				pages = const.PAGE_LIMIT
			self.parse_catalog_page(text = text, catalog_url = catalog['url'])
			if const.PAGER_PARSE:
				for page in range(2,int(pages)):
					self.run_parse_pager(catalog_url = catalog['url'], page = page)

	def run_parse_pager(self, catalog_url: str, page: int = 0):
		url = str(catalog_url) + "?page=" + str(page)
		text = self.load_page(url = url)
		self.parse_catalog_page(text = text, catalog_url = url)


if __name__ == '__main__':
	parser1 = Client()
	parser2 = Client()

	thread1 = Thread(target=parser1.run, args=('even',), daemon=True)
	thread2 = Thread(target=parser2.run, args=('odd',), daemon=True)
		
	thread1.start()
	thread2.start()

	thread1.join()
	thread2.join()