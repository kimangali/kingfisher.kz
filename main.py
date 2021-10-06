import requests
from bs4 import BeautifulSoup as BS 
from urllib.parse import quote_plus
from tqdm import tqdm
import numpy as np
import json

headers = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
}

def get_data(cities, categories):
	products = [['title', 'category', 'price', 'city', 'available']]

	for city in tqdm(cities):
		for category in tqdm(categories, leave=False):
			#constructing link
			link = domen + categories[category]
			
			req_link = requests.post(link, cookies={'city_select': cities[city]})
			html = BS(req_link.text, 'lxml')
		
			goods = html.find_all('div', class_='goodsBlock')

			for good in goods:
				title = good.select('a.title>span')[0].get_text(strip=True)
				price = int(''.join([s for s in good.select('span.price>span.new')[0].get_text(strip=True).split() if s.isdigit()]))
				available = 'В наличии'
				try:
					available = good.select('span.wrapperNone>span')[0].get_text(strip=True)
				except:
					pass	

				products.append(["'"+title+"'", category, price, city, available])

	#saving as csv
	np.savetxt("products.csv", 
			   products,
			   delimiter =", ", 
			   fmt ='% s')

	#saving to json
	products_dict = []
	for i in products[1:]:
		products_dict.append({'title': i[0], 'category': i[1], 'price': i[2], 'city': i[3], 'available': i[4]})
	with open('products.json', 'w') as file:
		json.dump(products_dict, file, indent = 6, ensure_ascii=False)


def main():
	req_link = requests.get(domen)
	html = BS(req_link.content, 'lxml')

	categories = {submenu.find('span').get_text(strip=True): submenu.find('a')['href'].split('/')[1]  for submenu in html.find('ul', class_='topMenu').find_all('li', class_='dropmenu')}
	cities = {li.find_all('a')[0].get_text(strip=True): li.find_all('a')[0]['href'] for li in html.find('ul', class_='switchCity').find_all('li')}
	
	session = requests.session()
	for city in cities:
		link = 'https://kingfisher.kz' + cities[city]
		session.get(link)
		cities[city] = session.cookies['city_select']

	#parsing data
	get_data(cities, categories)


if __name__ == '__main__':

	domen = 'https://kingfisher.kz/'

	main()
