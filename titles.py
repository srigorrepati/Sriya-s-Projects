from bs4 import BeautifulSoup
import requests


file = open('marvel_title_refs.txt', 'w')

page = requests.get("https://www.imdb.com/list/ls029032797/")

soup = BeautifulSoup(page.text, 'html.parser')

title_list = soup.body.find_all('div', {'class': 'lister-item'})

for title in title_list:
    ref_url = title.find('a').get('href')
    file.write('%s\n' % ref_url)



