from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
import random


base_url = 'https://www.imdb.com'

with open('marvel_title_refs.txt') as f:
    ref_list = f.readlines()

ref_list = [x.strip() for x in ref_list]

title_info = pd.DataFrame(columns=['title', 'type', 'release_year', 'release_month', 'release_day', 'rating', 'length', 'stars', 'genres'])
characters = pd.DataFrame(columns=['title', 'character', 'character_alias', 'actor'])

for ref in ref_list[:-1]:
    title_page = requests.get(base_url + ref)

    print(base_url + '/' + ref)

    #credits_page = requests.get(base_url + '/' + ref_list[0] + 'fullcredits')

    soup = BeautifulSoup(title_page.text, 'html.parser')

    # Get movie/show title
    title = soup.body.find('h1', {'data-testid': 'hero-title-block__title'}).text

    length = None
    rating = None

    # Get release date info
    #release_date = soup.body.find('a', {'href': ref_list[0] + 'releaseinfo?ref_=tt_dt_rdat', 'class': lambda x: 'ipc-metadata-list-item__list-content-item' in x}).text
    list_items = soup.body.select('a.ipc-metadata-list-item__list-content-item')
    for item in list_items:
        if 'releaseinfo' in item.get('href'):
            release_date = item.text
            break
    #print(soup.body.select('a.ipc-metadata-list-item__list-content-item+[href*=title]'))
    release_date = release_date.split('(')[0]
    release_year = release_date.split(',')[1].strip()
    release_month = release_date.split(',')[0].split(' ')[0].strip()
    release_day = release_date.split(',')[0].split(' ')[1].strip()

    # Get header container for movie rating and length
    header_lines = soup.find('div', {'class': 'sc-80d4314-2 iJtmbR'}).find_all('li')
    for line in header_lines:
        if line.a is not None:
            if line.a.get('href') is not None:
                if 'parentalguide' in line.a.get('href'):
                    rating = line.span.text
        if ('m' in line.text or 'h' in line.text) and line.text[0].isdigit():
            length = line.text
            # Convert hour/min format to minutes
            if len(length.split(' ')) > 1:
                hours = length.split(' ')[0][:-1]
                minutes = length.split(' ')[1][:-1]
            else:
                hours = 0
                minutes = length[:-1]

            length = int(minutes) + 60 * int(hours)
    # Get star rating
    stars = soup.body.find('div', {'class': 'sc-7ab21ed2-2 kYEdvH'}).text
    stars = stars.split('/')[0]

    # Get genres
    genres = []
    genre_buttons = soup.body.find_all('a', {'class': 'sc-16ede01-3 bYNgQ ipc-chip ipc-chip--on-baseAlt'})
    for genre in genre_buttons:
        genres.append(genre.text)

    # Determine type of content
    content_type = None
    # If there is a 'TV Series' label at the top of the page, it's a TV series
    if 'TV' in header_lines[0].text:
        content_type = 'TV Series'
    # If there is box office information, its a movie
    if soup.body.find('section', {'cel_widget_id': 'StaticFeature_BoxOffice'}) is not None:
        content_type = 'Movie'
    # Otherwise, it's a short
    if content_type is None:
        content_type = 'Short'

    title_info.loc[len(title_info.index)] = [title, content_type, release_year, release_month, release_day, rating, length, stars, str(genres)]
print(title_info)

title_info.to_csv('marvel_titles.csv', index=False)

print(base_url + ref_list[0])