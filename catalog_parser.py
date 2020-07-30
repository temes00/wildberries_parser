import requests
import re
import time
import db
from bs4 import BeautifulSoup as BS

urls = [
		'https://www.wildberries.ru/catalog/zhenshchinam', 
		'https://www.wildberries.ru/catalog/muzhchinam',
		'https://www.wildberries.ru/catalog/detyam',
		'https://www.wildberries.ru/catalog/obuv',
		'https://www.wildberries.ru/catalog/aksessuary'
	]

catalogs = {}


url_cnt = 0
insert_cnt = 0
for url in urls:
	url_cnt += 1
	request = requests.get(url)
	html = BS(request.content, 'html.parser')	
	for category in html.select('.i-menu-catalog'):
		level1 = category.select('.maincatalog-list-1 li.name')
		print("LVL1 text = ",level1[0].text," url = ",url," pid = ",0)
		query = (
        	'INSERT INTO catalogs'
        	' (name,url,pid)'
        	' VALUES (%s,%s,%s)')
		db.dbh(query,"do",level1[0].text,url,0)
		insert_cnt += 1
		level2 = category.select('.maincatalog-list-2 li')
		cnt = url_cnt
		for levl2 in level2:
			cnt += 1
			query = (
            	'INSERT INTO catalogs'
            	' (name,url,pid)'
            	' VALUES (%s,%s,%s)')
			db.dbh(query,"do",levl2.a.text,levl2.a.get('href'),url_cnt)
			insert_cnt += 1
			print("LVL2 text = ",levl2.a.text," url = ",levl2.a.get('href')," pid = ",url_cnt)
			for levl3 in levl2.select(".maincatalog-list-3 li"):
				query = (
            		'INSERT INTO catalogs'
            		' (name,url,pid)'
            		' VALUES (%s,%s,%s)')
				db.dbh(query,"do",levl3.a.text,levl3.a.get('href'),cnt)
				print("LVL3 text = ",levl3.a.text," url = ",levl3.a.get('href')," pid = ",cnt)
				insert_cnt += 1
	url_cnt = insert_cnt
		
	time.sleep(10)
