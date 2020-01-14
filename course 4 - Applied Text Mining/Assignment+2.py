
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.0** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-text-mining/resources/d9pwm) course resource._
# 
# ---

# # Assignment 2 - Introduction to NLTK
# 
# In part 1 of this assignment you will use nltk to explore the Herman Melville novel Moby Dick. Then in part 2 you will create a spelling recommender function that uses nltk to find words similar to the misspelling. 

# ## Part 1 - Analyzing Moby Dick

# In[82]:


import nltk
import pandas as pd
import numpy as np

# If you would like to work with the raw text you can use 'moby_raw'
with open('moby.txt', 'r') as f:
    moby_raw = f.read()
    
# If you would like to work with the novel in nltk.Text format you can use 'text1'
moby_tokens = nltk.word_tokenize(moby_raw)
text1 = nltk.Text(moby_tokens)


# ### Example 1
# 
# How many tokens (words and punctuation symbols) are in text1?
# 
# *This function should return an integer.*

# In[83]:


def example_one():
    
    return len(nltk.word_tokenize(moby_raw)) # or alternatively len(text1)

example_one()


# ### Example 2
# 
# How many unique tokens (unique words and punctuation) does text1 have?
# 
# *This function should return an integer.*

# In[84]:


def example_two():
    
    return len(set(nltk.word_tokenize(moby_raw))) # or alternatively len(set(text1))

example_two()


# ### Example 3
# 
# After lemmatizing the verbs, how many unique tokens does text1 have?
# 
# *This function should return an integer.*

# In[85]:


from nltk.stem import WordNetLemmatizer

def example_three():

    lemmatizer = WordNetLemmatizer()
    lemmatized = [lemmatizer.lemmatize(w,'v') for w in text1]

    return len(set(lemmatized))

example_three()


# ### Question 1
# 
# What is the lexical diversity of the given text input? (i.e. ratio of unique tokens to the total number of tokens)
# 
# *This function should return a float.*

# In[86]:



tokens = nltk.word_tokenize(moby_raw)
unique_tokens = set(tokens)
lemmatizer = WordNetLemmatizer()
stems = [lemmatizer.lemmatize(w,'v') for w in text1]
unique_stems = set(stems)
tags = nltk.pos_tag(tokens)
moby_sents = nltk.sent_tokenize(moby_raw)

def answer_one():
    return len(unique_tokens) / len(tokens)

answer_one()


# ### Question 2
# 
# What percentage of tokens is 'whale'or 'Whale'?
# 
# *This function should return a float.*

# In[100]:


def answer_two():
    return len([tok for tok in tokens if tok == 'whale' or tok == 'Whale']) / len(tokens) * 100

answer_two()


# ### Question 3
# 
# What are the 20 most frequently occurring (unique) tokens in the text? What is their frequency?
# 
# *This function should return a list of 20 tuples where each tuple is of the form `(token, frequency)`. The list should be sorted in descending order of frequency.*

# In[88]:


token_freq = nltk.FreqDist(tokens)

token_freq_sorted = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)

def answer_three():
    return token_freq_sorted[:20]

answer_three()


# ### Question 4
# 
# What tokens have a length of greater than 5 and frequency of more than 150?
# 
# *This function should return an alphabetically sorted list of the tokens that match the above constraints. To sort your list, use `sorted()`*

# In[89]:


def answer_four():
    return sorted([tok for tok in unique_tokens if len(tok) > 5 and token_freq[tok] > 150])

answer_four()


# ### Question 5
# 
# Find the longest word in text1 and that word's length.
# 
# *This function should return a tuple `(longest_word, length)`.*

# In[90]:


def answer_five():
    return max([(tok, len(tok)) for tok in unique_tokens], key=lambda k: k[1])

answer_five()


# ### Question 6
# 
# What unique words have a frequency of more than 2000? What is their frequency?
# 
# "Hint:  you may want to use `isalpha()` to check if the token is a word and not punctuation."
# 
# *This function should return a list of tuples of the form `(frequency, word)` sorted in descending order of frequency.*

# In[91]:


def answer_six(): 
    return [(freq, tok) for tok, freq in token_freq_sorted if freq > 2000 and tok.isalpha()]


answer_six()


# ### Question 7
# 
# What is the average number of tokens per sentence?
# 
# *This function should return a float.*

# In[92]:



def answer_seven():
    
    tokens = 0
    sents = 0
    for sent in moby_sents:
        tokens += len(nltk.word_tokenize(sent))
        sents += 1
    return tokens / sents

answer_seven()


# ### Question 8
# 
# What are the 5 most frequent parts of speech in this text? What is their frequency?
# 
# *This function should return a list of tuples of the form `(part_of_speech, frequency)` sorted in descending order of frequency.*

# In[93]:



def answer_eight():
    import collections
    d = collections.defaultdict(int)
    for tok, pos in tags:
        d[pos] += 1
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[:5]

answer_eight()


# ## Part 2 - Spelling Recommender
# 
# For this part of the assignment you will create three different spelling recommenders, that each take a list of misspelled words and recommends a correctly spelled word for every word in the list.
# 
# For every misspelled word, the recommender should find find the word in `correct_spellings` that has the shortest distance*, and starts with the same letter as the misspelled word, and return that word as a recommendation.
# 
# *Each of the three different recommenders will use a different distance measure (outlined below).
# 
# Each of the recommenders should provide recommendations for the three default words provided: `['cormulent', 'incendenece', 'validrate']`.

# In[94]:


from nltk.corpus import words

correct_spellings = words.words()


# ### Question 9
# 
# For this recommender, your function should provide recommendations for the three default words provided above using the following distance metric:
# 
# **[Jaccard distance](https://en.wikipedia.org/wiki/Jaccard_index) on the trigrams of the two words.**
# 
# *This function should return a list of length three:
# `['cormulent_reccomendation', 'incendenece_reccomendation', 'validrate_reccomendation']`.*

# In[101]:


def create_trigram(w):
    trigrams = []
    for i in range(0, len(w)-2):
        trigrams.append(w[i:i+3])
    return set(trigrams)

def answer_nine(entries=['cormulent', 'incendenece', 'validrate']):
    max_dists, max_words, trigrams = {}, {}, {}
    for entry in entries:
        max_dists[entry] = 1.0
        max_words[entry] = None
        trigrams[entry] = create_trigram(entry)

    def try_correct(correct_spelling, incorrect_spelling):
        c_trigram = create_trigram(correct_spelling)
        distance = nltk.jaccard_distance(trigrams[incorrect_spelling], c_trigram)
        if distance < max_dists[incorrect_spelling]:
            max_dists[incorrect_spelling] = distance
            max_words[incorrect_spelling] = correct_spelling

    for correct_spelling in correct_spellings:
        for entry in entries:
            if correct_spelling[0] == entry[0]:
                try_correct(correct_spelling, entry)
            
    return [max_words[entry] for entry in entries]
    
answer_nine()


# ### Question 10
# 
# For this recommender, your function should provide recommendations for the three default words provided above using the following distance metric:
# 
# **[Jaccard distance](https://en.wikipedia.org/wiki/Jaccard_index) on the 4-grams of the two words.**
# 
# *This function should return a list of length three:
# `['cormulent_reccomendation', 'incendenece_reccomendation', 'validrate_reccomendation']`.*

# In[103]:


def create_quadgram(w):
    quadgrams = []
    for i in range(0, len(w)-3):
        quadgrams.append(w[i:i+4])
    return set(quadgrams)

def answer_ten(entries=['cormulent', 'incendenece', 'validrate']):
    max_dists, max_words, quadgrams = {}, {}, {}
    for entry in entries:
        max_dists[entry] = 1.0
        max_words[entry] = None
        quadgrams[entry] = create_quadgram(entry)

    def try_correct(correct_spelling, incorrect_spelling):
        c_quadgram = create_quadgram(correct_spelling)
        distance = nltk.jaccard_distance(quadgrams[incorrect_spelling], c_quadgram)
        if distance < max_dists[incorrect_spelling]:
            max_dists[incorrect_spelling] = distance
            max_words[incorrect_spelling] = correct_spelling

    for correct_spelling in correct_spellings:
        for entry in entries:
            if correct_spelling[0] == entry[0]:
                try_correct(correct_spelling, entry)
            
    return [max_words[entry] for entry in entries]    
        
answer_ten()


# ### Question 11
# 
# For this recommender, your function should provide recommendations for the three default words provided above using the following distance metric:
# 
# **[Edit distance on the two words with transpositions.](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)**
# 
# *This function should return a list of length three:
# `['cormulent_reccomendation', 'incendenece_reccomendation', 'validrate_reccomendation']`.*

# In[99]:


def answer_eleven(entries=['cormulent', 'incendenece', 'validrate']):
    max_dists, max_words = {}, {}
    for entry in entries:
        max_dists[entry] = 1000.0
        max_words[entry] = None

    def try_correct(correct_spelling, incorrect_spelling):
        distance = nltk.edit_distance(correct_spelling, incorrect_spelling)
        if distance < max_dists[incorrect_spelling]:
            max_dists[incorrect_spelling] = distance
            max_words[incorrect_spelling] = correct_spelling

    for correct_spelling in correct_spellings:
        for entry in entries:
            if correct_spelling[0] == entry[0]:
                try_correct(correct_spelling, entry)
            
    return [max_words[entry] for entry in entries]    
        
answer_eleven()


# In[ ]:




