# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 11:24:44 2017

@author: kerrydriscoll
"""

from pandas import ExcelWriter
from requests import get
from bs4 import BeautifulSoup
import re
import math
from time import time, sleep
from random import randint
from IPython.core.display import clear_output
from warnings import warn



url = "http://www.imdb.com/search/title?num_votes=25000,&title_type=feature&view=simple&sort=num_votes,desc&page=1&ref_=adv_nxt"

response = get(url)
html_soup = BeautifulSoup(response.text, 'html.parser')
type(html_soup)

num_films_text = html_soup.find_all('div', class_ = 'desc')
num_films=re.search('of (\d.+) titles',str(num_films_text[0])).group(1)
num_films=int(num_films.replace(',', ''))
print(num_films)

num_pages = math.ceil(num_films/50)
print(num_pages)

ids = []

start_time = time()
requests = 0

# For every page in the interval 1-4
for page in range(1,num_pages+1):
    
    # Make a get request    
    url = "http://www.imdb.com/search/title?num_votes=25000,&title_type=feature&view=simple&sort=num_votes,desc&page="+str(page)+"&ref_=adv_nxt"
    response = get(url)
    
    # Pause the loop
    sleep(randint(8,15))
    
    # Monitor the requests
    requests += 1
    sleep(randint(1,3))
    elapsed_time = time() - start_time
    print('Request: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    clear_output(wait = True)
    
    # Throw a warning for non-200 status codes
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))
        
    # Break the loop if the number of requests is greater than expected
    if requests > num_pages:
        warn('Number of requests was greater than expected.')  
        break
    
    # Parse the content of the request with BeautifulSoup
    page_html = BeautifulSoup(response.text, 'html.parser')
    
    # Select all the 50 movie containers from a single page
    movie_containers = page_html.find_all('div', class_ = 'lister-item mode-simple')

    # Scrape the ID 
    for i in range(len(movie_containers)):
        id = re.search('tt(\d+)/',str(movie_containers[i].a)).group(1)
        ids.append(id)


print(ids)
print(len(ids))

ids_df = pd.DataFrame({'col':ids})
writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/25000voteIDs.xlsx')
ids_df.to_excel(writer)
writer.save()