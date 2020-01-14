
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-text-mining/resources/d9pwm) course resource._
# 
# ---

# # Assignment 3
# 
# In this assignment you will explore text message data and create models to predict if a message is spam or not. 

# In[1]:


import pandas as pd
import numpy as np

spam_data = pd.read_csv('spam.csv')

spam_data['target'] = np.where(spam_data['target']=='spam',1,0)
spam_data.head(10)


# In[2]:


from sklearn.model_selection import train_test_split


X_train, X_test, y_train, y_test = train_test_split(spam_data['text'], 
                                                    spam_data['target'], 
                                                    random_state=0)


# ### Question 1
# What percentage of the documents in `spam_data` are spam?
# 
# *This function should return a float, the percent value (i.e. $ratio * 100$).*

# In[3]:


def answer_one():
    return spam_data['target'].sum() / len(spam_data['target']) * 100


# In[4]:


answer_one()


# ### Question 2
# 
# Fit the training data `X_train` using a Count Vectorizer with default parameters.
# 
# What is the longest token in the vocabulary?
# 
# *This function should return a string.*

# In[5]:


from sklearn.feature_extraction.text import CountVectorizer

def answer_two():
    vect = CountVectorizer().fit(X_train)
    return max([(f, len(f)) for f in vect.get_feature_names()], key=lambda f: f[1])[0]


# In[6]:


answer_two()


# ### Question 3
# 
# Fit and transform the training data `X_train` using a Count Vectorizer with default parameters.
# 
# Next, fit a fit a multinomial Naive Bayes classifier model with smoothing `alpha=0.1`. Find the area under the curve (AUC) score using the transformed test data.
# 
# *This function should return the AUC score as a float.*

# In[7]:


from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score

def answer_three():
    vect = CountVectorizer().fit(X_train)
    X_train_v = vect.transform(X_train)
    model = MultinomialNB(alpha=0.1).fit(X_train_v, y_train)
    
    return roc_auc_score(y_test, model.predict(vect.transform(X_test)))


# In[8]:


answer_three()


# ### Question 4
# 
# Fit and transform the training data `X_train` using a Tfidf Vectorizer with default parameters.
# 
# What 20 features have the smallest tf-idf and what 20 have the largest tf-idf?
# 
# Put these features in a two series where each series is sorted by tf-idf value and then alphabetically by feature name. The index of the series should be the feature name, and the data should be the tf-idf.
# 
# The series of 20 features with smallest tf-idfs should be sorted smallest tfidf first, the list of 20 features with largest tf-idfs should be sorted largest first. 
# 
# *This function should return a tuple of two series
# `(smallest tf-idfs series, largest tf-idfs series)`.*

# In[86]:


from sklearn.feature_extraction.text import TfidfVectorizer

def answer_four():
    vect = TfidfVectorizer().fit(X_train)
    X_train_v = vect.transform(X_train)    
    X_train_v = X_train_v.max(axis=0).toarray()
        
    idf_values = {feature_name:X_train_v[0, idx] for feature_name, idx in vect.vocabulary_.items()}
    df = pd.DataFrame({'feature':list(idf_values.keys()), 'coef':list(idf_values.values())})

    df = df.sort_values(['coef', 'feature'], ascending=[True, True])
    small_srs = pd.Series(df['coef'][:20].values, index=df['feature'][:20].values)
    df = df.sort_values(['coef', 'feature'], ascending=[False, True])
    large_srs = pd.Series(df['coef'][:20].values, index=df['feature'][:20].values)
    
    return (small_srs, large_srs)


# In[87]:


answer_four()


# ### Question 5
# 
# Fit and transform the training data `X_train` using a Tfidf Vectorizer ignoring terms that have a document frequency strictly lower than **3**.
# 
# Then fit a multinomial Naive Bayes classifier model with smoothing `alpha=0.1` and compute the area under the curve (AUC) score using the transformed test data.
# 
# *This function should return the AUC score as a float.*

# In[11]:


def answer_five():
    vect = TfidfVectorizer(min_df=3).fit(X_train)
    X_train_v = vect.transform(X_train)
    model = MultinomialNB(alpha=0.1).fit(X_train_v, y_train)
    
    return roc_auc_score(y_test, model.predict(vect.transform(X_test)))    


# In[12]:


answer_five()


# ### Question 6
# 
# What is the average length of documents (number of characters) for not spam and spam documents?
# 
# *This function should return a tuple (average length not spam, average length spam).*

# In[13]:


def answer_six():
    avg_not_spam = spam_data[spam_data['target']==0]['text'].str.len().mean()
    avg_spam = spam_data[spam_data['target']==1]['text'].str.len().mean()
    return (avg_not_spam, avg_spam)


# In[14]:


answer_six()


# <br>
# <br>
# The following function has been provided to help you combine new features into the training data:

# In[15]:


def add_feature(X, feature_to_add):
    """
    Returns sparse feature matrix with added feature.
    feature_to_add can also be a list of features.
    """
    from scipy.sparse import csr_matrix, hstack
    return hstack([X, csr_matrix(feature_to_add).T], 'csr')


# ### Question 7
# 
# Fit and transform the training data X_train using a Tfidf Vectorizer ignoring terms that have a document frequency strictly lower than **5**.
# 
# Using this document-term matrix and an additional feature, **the length of document (number of characters)**, fit a Support Vector Classification model with regularization `C=10000`. Then compute the area under the curve (AUC) score using the transformed test data.
# 
# *This function should return the AUC score as a float.*

# In[16]:


from sklearn.svm import SVC

def answer_seven():
    vect = TfidfVectorizer(min_df=5).fit(X_train)
    X_train_v = vect.transform(X_train)
    
    X_train_v = add_feature(X_train_v, X_train.str.len())
    X_test_v = add_feature(vect.transform(X_test), X_test.str.len())
    
    model = SVC(C=10000).fit(X_train_v, y_train)
    
    return roc_auc_score(y_test, model.predict(X_test_v))   


# In[17]:


answer_seven()


# ### Question 8
# 
# What is the average number of digits per document for not spam and spam documents?
# 
# *This function should return a tuple (average # digits not spam, average # digits spam).*

# In[18]:


def count_digits(s):
    return len([c for c in s if c.isdigit()])

def answer_eight():

    avg_not_spam = spam_data[spam_data['target']==0]['text'].apply(count_digits).mean()
    avg_spam = spam_data[spam_data['target']==1]['text'].apply(count_digits).mean()
    return (avg_not_spam, avg_spam)


# In[19]:


answer_eight()


# ### Question 9
# 
# Fit and transform the training data `X_train` using a Tfidf Vectorizer ignoring terms that have a document frequency strictly lower than **5** and using **word n-grams from n=1 to n=3** (unigrams, bigrams, and trigrams).
# 
# Using this document-term matrix and the following additional features:
# * the length of document (number of characters)
# * **number of digits per document**
# 
# fit a Logistic Regression model with regularization `C=100`. Then compute the area under the curve (AUC) score using the transformed test data.
# 
# *This function should return the AUC score as a float.*

# In[20]:


from sklearn.linear_model import LogisticRegression

def answer_nine():
    vect = TfidfVectorizer(min_df=5, ngram_range=(1,3)).fit(X_train)

    X_train_v = add_feature(vect.transform(X_train), 
        [X_train.str.len(), X_train.apply(count_digits)] )
    X_test_v = add_feature(vect.transform(X_test), 
        [X_test.str.len(), X_test.apply(count_digits)] )

    model = LogisticRegression(C=100).fit(X_train_v, y_train)
    
    return roc_auc_score(y_test, model.predict(X_test_v))


# In[21]:


answer_nine()


# ### Question 10
# 
# What is the average number of non-word characters (anything other than a letter, digit or underscore) per document for not spam and spam documents?
# 
# *Hint: Use `\w` and `\W` character classes*
# 
# *This function should return a tuple (average # non-word characters not spam, average # non-word characters spam).*

# In[22]:


def count_nonword(s):
    return len([c for c in s if not c.isdigit() and not c.isalpha() and c != '_'])

def answer_ten():
    avg_not_spam = spam_data[spam_data['target']==0]['text'].apply(count_nonword).mean()
    avg_spam = spam_data[spam_data['target']==1]['text'].apply(count_nonword).mean()    
    
    return (avg_not_spam, avg_spam)


# In[23]:


answer_ten()


# ### Question 11
# 
# Fit and transform the training data X_train using a Count Vectorizer ignoring terms that have a document frequency strictly lower than **5** and using **character n-grams from n=2 to n=5.**
# 
# To tell Count Vectorizer to use character n-grams pass in `analyzer='char_wb'` which creates character n-grams only from text inside word boundaries. This should make the model more robust to spelling mistakes.
# 
# Using this document-term matrix and the following additional features:
# * the length of document (number of characters)
# * number of digits per document
# * **number of non-word characters (anything other than a letter, digit or underscore.)**
# 
# fit a Logistic Regression model with regularization C=100. Then compute the area under the curve (AUC) score using the transformed test data.
# 
# Also **find the 10 smallest and 10 largest coefficients from the model** and return them along with the AUC score in a tuple.
# 
# The list of 10 smallest coefficients should be sorted smallest first, the list of 10 largest coefficients should be sorted largest first.
# 
# The three features that were added to the document term matrix should have the following names should they appear in the list of coefficients:
# ['length_of_doc', 'digit_count', 'non_word_char_count']
# 
# *This function should return a tuple `(AUC score as a float, smallest coefs list, largest coefs list)`.*

# In[42]:


def answer_eleven():
    vect = CountVectorizer(min_df=5, ngram_range=(2,5), analyzer='char_wb').fit(X_train)
    
    X_train_v = add_feature(vect.transform(X_train), 
        [X_train.str.len(), X_train.apply(count_digits), X_train.apply(count_nonword)] )
    X_test_v = add_feature(vect.transform(X_test), 
        [X_test.str.len(), X_test.apply(count_digits), X_test.apply(count_nonword)] )
    
    model = LogisticRegression(C=100).fit(X_train_v, y_train)
    
    coefs = {feature_name:model.coef_[0,idx] for feature_name, idx in vect.vocabulary_.items()}
    
    coefs['length_of_doc'] = model.coef_[0, -3]
    coefs['digit_count'] = model.coef_[0, -2]
    coefs['non_word_char_count'] = model.coef_[0, -1]
    
    sorted_coefs = sorted(list(coefs.items()), key=lambda t: t[1])
    
    small_coef = sorted_coefs[:10]
    large_coef = sorted_coefs[-10:]
    
    print(small_coef)
    idx, vals = zip(*small_coef)
    small_coef = pd.Series(vals, index=idx)

    idx, vals = zip(*large_coef)
    large_coef = pd.Series(vals, index=idx)
    
    score = roc_auc_score(y_test, model.predict(X_test_v))
    return (score, small_coef, large_coef)


# In[43]:


answer_eleven()


# In[ ]:




