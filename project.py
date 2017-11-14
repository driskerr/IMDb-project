# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:32:04 2017

@author: kerrydriscoll
"""

import pandas as pd
import numpy as np
import re
import imdb

df = pd.DataFrame(columns=['ID', 'Title', 'Year', 'MPAA', 'Rating', 'Votes'])

i =  imdb.IMDb(accessSystem='http')

movies = ['4925292', '0780504', '0377092', '0268126', '0128853', '0050212', '0105435', '5013056', '0074119', '0064253', '0061811', '0112697']
for m in movies:
    movie = i.get_movie(m)
    
    year=movie.get('year')
    mpaa=re.search('USA:(.+?)(:|,|\')',str(movie.get('certification'))).group(1)
    
    rating=movie.get('rating')
    votes=movie.get('votes')
    
    df = df.append(pd.DataFrame({'ID': [m], 'Title': [str(movie)], 'Year': [year], 'MPAA': [mpaa], 'Rating':[rating], 'Votes':[votes]}))

df = df.reset_index()    
df['Year']=df['Year'].astype(int)
df['Votes']=df['Votes'].astype(int)
df = df[['ID', 'Title', 'Year', 'MPAA', 'Rating', 'Votes']]
df = df.sort_values(by=['Rating'], ascending=False)
#df = df.sort_values(by=['Year'])
    
#votes = i.get_movie_vote_details('0780504')
#print(votes)
    
#i.update(movie, 'vote details')
#print(movie.get('mean and median')

#i.get_movie_infoset()

#i.update(movie,'business')
#budget = movie.get('budget')
#gross = movie.get('gross')
