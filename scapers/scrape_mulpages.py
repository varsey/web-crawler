import requests
from bs4 import BeautifulSoup

URL = 'https://scrapingclub.com/exercise/list_basic/?page=1'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'lxml')
items = soup.find_all('div', class_='col-lg-4 col-md-6 mb-4')

count = 1
for i in items:
    item_name = i.find('h4', class_='card-title').text.strip('\n')
    item_price = i.find('h5').text
    print('%s ) Price: %s, Item Name: %s' % (count, item_price, item_name))
    count = count + 1

pages = soup.find('ul', class_='pagination')

urls = []
links = pages.find_all('a', class_='page-link')
for link in links:
    page_num = int(link.text) if link.text.isdigit() else None
    if page_num is not None:
        x = link.get('href')
        urls.append(x)
print(urls)

count = 1
for i in urls:
    new_url = URL[:-1] + i
    response = requests.get(new_url)
    soup = BeautifulSoup(response.text, 'lxml')
    items = soup.find_all('div', class_='col-lg-4 col-md-6 mb-4')

    for i in items:
        item_name = i.find('h4', class_='card-title').text.strip('\n')
        item_price = i.find('h5').text
        print('%s ) Price: %s, Item Name: %s' % (count, item_price, item_name))
        count = count + 1
