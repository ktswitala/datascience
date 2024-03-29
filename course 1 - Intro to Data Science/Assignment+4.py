
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[103]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[104]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
states_fixed = dict(zip(states.values(), states.keys()))


# In[105]:



def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
                
    current_state = None
    pairs = []
    
    import re
    #print(open("university_towns.txt", "r").read())
    with open("university_towns.txt", "r") as f:
        for line in f.readlines():
            m = re.match("(.*)\[edit\](.*)", line) 
            if m:
                state = m.group(1)
                if state in states_fixed:
                    current_state = state
                    continue
                else:
                    raise Exception("unknown line", line)
             
            else:
                idx = line.find("(")
                if idx > -1:
                    line = line[:idx]
                line = line.strip(" ").strip('\n')
                pairs.append((current_state, line))
            
            #if line == 'The Colleges of Worcester Consortium:\n':
            #    continue
                
            #if line == 'The Five College Region of Western Massachusetts:\n':
            #    continue
            
            #if line == 'Faribault, South Central College\n':
            #    pairs.append([current_state, 'Faribault'])
            #    continue
            
            #if line == 'North Mankato, South Central College\n':
            #    pairs.append([current_state, 'North Mankato'])
            #    continue
            
            
            #raise Exception("unmatched line", current_state, line)
    
    return pd.DataFrame(pairs, columns=["State", "RegionName"] )


# In[106]:


gdp = pd.read_excel('gdplev.xls', usecols=[4,6])
gdp.columns = ['Quarterly', 'GDP in billions of chained 2009 dollars']
gdp = gdp.drop( range(0, 219) )
gdp['GDP Change'] = gdp.iloc[:, [1]].diff()
gdp = gdp.set_index('Quarterly')

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    def window_func(params):
        if params[0] < 0 and params[1] < 0:
            return True
        else:
            return False
    
    gdp['Recession start'] = gdp['GDP Change'].rolling(2).apply(window_func)
    
    return gdp['Recession start'].shift(-1).idxmax()
get_recession_start()


# In[107]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
           
    def window_func(params):
        if params[0] > 0 and params[1] > 0:
            return True
        else:
            return False
    
    gdp['Recession end'] = gdp['GDP Change'].rolling(2).apply(window_func)
    rec_start = get_recession_start()
    looking_for_end = False
    rec_end = None
    for idx, row in gdp.iterrows():
        if looking_for_end is True:
            if row['Recession end'] == 1:
                rec_end = idx
        if idx == rec_start:
            looking_for_end = True
        if rec_end is not None:
            break
        
    return rec_end
get_recession_end()
#gdp.loc[250:260]


# In[108]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    def window_func(params):
        print(params)
        return True

    start_idx = get_recession_start()
    end_idx = get_recession_end()
    gdp['Recession'] = 0
    gdp.loc[start_idx:end_idx]['Recession'] = 1

    bottom_idx = gdp[gdp['Recession'] == 1]['GDP in billions of chained 2009 dollars'].idxmin()
    return bottom_idx
get_recession_bottom()


# In[109]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housing_data = pd.read_csv('City_Zhvi_AllHomes.csv')
    housing_data.drop(['RegionID', 'Metro', 'CountyName', 'SizeRank'], axis=1, inplace=True)
    
    mindex_tuples = list(zip(housing_data['State'].apply(lambda s: states[s]), housing_data['RegionName']))
    mindex = pd.MultiIndex.from_tuples(mindex_tuples, names=("State", "RegionName"))
    
    df = pd.DataFrame()
    for year in range(2000, 2017):
        for i, (q_name, months) in enumerate(zip(range(1,5), [[1,2,3], [4,5,6], [7,8,9], [10,11,12]])):
            column_to = '{0}q{1}'.format(year, i+1)
            columns_from = ["{0}-{1:02d}".format(year, m) for m in months]
            if column_to == '2016q4':
                continue
            df[column_to] = housing_data.loc[:,columns_from].mean(axis=1)
            
    df.index = mindex
    df = df.sort_index()
    return df


# In[121]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #print(gdp.loc['2008q1':'2009q4'])

    university_towns = get_list_of_university_towns()
    rec_bottom = get_recession_bottom()
    rec_start = get_recession_start()
    rec_end = get_recession_end()
    housing_data = convert_housing_data_to_quarters()

    housing_change = housing_data[rec_bottom] - housing_data[rec_start] 
    housing_ratio = housing_data[rec_start] / housing_data[rec_bottom]
        
    def university_group_fn(params):
        state, region_name = params
        is_uni_town = max( (university_towns['State'] == state) & (university_towns['RegionName'] == region_name) )
        if is_uni_town:
            return "uni"
        else:
            return "non-uni"
            
    housing_change = housing_change.groupby(by=university_group_fn)    
    ttest = ttest_ind(housing_change.get_group("uni").dropna(), housing_change.get_group("non-uni").dropna())

    first_answer = ttest.pvalue < 0.01
    second_answer = ttest.pvalue
    uni_mean = housing_ratio.loc[housing_change.get_group("uni").index].dropna().mean()
    non_uni_mean = housing_ratio.loc[housing_change.get_group("non-uni").index].dropna().mean()
    print(uni_mean, non_uni_mean)
    if uni_mean > non_uni_mean:
        third_answer = "university town"
    else:
        third_answer = "non-university town"
        
    return (first_answer, second_answer, third_answer)
run_ttest()


# In[ ]:





# In[ ]:




