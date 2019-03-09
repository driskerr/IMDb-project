# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 11:24:44 2017

@author: kerrydriscoll
"""
import pandas as pd
from matplotlib import pyplot as plt
from pandas import ExcelWriter
from requests import get
from bs4 import BeautifulSoup
import re
import math
from time import time, sleep
from random import randint
from IPython.core.display import clear_output
from warnings import warn


##Define Search Criteria

#criteria_votes=range(5,1897441,10)
criteria_votes=range(2000,60000,1000)
"""
include_votes = input("Limit search by Number of Votes? (Y/N) \n")
if include_votes.upper() == "Y":
    criteria_votes = "&num_votes="+input("Minimum number of votes: \n")+","
else:
    criteria_votes=""
    
include_language = input("Limit search by Language? (Y/N) \n")
if include_language.upper() == "Y":
    criteria_language = "&primary_language="+input("Language Spoken: \n English=en \n French=fr \n German=de \n Chinese=zh \n Mandarin=cmn \n Hindi=hi \n Greek=el \n Italian=it \n Arabic=ar \n Japanese=ja \n Korean=ko \n Persian=fa \n Panjabi=pj \n Portuguese=pt \n Russian=ru \n Spanish=es \n Swedish=sv \n Turkish=tr \n ")
else:
    criteria_language=""
    """
language_key = pd.read_excel(r'/Users/kerrydriscoll/Documents/imdb project/language abbreviations.xlsx', sheetname=0)
criteria_language=language_key.Abbreviation.tolist()
criteria_language.append("")
#criteria_language=["", "en", "ar", "bg"]
"""    
include_release_date = input("Limit search by Release Date? (Y/N) \n")
if include_release_date.upper() == "Y":
    criteria_release_date = "&release_date="+input("Date year/range: \n (format 'YYYY' or 'YYY1,YYY2') \n")
else:
"""    
#criteria_release_date=range(1898,2019)
criteria_release_date=range(1914,2018)
#criteria_release_date=""
"""
include_country = input("Limit search by Country of Origin? (Y/N) \n")
if include_country.upper() == "Y":
    criteria_country = "&country_of_origin="+input("Country of Origin: \n United States=us \n United Kingdom=gb \n Australia=au \n Brazil=br \n Canada=ca \n China=cn \n France=fr \n Germany=de \n Greece=gr \n Hong Kong=hk \n India=in \n Iran=ir \n Ireland=ie \n Italy=it \n Japan=jp \n Mexico=mx \n Pakistan=pk \n Russia=ru \n Spain=es \n Sweden=se \n South Africa=za \n South Korea=kr \n Switzerland=ch \n Thailand=th \n")
else:
"""    
criteria_country=""
"""
print(criteria_votes)
print(criteria_language)
print(criteria_release_date)
print(criteria_country)
"""
language_popularity_df= pd.DataFrame({}, columns= ['Min_Votes','Max_Votes', 'Year', 'English/Foriegn', 'Num_of_Films'])

for i in criteria_votes:
    for lang in criteria_language:
        for y in criteria_release_date:
            url = "http://www.imdb.com/search/title?count=250"+criteria_country+"&primary_language="+lang+"&num_votes="+str(i)+","+str(i+1000)+"&release_date="+str(y)+"&title_type=feature&view=simple&sort=num_votes,desc&page=1&ref_=adv_nxt"
            #print(url)
            response = get(url)
            html_soup = BeautifulSoup(response.text, 'html.parser')
            type(html_soup)

            num_films_text = html_soup.find_all('div', class_ = 'desc')
            if isinstance(num_films_text, int):
                num_films = num_films_text
            elif not num_films_text:
                num_films = 0
            elif isinstance(num_films_text, int) == False:
                num_films=re.search('(\d.+|\d+) title',str(num_films_text[0])).group(1)
                num_films=int(num_films.replace(',', ''))
        
        
            if lang == "":
                language_popularity_df = language_popularity_df.append({'Min_Votes': i,'Max_Votes': i+1000,'Year':y, 'English/Foriegn': 'All', 'Num_of_Films': num_films}, ignore_index=True)
            else:
                language_popularity_df = language_popularity_df.append({'Min_Votes': i,'Max_Votes': i+1000,'Year':y, 'English/Foriegn': language_key[language_key.Abbreviation==lang].Language.tolist()[0], 'Num_of_Films': num_films}, ignore_index=True)

            
language_popularity_df.Min_Votes = language_popularity_df.Min_Votes.astype(int)
language_popularity_df.Max_Votes = language_popularity_df.Max_Votes.astype(int)
language_popularity_df.Year = language_popularity_df.Year.astype(int)
language_popularity_df.Num_of_Films = language_popularity_df.Num_of_Films.astype(int)

language_popularity_pivot= language_popularity_df.pivot(
	columns = 'English/Foriegn',
	index = 'Min_Votes',
	values = 'Num_of_Films').reset_index()
 
year_popularity_pivot= language_popularity_df.groupby('English/Foriegn').pivot(
	columns = 'Min_Votes',
	index = 'Year',
	values = 'Num_of_Films').reset_index()
 
language_popularity_pivot['Perc_Eng']=100*(language_popularity_pivot.English/language_popularity_pivot.All)
language_popularity_pivot=language_popularity_pivot.round({'Perc_Eng':2})

print(language_popularity_pivot)
print(year_popularity_pivot)

plt.plot(language_popularity_pivot.Min_Votes, language_popularity_pivot.Perc_Eng, 'o')
plt.show()

plt.plot(language_popularity_pivot.Min_Votes, language_popularity_pivot.All, 'o')
plt.show()

#writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/language_analysis.xlsx')
#language_popularity_pivot.to_excel(writer)
#writer.save()

#num_pages = math.ceil(num_films/250)
#print(num_pages)
"""
ids = []

start_time = time()
requests = 0

# For every page in the interval
for page in range(1,num_pages+1):
    
    # Make a get request    
    url = "http://www.imdb.com/search/title?count=250"+criteria_country+criteria_language+criteria_votes+criteria_release_date+"&title_type=feature&view=simple&sort=user_rating,desc&page="+str(page)+"&ref_=adv_nxt"
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
print(len(ids)==num_films)

ids_df = pd.DataFrame({'col':ids})
writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/'+criteria_country+criteria_language+criteria_votes+criteria_release_date+'IDs.xlsx')
#writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/25000voteIDs.xlsx')
ids_df.to_excel(writer)
writer.save()
"""
