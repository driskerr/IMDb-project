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
from imdb import IMDb


start_time = time.time()

i =  IMDb(accessSystem='http')

demo_list=[]
demo_list_sub=[]
demos=i.get_movie('0780504','vote details').get('demographics')
for d in demos:
    demo_list.append(d)
demo_list.remove('imdb staff')
demo_list.remove('top 1000 voters')
demo_list.remove('imdb users')
demo_list = sorted(demo_list)
myorder = [9, 4, 3, 0, 1, 2, 15, 14, 13, 10, 11, 12, 8, 5, 6, 7]
demo_list = [demo_list[i] for i in myorder]
for d in demo_list:
    demo_list_sub.append(str(d)+'_rating')
    demo_list_sub.append(str(d)+'_votes')


df=pd.DataFrame()
df_initial = pd.DataFrame(columns=['ID', 'Title', 'Year', 'MPAA', 'Rating', 'Votes'])

i =  IMDb(accessSystem='http')
"""
movies = []
for _ in range(100):
    randID = str(random.randint(0, 780505)).zfill(7)
    movies.append(randID)
"""
#movies = ['0780504']
movies = ['0053494','0053494','4925292', '0780504', '0377092', '0268126', '0128853', '0050212', '0105435', '5013056', '0074119', '0064253', '0061811', '0112697', '0405094', '1255953', '0046268', '0029593']

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
        
        demographics=i.get_movie(m,'vote details').get('demographics')
        demo_dict={}
        for d in demo_list:
            if d in demographics:
                demo_dict[str(d)+'_rating'] = demographics[d]['rating']
                demo_dict[str(d)+'_votes']= demographics[d]['votes']
            elif d not in demographics:
                demo_dict[str(d)+'_rating'] = None
                demo_dict[str(d)+'_votes']= 0
        
        demo_df=pd.DataFrame.from_dict(demo_dict, orient='index')
        demo_df=demo_df.T
        demo_df=demo_df[demo_list_sub]        
    
        df_initial = pd.DataFrame({'ID': [m], 'Title': [str(movie)], 'Year': [year], 'MPAA': [mpaa], 'Rating':[rating], 'Votes':[votes]})
        df_initial = df_initial[['ID', 'Title', 'Year', 'MPAA','Rating', 'Votes']]        
        df_both = pd.concat([df_initial, demo_df], axis=1)
        
        df = df.append(df_both, ignore_index=True)
    
df = df.reset_index(drop=True)    
df['Year']=df['Year'].astype(int)
df['Votes']=df['Votes'].astype(int)
votes_cols = [col for col in df.columns if '_votes' in col]
df[votes_cols]=df[votes_cols].astype(int)
df = df.sort_values(by=['Rating'], ascending=False)

demo_votes_cols = ['males aged 18 29_votes', 'males aged 30 44_votes','males aged 45 plus_votes', 'females aged 18 29_votes','females aged 30 44_votes', 'females aged 45 plus_votes']

df['known total votes >18'] = df[demo_votes_cols].sum(axis=1)

for d in demo_votes_cols:
    df['percent_'+str(d)] = df[d]/df['known total votes >18']
    
"""
U.S. Population Statistics

Percent Composition of the >18 population (249,485,228 people)
According to U.S. Census Bureau 2016 Population Estimates

DEMO            COUNT           PERCENT
MALE 18-29      27,450,678      0.110029272	
MALE 30-44      31,121,027      0.124740961	
MALE 45+        62,898,003      0.252111131
FEMALE 18-29    26,284,017      0.105352999	
FEMALE 30-44    31,135,488      0.124798924
FEMALE 45+      70,596,015      0.282966713
TOTAL           249,485,228     1.000000000
"""

df['weight_males aged 18 29']       = 0.110029272/ df['percent_males aged 18 29_votes']
df['weight_males aged 30 44']       = 0.124740961/ df['percent_males aged 30 44_votes']
df['weight_males aged 45 plus']     = 0.252111131/ df['percent_males aged 45 plus_votes']
df['weight_females aged 18 29']     = 0.105352999/ df['percent_females aged 18 29_votes']
df['weight_females aged 30 44']     = 0.124798924/ df['percent_females aged 30 44_votes']
df['weight_females aged 45 plus']   = 0.282966713/ df['percent_females aged 45 plus_votes']

df['unweighted rating'] = (df['males aged 18 29_rating']*df['percent_males aged 18 29_votes']) + (df['males aged 30 44_rating']*df['percent_males aged 30 44_votes']) + (df['males aged 45 plus_rating']*df['percent_males aged 45 plus_votes']) + (df['females aged 18 29_rating']*df['percent_females aged 18 29_votes']) + (df['females aged 30 44_rating']*df['percent_females aged 30 44_votes']) + (df['females aged 45 plus_rating']*df['percent_females aged 45 plus_votes'])
df['weighted rating'] = (df['males aged 18 29_rating']*df['weight_males aged 18 29']*df['percent_males aged 18 29_votes']) + (df['males aged 30 44_rating']*df['weight_males aged 30 44']*df['percent_males aged 30 44_votes']) + (df['males aged 45 plus_rating']*df['weight_males aged 45 plus']*df['percent_males aged 45 plus_votes']) + (df['females aged 18 29_rating']*df['weight_females aged 18 29']*df['percent_females aged 18 29_votes']) + (df['females aged 30 44_rating']*df['weight_females aged 30 44']*df['percent_females aged 30 44_votes']) + (df['females aged 45 plus_rating']*df['weight_females aged 45 plus']*df['percent_females aged 45 plus_votes'])

df['difference'] = df['new rating']-df['unweighted rating']
df['abs_difference']= abs(df['difference'])

#df = df.sort_values(by='abs_difference', ascending=False)
df = df.sort_values(by='difference', ascending=False)
df[['Title', 'Year', 'Votes','Rating','unweighted rating', 'weighted rating', 'difference']]

run_time=time.time() - start_time
print("--- {} seconds ---".format(run_time))
print("--- {} seconds per movie ---".format(run_time/len(movies)))
    
#df = df.sort_values(by=['Year'])


"""
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
