# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:32:04 2017

@author: kerrydriscoll
"""

import time
import pandas as pd
import numpy as np
import re
import random
import imdb

start_time = time.time()

df = pd.DataFrame(columns=['ID', 'Title', 'Year', 'MPAA', 'Rating', 'Votes'])

i =  imdb.IMDb(accessSystem='http')
#"""
movies = []
for _ in range(100):
    randID = str(random.randint(0, 780505)).zfill(7)
    movies.append(randID)
#"""
#movies = ['0780504']
#movies = ['0053494','0053494','4925292', '0780504', '0377092', '0268126', '0128853', '0050212', '0105435', '5013056', '0074119', '0064253', '0061811', '0112697', '0405094', '1255953', '0046268', '0029593']

for m in movies:
    movie = i.get_movie(m)
    if str(movie)=='':
        continue
    
    kind = movie.get('kind')
    if kind != 'movie':
        continue
    
    language_search = movie.get('language')
    if language_search == None:
        continue
    
    if language_search[0]=="English":
        language = "English"
    else:
        language = "Foriegn"
    
    votes=movie.get('votes')
    if votes == None:
        continue
    
    if (language == "English") and (votes>=1000):
        year=movie.get('year')
        if re.search('USA:(.+?)(:|,|\')',str(movie.get('certification')))!=None:
            mpaa=re.search('USA:(.+?)(:|,|\')',str(movie.get('certification'))).group(1)
    
        rating=movie.get('rating')
    
        df = df.append(pd.DataFrame({'ID': [m], 'Title': [str(movie)], 'Year': [year], 'MPAA': [mpaa], 'Rating':[rating], 'Votes':[votes]}))

df = df.reset_index()    
df['Year']=df['Year'].astype(int)
df['Votes']=df['Votes'].astype(int)
df = df[['ID', 'Title', 'Year', 'MPAA','Rating', 'Votes']]
df = df.sort_values(by=['Rating'], ascending=False)

run_time=time.time() - start_time
print("--- {} seconds ---".format(run_time))
print("--- {} seconds per movie ---".format(run_time/len(movies)))
    
#df = df.sort_values(by=['Year'])

"""
i = imdb.IMDb(accessSystem='http')

movie = i.get_movie('0780504')
i.update(movie, 'vote details')
print(movie.get('median'))
print(movie.get('arithmetic mean'))
print(movie.get('number of votes'))
print(movie.get('demographics'))

from imdb import IMDb
ia = IMDb()
m = ia.get_movie('0780504', 'vote details')
print('median', m.get('median'))
print('arithmetic mean', m.get('arithmetic mean'))
print('number of votes', m.get('number of votes'))
print('demographics', m.get('demographics'))

from imdb import IMDb
ia = IMDb()
m = ia.get_movie('0780504', 'business')
print('budget', m.get('budget'))
print('gross', m.get('gross'))
#i.get_movie_infoset()
"""
#i.update(movie,'business')
#budget = movie.get('budget')
#gross = movie.get('gross')
