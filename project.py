# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:32:04 2017

@author: kerrydriscoll
"""

"""
Step 1:
Install IMDBPy with the following code in terminal
(to ensure you have the most current version):

pip3 install git+https://github.com/alberanid/imdbpy

"""
"""
Import Libraries
"""

from time import time, sleep
import datetime
import pandas as pd
import numpy as np
from pandas import ExcelWriter
import re
from random import randint
from IPython.display import clear_output
import imdb
import sys
from imdb import IMDb, IMDbError



"""
Measure Runtime to Evaluate Code Performance
"""
start_time = time()

"""
connect to IMDb
"""
i =  IMDb(accessSystem='http')

"""
BUILD DEMOGRAPHIC LABELS
Generate framework of demographics to reweigh ratings by later

This code does the following:
1. Access the demoraphics page of a the movie "Silence of the Lambs"
2. Pulls the demographics categories (['male', 'female', 'aged 18 29', ...])
3. Removes IMDb-specific demographic categories that are not of interest 
   (and the redundant 'imdb users' which is the same as the 'Rating' we'll 
   pull from the movie's main page)
4. Sorts the demographic categories to my liking (from general to specific, by age)
5. Generates headers to record the a) rating and b) number of votes for each 
   demographic group

"""
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

"""
CREATE DATAFRAMES to capture relevant info on movies

 - df_initial   will capture the general movie info
 - df           though empty now, will eventually include all the info in 
                df_initial and the demo_list_sub
"""

df_initial = pd.DataFrame(columns=['ID', 'Title', 'Year', 'Language', 'MPAA', 'Rating', 'Votes', 'Top 250 Rank'])
df=pd.DataFrame()

"""
ACCESS MOVIES
NEED TO SELECT WHICH ONE

- option 1: (for code testing) only use "Drive"
- option 2: (for code testing) using a list of movies meet or fail a variety of 
            criteria later in the code (foriegn movies, no MPAA, empty demos)
- option 3: generate random strings of numbers to pull random movies from IMDb
- option 4: IMDb top 250
- option 5: all movies eligible to appear in top 250, a.k.a. feature films with over 25,000 votes
"""

i =  IMDb(accessSystem='http')
##"""
movies = []
#movies = ['0780504']
#movies = ['0053494','0053494','0757180','4925292', '0780504', '0377092', '0268126', '0128853', '0050212', '0105435', '5013056', '0074119', '0064253', '0061811', '0112697', '0405094', '1255953', '0046268', '0029593']
#A24 Titles only
#movies=pd.read_excel('/Users/kerrydriscoll/Desktop/resumes/A24/A24 IDs.xlsx')['IMDb'].tolist()
"""
for _ in range(5521897):
    #randID = str(randint(0, 7221897)).zfill(7)
    randID = str(_).zfill(7)
    movies.append(randID)
"""

for id in i.get_top250_movies():
    movies.append(i.get_imdbID(id))
"""
movies = pd.read_excel('/Users/kerrydriscoll/Documents/imdb project/25000voteIDs.xlsx')['col'].tolist()
for item in range(len(movies)):
    movies[item] = str(movies[item]).zfill(7)
"""
"""
BUILD THE DATAFRAME

1. Gets the movie name
2. Gets the kind of media associated with the string
    - could be 'movie', 'tv series', 'video game', 'short', etc
    - will only keep those classified as 'movie'
3. Determines if the movie is English-language or foriegn
4. Captures the number of votes have been submitted for this film
5. Only continues building dataframe with English language movies and/or with 
   more than 1,000 (or 25,000) votes
6. Captures the year of release
7. Captures the MPAA rating of the film (mostly just for curiosity)
8. The publicly displayed rating of the film
9. Capture general movie info in df_initial
10. Extract the demographic-category-specific (['male', 'female', 'aged 18 29', ...]) 
    rating and number of votes
11. Concatenate together the general movie info and demographic-specific info
    into df
"""
#"""
#loop_time = time()
requests = 0

