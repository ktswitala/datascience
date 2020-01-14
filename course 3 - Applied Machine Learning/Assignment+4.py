
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-machine-learning/resources/bANLa) course resource._
# 
# ---

# ## Assignment 4 - Understanding and Predicting Property Maintenance Fines
# 
# This assignment is based on a data challenge from the Michigan Data Science Team ([MDST](http://midas.umich.edu/mdst/)). 
# 
# The Michigan Data Science Team ([MDST](http://midas.umich.edu/mdst/)) and the Michigan Student Symposium for Interdisciplinary Statistical Sciences ([MSSISS](https://sites.lsa.umich.edu/mssiss/)) have partnered with the City of Detroit to help solve one of the most pressing problems facing Detroit - blight. [Blight violations](http://www.detroitmi.gov/How-Do-I/Report/Blight-Complaint-FAQs) are issued by the city to individuals who allow their properties to remain in a deteriorated condition. Every year, the city of Detroit issues millions of dollars in fines to residents and every year, many of these fines remain unpaid. Enforcing unpaid blight fines is a costly and tedious process, so the city wants to know: how can we increase blight ticket compliance?
# 
# The first step in answering this question is understanding when and why a resident might fail to comply with a blight ticket. This is where predictive modeling comes in. For this assignment, your task is to predict whether a given blight ticket will be paid on time.
# 
# All data for this assignment has been provided to us through the [Detroit Open Data Portal](https://data.detroitmi.gov/). **Only the data already included in your Coursera directory can be used for training the model for this assignment.** Nonetheless, we encourage you to look into data from other Detroit datasets to help inform feature creation and model selection. We recommend taking a look at the following related datasets:
# 
# * [Building Permits](https://data.detroitmi.gov/Property-Parcels/Building-Permits/xw2a-a7tf)
# * [Trades Permits](https://data.detroitmi.gov/Property-Parcels/Trades-Permits/635b-dsgv)
# * [Improve Detroit: Submitted Issues](https://data.detroitmi.gov/Government/Improve-Detroit-Submitted-Issues/fwz3-w3yn)
# * [DPD: Citizen Complaints](https://data.detroitmi.gov/Public-Safety/DPD-Citizen-Complaints-2016/kahe-efs3)
# * [Parcel Map](https://data.detroitmi.gov/Property-Parcels/Parcel-Map/fxkw-udwf)
# 
# ___
# 
# We provide you with two data files for use in training and validating your models: train.csv and test.csv. Each row in these two files corresponds to a single blight ticket, and includes information about when, why, and to whom each ticket was issued. The target variable is compliance, which is True if the ticket was paid early, on time, or within one month of the hearing data, False if the ticket was paid after the hearing date or not at all, and Null if the violator was found not responsible. Compliance, as well as a handful of other variables that will not be available at test-time, are only included in train.csv.
# 
# Note: All tickets where the violators were found not responsible are not considered during evaluation. They are included in the training set as an additional source of data for visualization, and to enable unsupervised and semi-supervised approaches. However, they are not included in the test set.
# 
# <br>
# 
# **File descriptions** (Use only this data for training your model!)
# 
#     readonly/train.csv - the training set (all tickets issued 2004-2011)
#     readonly/test.csv - the test set (all tickets issued 2012-2016)
#     readonly/addresses.csv & readonly/latlons.csv - mapping from ticket id to addresses, and from addresses to lat/lon coordinates. 
#      Note: misspelled addresses may be incorrectly geolocated.
# 
# <br>
# 
# **Data fields**
# 
# train.csv & test.csv
# 
#     ticket_id - unique identifier for tickets
#     agency_name - Agency that issued the ticket
#     inspector_name - Name of inspector that issued the ticket
#     violator_name - Name of the person/organization that the ticket was issued to
#     violation_street_number, violation_street_name, violation_zip_code - Address where the violation occurred
#     mailing_address_str_number, mailing_address_str_name, city, state, zip_code, non_us_str_code, country - Mailing address of the violator
#     ticket_issued_date - Date and time the ticket was issued
#     hearing_date - Date and time the violator's hearing was scheduled
#     violation_code, violation_description - Type of violation
#     disposition - Judgment and judgement type
#     fine_amount - Violation fine amount, excluding fees
#     admin_fee - $20 fee assigned to responsible judgments
# state_fee - $10 fee assigned to responsible judgments
#     late_fee - 10% fee assigned to responsible judgments
#     discount_amount - discount applied, if any
#     clean_up_cost - DPW clean-up or graffiti removal cost
#     judgment_amount - Sum of all fines and fees
#     grafitti_status - Flag for graffiti violations
#     
# train.csv only
# 
#     payment_amount - Amount paid, if any
#     payment_date - Date payment was made, if it was received
#     payment_status - Current payment status as of Feb 1 2017
#     balance_due - Fines and fees still owed
#     collection_status - Flag for payments in collections
#     compliance [target variable for prediction] 
#      Null = Not responsible
#      0 = Responsible, non-compliant
#      1 = Responsible, compliant
#     compliance_detail - More information on why each ticket was marked compliant or non-compliant
# 
# 
# ___
# 
# ## Evaluation
# 
# Your predictions will be given as the probability that the corresponding blight ticket will be paid on time.
# 
# The evaluation metric for this assignment is the Area Under the ROC Curve (AUC). 
# 
# Your grade will be based on the AUC score computed for your classifier. A model which with an AUROC of 0.7 passes this assignment, over 0.75 will recieve full points.
# ___
# 
# For this assignment, create a function that trains a model to predict blight ticket compliance in Detroit using `readonly/train.csv`. Using this model, return a series of length 61001 with the data being the probability that each corresponding ticket from `readonly/test.csv` will be paid, and the index being the ticket_id.
# 
# Example:
# 
#     ticket_id
#        284932    0.531842
#        285362    0.401958
#        285361    0.105928
#        285338    0.018572
#                  ...
#        376499    0.208567
#        376500    0.818759
#        369851    0.018528
#        Name: compliance, dtype: float32
#        
# ### Hints
# 
# * Make sure your code is working before submitting it to the autograder.
# 
# * Print out your result to see whether there is anything weird (e.g., all probabilities are the same).
# 
# * Generally the total runtime should be less than 10 mins. You should NOT use Neural Network related classifiers (e.g., MLPClassifier) in this question. 
# 
# * Try to avoid global variables. If you have other functions besides blight_model, you should move those functions inside the scope of blight_model.
# 
# * Refer to the pinned threads in Week 4's discussion forum when there is something you could not figure it out.

# In[98]:

import pandas as pd
import numpy as np

import time

import sklearn.model_selection
import sklearn.svm
import sklearn.dummy
import sklearn.ensemble

def blight_model():
    
    random_state = 6948
    
    test_filenames = ['train.csv', 'readonly/test.csv', 'readonly/addresses.csv', 'readonly/latlons.csv']
    submit_filenames = ['train.csv', 'test.csv', 'addresses.csv', 'latlons.csv']
    
    filenames = submit_filenames
    
    def resolve_latlon(data):
        data = data.merge(addrs, how='inner', on='ticket_id')
        data = data.merge(latlons, how='inner', on='address')
        data = data.drop(['ticket_id', 'address'], axis=1)
        return data
    
    # Your code here
    train_data_raw = pd.read_csv(filenames[0], encoding='ISO-8859-1')
    test_data_raw = pd.read_csv(filenames[1], encoding='ISO-8859-1')
    addrs = pd.read_csv(filenames[2], encoding='ISO-8859-1')
    latlons = pd.read_csv(filenames[3], encoding='ISO-8859-1')
    
    train_data_raw['ticket_issued_date'] = pd.to_datetime( train_data_raw['ticket_issued_date'] )
    
    def tree_data():
        data = {}
        
        fields = ['clean_up_cost', 'judgment_amount', 'discount_amount']
        data["train"] = train_data_raw[fields + ['compliance']]
        data["train"].index = train_data_raw['ticket_issued_date']
        data["train"] = data["train"].dropna()
        data["submit"] = test_data_raw[fields]
        data["submit"].index = test_data_raw['ticket_id']

        data["train"], data["test"] = data["train"].loc['2004':'2009'], data["train"].loc['2010':'2011']
        data["X_train"], data["y_train"] = data["train"][fields], data["train"]['compliance']
        data["X_test"], data["y_test"] = data["test"][fields], data["test"]['compliance']
        
        return data

    def location_data():
        data = {}
        
        data["train"] = train_data_raw[['ticket_id', 'compliance']]
        data["train"] = resolve_latlon(data["train"])
        data["train"].index = train_data_raw['ticket_issued_date']
        data["train"] = data["train"].dropna()
        data["submit"]= test_data_raw[['ticket_id']]
        data["submit"] = resolve_latlon(data["submit"]) 
        data["submit"].index = test_data_raw['ticket_id']
        data["submit"]['lat'] = data["submit"]['lat'].replace({np.nan:data["submit"]['lat'].mean()})
        data["submit"]['lon'] = data["submit"]['lon'].replace({np.nan:data["submit"]['lon'].mean()})

        data["train"], data["test"] = data["train"].loc['2004':'2009'], data["train"].loc['2010':'2011']
        data["X_train"], data["y_train"] = data["train"][['lat', 'lon']], data["train"]['compliance']
        data["X_test"], data["y_test"] = data["test"][['lat', 'lon']], data["test"]['compliance']

        return data
    
    def violation_data():
        data = {}       
        
        data["train"] = train_data_raw[['violation_code', 'compliance']]
        
        #print(data["train"].groupby('violation_code').agg(['count','mean']).sort_values(('compliance', 'count')))
        return data
    
    location_data = location_data()
    violation_data = violation_data()
    tree_data = tree_data()
    
    def score_model(data, m):
        predicts = m.predict(data["X_test"])
        scores = m.predict_proba(data["X_test"])[:,1]
        print(m)
        print(sklearn.metrics.confusion_matrix(data["y_test"], predicts))
        print(sklearn.metrics.roc_auc_score(data["y_test"], scores))

    def search_knn(data):
        print("searching knn...")
        start_time = time.time()

        for n in range(0,50,5):
            if n == 0:
                continue
            m = sklearn.neighbors.KNeighborsClassifier(n_neighbors=n)
            scores = sklearn.model_selection.cross_val_score(m, data["X_train"], data["y_train"], 
                scoring='roc_auc', cv=3)        
            print(n, scores.mean())
        for n in range(0,50,5):
            if n == 0:
                continue
            m = sklearn.neighbors.KNeighborsClassifier(n_neighbors=n, weights='distance')
            scores = sklearn.model_selection.cross_val_score(m, data["X_train"], data["y_train"], 
                scoring='roc_auc', cv=3)        
            print(n, scores.mean())
 
        print("searching knn took {0} secs".format(time.time()-start_time))
        
    def train_knn(data):
        m = sklearn.neighbors.KNeighborsClassifier(n_neighbors=25)
        m.fit(data["X_train"], data["y_train"])
        return m

    def train_trees(data):
        m = sklearn.ensemble.GradientBoostingClassifier()
        m.fit(data["X_train"], data["y_train"])
        return m
    
    def score_models():
        score_model(location_data, knn_model)
        score_model(tree_data, tree_model)
        
    #search_knn(location_data)

    knn_model = train_knn(location_data)
    tree_model = train_trees(tree_data)

    series = tree_model.predict_proba(tree_data["submit"])[:,1]
    #score_models()
    
    
    return pd.Series(series, index=test_data_raw['ticket_id'])


# In[97]:

blight_model()


# In[ ]:



