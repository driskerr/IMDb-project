#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 09:29:09 2019

@author: kerrydriscoll
"""

"""
Import Libraries
"""

from time import time, sleep
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
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
Visualize Data
"""
movie_performance = pd.read_excel('/Users/kerrydriscoll/Documents/imdb project/Reweighted_Possible250_03-08_06-55.xlsx')
vote_col = [col for col in movie_performance.columns if 'votes' in col.lower()]
rating_col = [col for col in movie_performance.columns if 'rating' in col.lower()]

"""
Help me pick which movies to visualize
"""
temp = movie_performance[['Title','Top 250 Rank', 'Votes', 'males_votes','females_votes', 'rank_difference_census']]
temp['% male'] = temp['males_votes'] / temp['Votes']
temp['% female'] = temp['females_votes'] / temp['Votes']
temp['difference'] = temp['% male'] - temp['% female']
temp.sort_values(by='difference',ascending=False,inplace=True)
print(temp[temp['Top 250 Rank'].notnull()])


"""
U.S. Census Targets
"""
us_targets = pd.read_csv(r'/Users/kerrydriscoll/Documents/imdb project/ACS_demos.csv')
gender = us_targets.groupby('gender')['count'].sum().reset_index()
age = us_targets.groupby('age')['count'].sum().reset_index()

"""
Average IMDb Movie (with over 25,000 votes)
a.k.a. Eligible for IMDb top 250
"""
average_movie = movie_performance[vote_col].sum()

fig3, ax3 = plt.subplots(1,2, figsize=(7.62, 5.08))
size = 0.4

plt.subplot(1,2,1)
inner_colors = ('#417E90','#DB3948')
outer_colors = ('#92B8C3','#EA8D95')
plt.pie([gender[gender['gender']=='males']['count'].values,gender[gender['gender']=='females']['count'].values],\
        radius=1-size,\
        colors=inner_colors,\
        autopct='%1.f%%',pctdistance=0.65,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
plt.pie([average_movie['males_votes'],average_movie['females_votes']],\
        radius=1,\
        #labels=['Male', 'Female'],\
        colors=outer_colors,\
        autopct='%1.f%%',pctdistance=0.78,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
plt.legend(labels=['Male', 'Female'], loc= 8, ncol=2, bbox_to_anchor=(0.5, -0.2))
plt.title('Gender')

plt.subplot(1,2,2)
inner_colors = ('#32A257','#E45B17','#8863B2')
outer_colors = ('#A5D59F','#F9AD6B','#C2ABD9')
plt.pie([age[age['age']=='18 29']['count'].values,age[age['age']=='30 44']['count'].values,age[age['age']=='45 plus']['count'].values],\
        radius=1-size,\
        colors=inner_colors,\
        autopct='%1.f%%',pctdistance=0.65,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
plt.pie([average_movie['aged 18 29_votes'],average_movie['aged 30 44_votes'],average_movie['aged 45 plus_votes']],\
        radius=1,\
        #labels=['18-29','30-44','45+'],\
        colors=outer_colors,\
        autopct='%1.f%%',pctdistance=0.78,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
plt.legend(labels=['18-29','30-44','45+'], loc=8,ncol=3, bbox_to_anchor=(0.5, -0.2))
plt.title('Age')

fig3.suptitle('Average IMDb Movie',fontsize="x-large")

#plt.savefig('Average IMDb Movie.png', bbox_inches="tight")
plt.show()


"""
Key on How to Read Chart
"""
fig2, ax2 = plt.subplots(figsize=(1.5,1.5))
inner_colors = ((0,0,0,.4),(0,0,0,.4),(0,0,0,.4))
outer_colors = ((0,0,0,.2),(0,0,0,.2),(0,0,0,.2))
plt.pie([gender[gender['gender']=='males']['count'].values,gender[gender['gender']=='females']['count'].values],\
        radius=1-size,\
        colors=inner_colors,\
        #autopct='%1.f%%',pctdistance=0.65,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
plt.pie([average_movie['males_votes'],average_movie['females_votes']],\
        radius=1,\
        #labels=['Male', 'Female'],\
        colors=outer_colors,\
        #autopct='%1.f%%',pctdistance=0.78,\
        wedgeprops=dict(width=size, edgecolor='w'),\
        startangle=90)
ax2.annotate("U.S. Census", xy=(.3, .2), xytext=(1.35*np.sign(.3), 1.4*.2),arrowprops=dict(facecolor='black', arrowstyle="->"))
ax2.annotate("IMDb Voters", xy=(.7, -.2), xytext=(1.35*np.sign(.7), 1.4*-.2),arrowprops=dict(facecolor='black', arrowstyle="->"))

#plt.savefig('key.png', bbox_inches="tight")
plt.show()


"""
Recreate for Any Specific Movie
"""

def demo_graphs(title):
    df = movie_performance[movie_performance['Title']==title][['Title', 'Year']+vote_col].reset_index()
    
    fig, ax = plt.subplots(1,2, figsize=(7.62, 5.08))
    size = 0.4
    
    plt.subplot(1,2,1)
    inner_colors = ('#417E90','#DB3948')
    outer_colors = ('#92B8C3','#EA8D95')
    plt.pie([gender[gender['gender']=='males']['count'].values,gender[gender['gender']=='females']['count'].values],\
            radius=1-size,\
            colors=inner_colors,\
            autopct='%1.f%%',pctdistance=0.65,\
            wedgeprops=dict(width=size, edgecolor='w'),\
            startangle=90)
    plt.pie([df['males_votes'][0],df['females_votes'][0]],\
            radius=1,\
            #labels=['Male', 'Female'],\
            colors=outer_colors,\
            autopct='%1.f%%',pctdistance=0.78,\
            wedgeprops=dict(width=size, edgecolor='w'),\
            startangle=90)
    plt.legend(labels=['Male', 'Female'], loc= 8, ncol=2, bbox_to_anchor=(0.5, -0.2))
    plt.title('Gender')
    
    plt.subplot(1,2,2)
    inner_colors = ('#32A257','#E45B17','#8863B2')
    outer_colors = ('#A5D59F','#F9AD6B','#C2ABD9')
    plt.pie([age[age['age']=='18 29']['count'].values,age[age['age']=='30 44']['count'].values,age[age['age']=='45 plus']['count'].values],\
            radius=1-size,\
            colors=inner_colors,\
            autopct='%1.f%%',pctdistance=0.65,\
            wedgeprops=dict(width=size, edgecolor='w'),\
            startangle=90)
    plt.pie([df['aged 18 29_votes'][0],df['aged 30 44_votes'][0], df['aged 45 plus_votes'][0]],\
            radius=1,\
            #labels=['18-29','30-44','45+'],\
            colors=outer_colors,\
            autopct='%1.f%%',pctdistance=0.78,\
            wedgeprops=dict(width=size, edgecolor='w'),\
            startangle=90)
    plt.legend(labels=['18-29','30-44','45+'], loc=8,ncol=3, bbox_to_anchor=(0.5, -0.2))
    plt.title('Age')
    
    fig.suptitle('{} ({})'.format(title, df['Year'][0]),fontsize="x-large")
    
    #plt.savefig('{}.png'.format(title), bbox_inches="tight")
    plt.show()
    
demo_graphs('The Wizard of Oz')
demo_graphs('For a Few Dollars More')

for t in movie_performance[['Title']].sample(10)['Title']:
    demo_graphs(t)
    
    
"""
Other Analysis
"""
#Number of Movies Swapped in the Top 250
num_swap250 = len(movie_performance[(movie_performance['Top 250 Rank'].notnull()) & (movie_performance['rank_census']>252)])
print(num_swap250)

#Genre Performance
all_genre = ', '.join(movie_performance['Genre'].unique().tolist())
genre_unique = []
for genre in all_genre.split(', '):
    if genre not in genre_unique:
        genre_unique.append(genre)

genre_performance_dict = {}
for genre in genre_unique:
    #print(genre)
    genre_df = movie_performance[movie_performance['Genre'].str.contains(genre)]
    #print(len(genre_df))
    #print(genre_df[['unweighted_rating','weighted_census_rating','difference_census', 'rank_unweighted','rank_census','rank_difference_census']].mean())
    genre_performance_dict[genre] = genre_df['rank_difference_census'].mean()
    
genre_performance_df = pd.DataFrame.from_dict(genre_performance_dict,orient='index', columns=['rank_difference_census']).sort_values(by='rank_difference_census')
genre_performance_df

genre_performance_dict = {}
for genre in genre_unique:
    #print(genre)
    genre_df = movie_performance[movie_performance['Genre'].str.contains(genre)]
    #print(len(genre_df))
    #print(genre_df[['unweighted_rating','weighted_census_rating','difference_census', 'rank_unweighted','rank_census','rank_difference_census']].mean())
    genre_performance_dict[genre] = genre_df['rank_difference_census'].mean()
    
genre_performance_df = pd.DataFrame.from_dict(genre_performance_dict,orient='index', columns=['rank_difference_census']).sort_values(by='rank_difference_census')
genre_performance_df

#Year Performance
year_performance_df = movie_performance.groupby((movie_performance['Year']//10)*10)['rank_difference_census'].mean()
year_performance_df

#Language Performance
language_opt_df = movie_performance.groupby('Language')['ID'].count().reset_index().sort_values(by='ID', ascending=False)
language_option = language_opt_df[language_opt_df['ID']>= 5]['Language'].unique()

language_performance_dict = {}
for language in language_option:
    #print(language)
    lang_df = movie_performance[movie_performance['Language'].str.contains(language)]
    #print(len(lang_df))
    #print(lang_df[['unweighted_rating','weighted_census_rating','difference_census', 'rank_unweighted','rank_census','rank_difference_census']].mean())
    language_performance_dict[language] = lang_df['rank_difference_census'].mean()
    
lang_performance_df = pd.DataFrame.from_dict(language_performance_dict,orient='index', columns=['rank_difference_census']).sort_values(by='rank_difference_census')
lang_performance_df


#Gender Compistion Performance
movie_performance['% male'] = movie_performance['males_votes']/(movie_performance['males_votes'] + movie_performance['females_votes'])
movie_performance['% female'] = movie_performance['females_votes']/(movie_performance['males_votes'] + movie_performance['females_votes'])

movie_performance['percentile % male'] = movie_performance.apply(lambda row: percentileofscore(movie_performance['% male'],row['% male']), axis=1)
movie_performance['percentile % male'].replace(100,99.99, inplace=True)
movie_performance['percentile % female'] = movie_performance.apply(lambda row: percentileofscore(movie_performance['% female'],row['% female']), axis=1)
movie_performance['percentile % female'].replace(100,99.99, inplace=True)

perc_fem_performance_df = movie_performance.groupby((movie_performance['percentile % female']//20)*20)['rank_difference_census'].mean()
perc_fem_performance_df

perc_m_performance_df = movie_performance.groupby((movie_performance['percentile % male']//20)*20)['rank_difference_census'].mean()
perc_m_performance_df


#Age Composition Performance
movie_performance['% 18 29'] = movie_performance['aged 18 29_votes']/(movie_performance['aged 18 29_votes'] + movie_performance['aged 30 44_votes']+movie_performance['aged 45 plus_votes'])
movie_performance['% 30 44'] = movie_performance['aged 30 44_votes']/(movie_performance['aged 18 29_votes'] + movie_performance['aged 30 44_votes']+movie_performance['aged 45 plus_votes'])
movie_performance['% 45 plus'] = movie_performance['aged 45 plus_votes']/(movie_performance['aged 18 29_votes'] + movie_performance['aged 30 44_votes']+movie_performance['aged 45 plus_votes'])

movie_performance['percentile % 18 29'] = movie_performance.apply(lambda row: percentileofscore(movie_performance['% 18 29'],row['% 18 29']), axis=1)
movie_performance['percentile % 18 29'].replace(100,99.99, inplace=True)
movie_performance['percentile % 30 44'] = movie_performance.apply(lambda row: percentileofscore(movie_performance['% 30 44'],row['% 30 44']), axis=1)
movie_performance['percentile % 30 44'].replace(100,99.99, inplace=True)
movie_performance['percentile % 45 plus'] = movie_performance.apply(lambda row: percentileofscore(movie_performance['% 45 plus'],row['% 45 plus']), axis=1)
movie_performance['percentile % 45 plus'].replace(100,99.99, inplace=True)

perc_18_29_performance_df = movie_performance.groupby((movie_performance['percentile % 18 29']//20)*20)['rank_difference_census'].mean()
perc_18_29_performance_df

perc_30_44_performance_df = movie_performance.groupby((movie_performance['percentile % 30 44']//20)*20)['rank_difference_census'].mean()
perc_30_44_performance_df

perc_45pl_performance_df = movie_performance.groupby((movie_performance['percentile % 45 plus']//20)*20)['rank_difference_census'].mean()
perc_45pl_performance_df