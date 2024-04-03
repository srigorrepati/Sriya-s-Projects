from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
import random


base_url = 'https://www.imdb.com'

with open('marvel_title_refs.txt') as f:
    ref_list = f.readlines()

ref_list = [x.strip() for x in ref_list]

characters = pd.DataFrame(columns=['title', 'character', 'character_alias', 'actor'])

for ref in ref_list:

    credits_page = requests.get(base_url + '/' + ref + 'fullcredits')
    print(base_url + '/' + ref + 'fullcredits')

    soup = BeautifulSoup(credits_page.text, 'html.parser')

    title = soup.body.select_one('div.subpage_title_block__right-column').select_one('a[href*="title"]').text
    print(title)

    # Get cast table
    cast_table = soup.body.find('table', {'class': 'cast_list'})

    cast_members = cast_table.find_all('tr')
    for member in cast_members[1:-1]:
        if member.find('td').get('colspan') is None:
            actor_name = member.find('td', {'class': None}).text.strip()
            actor_roles = member.select_one('td.character').select('a')
            char_name = actor_roles[0].text
            if len(actor_roles) > 1 and 'episode' not in actor_roles[1].text:
                char_alias = actor_roles[1].text
            else:
                char_alias = None
            characters.loc[len(characters.index)] = [title, char_name, char_alias, actor_name]
        else:
            if member.find('td').get('class') is not None:
                break

    characters.to_csv('marvel_characters.csv', index=False)