#"""
for m in movies:
    try:
        movie = i.get_movie(m)
    except IMDbError as err:
      print(err)
    
    #"""
    # Monitor the requests
   # requests += 1
    #sleep(randint(1,3))
    #elapsed_time = time() - loop_time
   # print('Request {}: Loop is {}% complete'.format(requests, (requests/len(movies))*100)
    #clear_output(wait = False)
    #"""
    """  
    if str(movie)=='':
        continue
    
    kind = movie.get('kind')
    if kind != 'movie':
        continue
    """
    language_search = movie.get('language')
    if language_search == None:
        continue
    
    if language_search[0]=="English":
        language = "English"
    else:
        language = "Foriegn, " + language_search[0]
    
    votes=movie.get('votes')
    if votes == None:
        continue
    
    #if (language == "English") and (votes>=1000):
    if votes>=25000:
        year=movie.get('year')
        if re.search('USA:(.+?)(:|,|\')',str(movie.get('certification')))!=None:
            mpaa=re.search('USA:(.+?)(:|,|\')',str(movie.get('certification'))).group(1)
        else:
            mpaa=None
    
        rating=movie.get('rating')
        
        top250 = movie.get('top 250 rank')
        
        df_initial = pd.DataFrame({'ID': [m], 'Title': [str(movie)], 'Year': [year],'Language':[language], 'MPAA': [mpaa], 'Rating':[rating], 'Votes':[votes], 'Top 250 Rank':[top250]})
        df_initial = df_initial[['ID', 'Title', 'Year', 'Language', 'MPAA', 'Rating', 'Votes', 'Top 250 Rank']]
        
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
            
        df_both = pd.concat([df_initial, demo_df], axis=1)
        
        df = df.append(df_both, ignore_index=True)

"""
If all the randomly generated numbers failed to select any movies that meet our
qualifications the code will stop running here
"""      
if df.empty==True:
    print("No qualified movies in randomly generated list")
    sys.exit()
else:
    pass

"""
CLEAN DATAFRAME

- resets the index
- Gets rid of the decimal place (#.0) in the 'Year', 'Votes', and 
  demographic category-specific votes columns
"""
    
df = df.reset_index(drop=True)    
df['Year']=df['Year'].astype(int)
df['Votes']=df['Votes'].astype(int)
votes_cols = [col for col in df.columns if '_votes' in col]
df[votes_cols]=df[votes_cols].astype(int)
df = df.sort_values(by=['Rating'], ascending=False)

"""
IDENTIFIES VOTE DETAILS for IMDb users who
 - identified their gender (male, female)
 - identified their age (under 18, 18-29, 30-44, 45+)
 - are over age 18 (excludes under 18) ... this is because there is inconsistent
   representation over the under-18 category on the site and because they cannot
   see R-rated movies
"""

demo_votes_cols = ['males aged 18 29_votes', 'males aged 30 44_votes','males aged 45 plus_votes', 'females aged 18 29_votes','females aged 30 44_votes', 'females aged 45 plus_votes']

"""
CALCULATE BASE

Sum of the IMDb users listed above:
[ - identified their gender (male, female)
 - identified their age (under 18, 18-29, 30-44, 45+)
 - are over age 18 (excludes under 18) ... this is because there is inconsistent
   representation over the under-18 category on the site and because the cannot
   see R-rated movies]
who voted on the film
"""
df['known total votes >18'] = df[demo_votes_cols].sum(axis=1)
df['Perc Votes studied']=df['known total votes >18']/df['Votes']
df['Perc Votes U.S.']=df['us users_votes']/(df['us users_votes']+df['non us users_votes'])

"""
CALCULATE DEMPGRAHIC COMPOSITION

Generates % of total IMDb votes belong to each demographic category

i.e. 27.4% of voters over age 18 were males aged 18-29
      8.2% of voters over age 18 were females aged 30-44
      ...
"""
for d in demo_votes_cols:
    df['percent_'+str(d)] = df[d]/df['known total votes >18']
    
"""
CREATE WEIGHTS for each Demographic Category to reflect the actual composition
of the United States


U.S. Population Statistics

Percent Composition of the >18 population (249,485,228 people)
According to U.S. Census Bureau 2016 Population Estimates

DEMO               COUNT           PERCENT
----------------------------------------------
MALE    18-29      27,450,678      0.110029272	
MALE    30-44      31,121,027      0.124740961	
MALE    45+        62,898,003      0.252111131
FEMALE  18-29      26,284,017      0.105352999	
FEMALE  30-44      31,135,488      0.124798924
FEMALE  45+        70,596,015      0.282966713
----------------------------------------------
TOTAL             249,485,228      1.000000000


Using our example for before:
i.e. if 27.4% of a movie's voters over age 18 were males aged 18-29
        then weight = 0.4016 = 0.110029272/0.274
        Males age 18-29 are weighted DOWN (0.4016 < 1.0) 
        because they make a SMALLER portion of the Population Base (11.00%) 
        than they do the Voter Base (27.4%)
        
     
     if 8.2% of a movie's voters over age 18 were females aged 30-44
         then weight = 1.5219 = 0.124798924/0.082
         Females age 30-44 are weighted UP (1.5219 > 1.0) 
         because they make a LARGER portion of the Population Base (12.48%)
         than they do the Voter Base (8.2%)

"""

df['weight_males aged 18 29']       = 0.110029272/ df['percent_males aged 18 29_votes'].replace({ 0 : np.nan })
df['weight_males aged 30 44']       = 0.124740961/ df['percent_males aged 30 44_votes'].replace({ 0 : np.nan })
df['weight_males aged 45 plus']     = 0.252111131/ df['percent_males aged 45 plus_votes'].replace({ 0 : np.nan })
df['weight_females aged 18 29']     = 0.105352999/ df['percent_females aged 18 29_votes'].replace({ 0 : np.nan })
df['weight_females aged 30 44']     = 0.124798924/ df['percent_females aged 30 44_votes'].replace({ 0 : np.nan })
df['weight_females aged 45 plus']   = 0.282966713/ df['percent_females aged 45 plus_votes'].replace({ 0 : np.nan })

weight_cols = [col for col in df.columns if 'weight_' in col]


"""
CALCULATE UNWEIGHTED RATING

Necessary because:
- the publicly displayed rating on the movie's main page (df['Rating']) is too 
  general (only has one decimal place)
- the publicly displayed rating takes into account all votes, even those that
  did not identify their age or gender or those under age 18 - since we limited
  our study to voters with these characteristics, our comparison must be limited
  to restricted to voters with these characteristics
"""
df['unweighted rating'] = (df['males aged 18 29_rating']*df['percent_males aged 18 29_votes']) + (df['males aged 30 44_rating']*df['percent_males aged 30 44_votes']) + (df['males aged 45 plus_rating']*df['percent_males aged 45 plus_votes']) + (df['females aged 18 29_rating']*df['percent_females aged 18 29_votes']) + (df['females aged 30 44_rating']*df['percent_females aged 30 44_votes']) + (df['females aged 45 plus_rating']*df['percent_females aged 45 plus_votes'])


"""
CALCULATE WEIGHTED RATING

Apply the weights to the rating of each demographic group to get the new 'unbiased' score
"""
df['weighted rating'] = (df['males aged 18 29_rating']*df['weight_males aged 18 29']*df['percent_males aged 18 29_votes']) + (df['males aged 30 44_rating']*df['weight_males aged 30 44']*df['percent_males aged 30 44_votes']) + (df['males aged 45 plus_rating']*df['weight_males aged 45 plus']*df['percent_males aged 45 plus_votes']) + (df['females aged 18 29_rating']*df['weight_females aged 18 29']*df['percent_females aged 18 29_votes']) + (df['females aged 30 44_rating']*df['weight_females aged 30 44']*df['percent_females aged 30 44_votes']) + (df['females aged 45 plus_rating']*df['weight_females aged 45 plus']*df['percent_females aged 45 plus_votes'])


"""
MEASURE THE DIFFERENCE 
between the Unweighted and Weighted Score

Determine which film's reputation (unweighted score) differs the most 
from it's actual enjoyment



Difference > 0.0  POS   Film is MORE liked than IMDb suggests
Difference < 0.0  NEG   Film is LESS liked than IMDb suggests

"""
df['difference'] = df['weighted rating']-df['unweighted rating']
df = df.sort_values(by='difference', ascending=False)

#df['abs_difference']= abs(df['difference'])
#df = df.sort_values(by='abs_difference', ascending=False)

"""
Print the essential info from the dataframe
"""

print(df[['Title', 'Year', 'Language','Votes', 'Rating','unweighted rating', 'weighted rating', 'difference']])

"""
MEASURE DIFFERENCE IN RANK

See how the reweighting affects the order of scores (particularly for the top 250)
"""

df['unweighted rank']=df['unweighted rating'].rank(ascending=0).astype(int)
df['weighted rank']=df['weighted rating'].rank(ascending=0).astype(int)
df['rank difference'] = df['unweighted rank']-df['weighted rank']

df = df.sort_values(by='rank difference', ascending=False)
print(df.head(10)[['Title', 'Year', 'Language','Votes','Rating','Top 250 Rank','unweighted rating', 'weighted rating', 'difference', 'unweighted rank', 'weighted rank', 'rank difference']])
print(df.tail(10)[['Title', 'Year', 'Language', 'Votes','Rating','Top 250 Rank','unweighted rating', 'weighted rating', 'difference', 'unweighted rank', 'weighted rank', 'rank difference']])

df = df.sort_values(by='weighted rank', ascending=True)
print(df[['Title', 'Year','Language', 'Votes','Rating','Top 250 Rank', 'unweighted rating', 'weighted rating', 'difference', 'unweighted rank', 'weighted rank', 'rank difference']])


writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/Reweighted250_{}.xlsx'.format(datetime.datetime.now().strftime("%m-%d_%H-%M")))
df.to_excel(writer)
writer.save()

"""
Measure Runtime to Evaluate Code Performance
"""
run_time=time() - start_time
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
