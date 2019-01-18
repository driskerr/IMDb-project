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
import sys
from imdb import IMDb, IMDbError
from ipfn import ipfn

pd.set_option('display.max_columns', 20)

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
#demo_list.remove('imdb staff')
demo_list.remove('top 1000 voters')
demo_list.remove('imdb users')
demo_list.remove('us users')
demo_list.remove('non us users')
demo_list.remove('males aged under 18')
demo_list.remove('females aged under 18')
demo_list.remove('aged under 18')
for d in demo_list:
    demo_list_sub.append(str(d)+'_rating')
    demo_list_sub.append(str(d)+'_votes')
    
"""
IDENTIFIES VOTE DETAILS for IMDb users who
 - identified their gender (male, female)
 - identified their age (under 18, 18-29, 30-44, 45+)
 - are over age 18 (excludes under 18) ... this is because there is inconsistent
   representation over the under-18 category on the site and because they cannot
   see R-rated movies
"""

demo_votes_cols = [col for col in demo_list_sub if '_votes' in col]

"""
CREATE WEIGHTS for each Demographic Category to reflect the actual composition
of the United States


U.S. Population Statistics

Percent Composition of the >18 population (247,403,128 people)
According to U.S. Census Bureau 2017 Population Estimates

-"AGE AND SEX  more information 2013-2017 American Community Survey 5-Year Estimates"
-https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml?src=CF


DEMO               COUNT           PERCENT
--------------------------------------------
MALE          120,408,314        0.486688729  	
FEMALE        126,994,814        0.513311271  	
--------------------------------------------
TOTAL         247,403,128        1.000000000


DEMO            COUNT           PERCENT
----------------------------------------------
 18-29      53,538,402        0.216401476  	
 30-44      62,293,674        0.251790163  	
 45+       131,571,052        0.531808361  
----------------------------------------------
TOTAL      247,403,128        1.000000000



DEMO               COUNT           PERCENT
----------------------------------------------
MALE    18-29      27,346,977       0.110536100 	
MALE    30-44      31,121,285       0.125791801 	
MALE    45+        62,898,003       0.250360828 
FEMALE  18-29      26,191,425       0.105865375 	
FEMALE  30-44      31,172,389       0.125998362 
FEMALE  45+        69,631,000       0.281447533 
----------------------------------------------
TOTAL             247,403,128       1.000000000


Using our example for before:
i.e. if 27.4% of a movie's voters over age 18 were males aged 18-29
        then weight = 0.403 = 0.110536100/0.274
        Males age 18-29 are weighted DOWN (0.403 < 1.0) 
        because they make a SMALLER portion of the Population Base (11.05%) 
        than they do the Voter Base (27.4%)
        
     
     if 8.2% of a movie's voters over age 18 were females aged 30-44
         then weight = 1.5366 = 0.125998362/0.082
         Females age 30-44 are weighted UP (1.5366 > 1.0) 
         because they make a LARGER portion of the Population Base (12.60%)
         than they do the Voter Base (8.2%)

"""

us_targets = pd.read_csv(r'/Users/kerrydriscoll/Documents/imdb project/ACS_demos.csv')
age_target = us_targets.groupby('age')['percent'].sum()
gender_target = us_targets.groupby('gender')['percent'].sum()

gender_dict = {'males': 0, 'females': 1}
age_dict = {'18 29': 1, '30 44': 2, '45 plus': 3}

age_target.index = age_target.index.map(age_dict)
gender_target.index = gender_target.index.map(gender_dict)
us_targets['gender'] = us_targets['gender'].map(gender_dict)
us_targets['age'] = us_targets['age'].map(age_dict)
us_targets.rename(columns = {'percent': 'percent_census'}, inplace=True)


"""
CREATE DATAFRAMES to capture relevant info on movies

 - df_initial   will capture the general movie info
 - df           though empty now, will eventually include all the info in 
                df_initial and the demo_list_sub
"""

df_initial = pd.DataFrame(columns=['ID', 'Title', 'Year', 'Language', 'Genre', 'MPAA', 'Rating', 'Votes', 'Top 250 Rank'])
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
"""
for id in i.get_top250_movies():
    movies.append(i.get_imdbID(id))
"""    
#"""
movies = pd.read_excel('/Users/kerrydriscoll/Documents/imdb project/25000voteIDs_{}.xlsx'.format(datetime.datetime.now().strftime("%m-%d")))['col'].tolist()
for item in range(len(movies)):
    movies[item] = str(movies[item]).zfill(7)
#"""
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
    
    genre=movie.get('genre')
    if genre == None:
        continue
    
    
    #if (language == "English") and (votes>=1000):
    if votes>=25000:
        year=movie.get('year')
        if re.search('United States:(.+?)(:|,|\')',str(movie.get('certification')))!=None:
            #mpaa=re.search('United States:(.+?)(:|,|\')',str(movie.get('certification'))).group(1)
            mpaa=[ratings[0] for ratings in re.findall('United States:(.+?)(:|,|\')',str(movie.get('certification'))) if 'TV' not in ratings[0]]
        else:
            mpaa=None
    
        rating=movie.get('rating')
        
        top250 = movie.get('top 250 rank')
        
        df_initial = pd.DataFrame({'ID': [m], 'Title': [str(movie)], 'Year': [year],'Language':[language], 'Genre': [", ".join(genre) if genre is not None else genre], 'MPAA': [", ".join(mpaa) if mpaa is not None else mpaa], 'Rating':[rating], 'Votes':[votes], 'Top 250 Rank':[top250]})
        df_initial = df_initial[['ID', 'Title', 'Year', 'Language','Genre','MPAA', 'Rating', 'Votes', 'Top 250 Rank']]
        
        demographics=i.get_movie(m,'vote details').get('demographics')
        demo_clean = pd.DataFrame(demographics)[demo_list]
        
        demo_dict={}
        for d in demo_list:
            if d in demographics:
                demo_dict[str(d)+'_rating'] = demo_clean[d]['rating']
                demo_dict[str(d)+'_votes']= demo_clean[d]['votes']
            elif d not in demographics:
                demo_dict[str(d)+'_rating'] = None
                demo_dict[str(d)+'_votes']= 0
                
        demo_df=pd.DataFrame.from_dict(demo_dict, orient='index').T
        
        demo_clean = demo_clean.T
        demo_clean.reset_index(inplace=True)
        
        demo_clean['gender'] = demo_clean['index'].apply(lambda x: x.split('aged')[0].strip())
        demo_clean['age'] = demo_clean['index'].apply(lambda x: x.split('aged')[1].strip() if len(x.split('aged')) > 1 else '')
        
        demo_clean = demo_clean[['gender', 'age', 'rating', 'votes']]
        demo_clean = demo_clean[(demo_clean['gender']!='') & (demo_clean['age']!='')].reset_index(drop=True)
        demo_clean['percent_original'] = demo_clean['votes'].apply(lambda x: x/demo_clean['votes'].sum())
        demo_clean['percent_infp'] = demo_clean['percent_original']
        
        demo_clean['age'] = demo_clean['age'].map(age_dict)
        demo_clean['gender'] = demo_clean['gender'].map(gender_dict)
        demo_clean = pd.merge(demo_clean, us_targets[['gender', 'age', 'percent_census']], on = ['gender', 'age'])
        
        ipfn_df = ipfn.ipfn(demo_clean, [age_target, gender_target], [['age'], ['gender']], weight_col = 'percent_infp')
        demo_final = ipfn_df.iteration()
        
        rating_unweighted = demo_final['rating'].dot(demo_final['percent_original'])
        rating_infp = demo_final['rating'].dot(demo_final['percent_infp'])
        rating_census = demo_final['rating'].dot(demo_final['percent_census'])
        
        ratings_df = pd.DataFrame({'unweighted_rating': [rating_unweighted], 'weighted_infp_rating': [rating_infp], 'weighted_census_rating': [rating_census],})
        
        df_all = pd.concat([df_initial, demo_df, ratings_df], axis=1)
        
        df = df.append(df_all, ignore_index=True)
        

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
MEASURE THE DIFFERENCE 
between the Unweighted and Weighted Score

Determine which film's reputation (unweighted score) differs the most 
from it's actual enjoyment



Difference > 0.0  POS   Film is MORE liked than IMDb suggests
Difference < 0.0  NEG   Film is LESS liked than IMDb suggests

"""
df['difference_infp'] = df['weighted_infp_rating']-df['unweighted_rating']
df['difference_census'] = df['weighted_census_rating']-df['unweighted_rating']
df = df.sort_values(by='difference_census', ascending=False)

#df['abs_difference']= abs(df['difference'])
#df = df.sort_values(by='abs_difference', ascending=False)

"""
Print the essential info from the dataframe
"""

print(df[['Title', 'Year', 'Language','Votes', 'Rating','unweighted_rating', 'weighted_infp_rating','weighted_census_rating', 'difference_infp', 'difference_census']])

"""
MEASURE DIFFERENCE IN RANK

See how the reweighting affects the order of scores (particularly for the top 250)
"""

df['rank_unweighted']=df['unweighted_rating'].rank(ascending=0).astype(int)
df['rank_infp']=df['weighted_infp_rating'].rank(ascending=0).astype(int)
df['rank_census']=df['weighted_census_rating'].rank(ascending=0).astype(int)
df['rank_difference_infp'] = df['rank_unweighted']-df['rank_infp']
df['rank_difference_census'] = df['rank_unweighted']-df['rank_census']

df = df.sort_values(by='rank_difference_census', ascending=False)
print(df.head(10)[['Title', 'Year', 'Language','Votes', 'Rating','unweighted_rating', 'weighted_infp_rating','weighted_census_rating', 'difference_infp', 'difference_census', 'rank_unweighted', 'rank_infp', 'rank_census', 'rank_difference_infp', 'rank_difference_census']])
print(df.tail(10)[['Title', 'Year', 'Language','Votes', 'Rating','unweighted_rating', 'weighted_infp_rating','weighted_census_rating', 'difference_infp', 'difference_census', 'rank_unweighted', 'rank_infp', 'rank_census', 'rank_difference_infp', 'rank_difference_census']])

df = df.sort_values(by='rank_difference_census', ascending=True)
print(df[['Title', 'Year', 'Language','Votes', 'Rating','unweighted_rating', 'weighted_infp_rating','weighted_census_rating', 'difference_infp', 'difference_census', 'rank_unweighted', 'rank_infp', 'rank_census', 'rank_difference_infp', 'rank_difference_census']])


#writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/Reweighted250_{}.xlsx'.format(datetime.datetime.now().strftime("%m-%d_%H-%M")))
writer = ExcelWriter('/Users/kerrydriscoll/Documents/imdb project/Reweighted_Possible250_{}.xlsx'.format(datetime.datetime.now().strftime("%m-%d_%H-%M")))
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