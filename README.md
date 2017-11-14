# IMDb-project
This is my attempt to reweigh IMDb movie scores by its demographic breakdown. Fingers crossed that this actually makes a difference.

# Synopsis
I am making this up as I go along. My tentative game-plan is as follows:
1. Scrape Demographic Score Data from IMDb 
  - may limit to films with over 1,000 user ratings (the same standard [Walt Hickey used in his TV show analysis](https://fivethirtyeight.com/features/men-are-sabotaging-the-online-reviews-of-tv-shows-aimed-at-women/))
  - may limit to >18 population, due to small IMDb user data in the under 18 population
  - uncertain if I am going to use IMDb's "arithmetic mean" or "weighted average" - IMDb weighs scores rather than relying on raw data to "eliminate and reduce attempts at vote stuffing by people more interested in changing the current rating of a movie than giving their true opinion of it."
2. Reweigh to match the 2016 Population Estimates released by the U.S. Census Bureau
3. See if there is a difference between "original" and weighted movie ratings

# Motivation
On a recent episode of the TIFF podcast, "Long Take", Walt Hickey, the culture writer on 538, discussed how movie-ratings may be problematic. One issue he identifyied is movie score aggregators (like IMDb, Rotten Tomatoes, etc) do not take the demographic distribution of voters into account when calculating scores. In other studies that use survey methodologies, pollsters will weigh respondents' answers to match the "known" distribution of the universe. For instance: if males make up 60% of the survey responses, but are known to make up 50% of the population, then we know that males were oversampled. To correct this, survey designers will be weight down the male responses and weigh up the female responses. I am was inspired to do the same with IMDb scores which provide a rough demographic breakdown by gender (male, female) and age group (<18, 18-29, 30-44, >45).

# Installation
I am writing this code in Python. Wish me luck.

# Contributors
Me, myself and I.

# License
who is going to see this? just give me credit if you do find it interesting
