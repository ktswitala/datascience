
# coding: utf-8

# # Assignment 2
# 
# Before working on this assignment please read these instructions fully. In the submission area, you will notice that you can click the link to **Preview the Grading** for each step of the assignment. This is the criteria that will be used for peer grading. Please familiarize yourself with the criteria before beginning the assignment.
# 
# An NOAA dataset has been stored in the file `data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv`. The data for this assignment comes from a subset of The National Centers for Environmental Information (NCEI) [Daily Global Historical Climatology Network](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt) (GHCN-Daily). The GHCN-Daily is comprised of daily climate records from thousands of land surface stations across the globe.
# 
# Each row in the assignment datafile corresponds to a single observation.
# 
# The following variables are provided to you:
# 
# * **id** : station identification code
# * **date** : date in YYYY-MM-DD format (e.g. 2012-01-24 = January 24, 2012)
# * **element** : indicator of element type
#     * TMAX : Maximum temperature (tenths of degrees C)
#     * TMIN : Minimum temperature (tenths of degrees C)
# * **value** : data value for element (tenths of degrees C)
# 
# For this assignment, you must:
# 
# 1. Read the documentation and familiarize yourself with the dataset, then write some python code which returns a line graph of the record high and record low temperatures by day of the year over the period 2005-2014. The area between the record high and record low temperatures for each day should be shaded.
# 2. Overlay a scatter of the 2015 data for any points (highs and lows) for which the ten year record (2005-2014) record high or record low was broken in 2015.
# 3. Watch out for leap days (i.e. February 29th), it is reasonable to remove these points from the dataset for the purpose of this visualization.
# 4. Make the visual nice! Leverage principles from the first module in this course when developing your solution. Consider issues such as legends, labels, and chart junk.
# 
# The data you have been given is near **Ann Arbor, Michigan, United States**, and the stations the data comes from are shown on the map below.

# In[1]:

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import mplleaflet
import pandas as pd

def leaflet_plot_stations(binsize, hashid):
    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))
    
    station_locations_by_hash = df[df['hash'] == hashid]
            
    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))
    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)
    return mplleaflet.display()

leaflet_plot_stations(400,'fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89')


# In[6]:

def plot_stuff():
    temp_data = pd.read_csv('data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')
    
    temp_data_groups = temp_data.groupby('Element')
    temp_df_min = temp_data_groups.get_group('TMIN')
    temp_df_max = temp_data_groups.get_group('TMAX')
    
    station_groups_min = temp_df_min.groupby('ID')
    station_groups_max = temp_df_max.groupby('ID')
        
    df_min_dict = {}
    for group_name, group in station_groups_min.groups.items():
        group_df = station_groups_min.get_group(group_name)
        df_min_dict[group_name] = pd.Series(data=group_df['Data_Value'].values, index=group_df['Date'])

    df_min = pd.DataFrame(df_min_dict).mean(axis=1)
    df_min.index = pd.to_datetime(df_min.index)

    df_max_dict = {}
    for group_name, group in station_groups_max.groups.items():
        group_df = station_groups_max.get_group(group_name)
        df_max_dict[group_name] = pd.Series(data=group_df['Data_Value'].values, index=group_df['Date'])

    df_max = pd.DataFrame(df_max_dict).mean(axis=1)
    df_max.index = pd.to_datetime(df_max.index)
    
    def group_by_date(row):
        return (row.month, row.day)
        return '{0}-{1}'.format(row.month, row.day)
        
    series_min = df_min['2005':'2014'].groupby(group_by_date).agg('min')
    series_max = df_max['2005':'2014'].groupby(group_by_date).agg('max')

    record_data = pd.DataFrame({'min':series_min, 'max':series_max}, index=series_min.index)
    
    def norm(v):
        return (v - df['min'].min()) / df['max'].max()
    
    def pick_color(row):
        ave = (row['min'] + row['max']) / 2
        return ave
        if ave < 0:
            return 0.9 * row['min'] + 0.1 * row['max']
        else:
            return 0.2 * row['min'] + 0.8 * row['max']
            
    segments = []
    color_array = []
    scatter_hi_points = []
    scatter_lo_points = []
    
    months = ['Jan', 'Feb', 'Mar', "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months = {month_name : pd.Timestamp(year=1999, month=month_i+1, day=1).dayofyear for month_i, month_name in enumerate(months)}
    
    for idx, row in record_data.iterrows():
        if idx[0] == 2 and idx[1] == 29:
            continue
        day = pd.Timestamp(year=1999, month=idx[0], day=idx[1]).dayofyear
        segments.append( [[day, row['min'] / 10],[day, row['max'] / 10]] )
        color_array.append( pick_color(row) )
        
        row_2015_min = df_min[pd.Timestamp(year=2015, month=idx[0], day=idx[1])]
        row_2015_max = df_max[pd.Timestamp(year=2015, month=idx[0], day=idx[1])]
        
        if row_2015_min < row['min']:
            scatter_lo_points.append( (day, row_2015_min / 10) )
        if row_2015_max > row['max']:
            scatter_hi_points.append( (day, row_2015_max / 10) )
                
    plt.figure(figsize=((365*3/80), 10), dpi=80)

    temp_cmap = mpl.colors.LinearSegmentedColormap.from_list('temp', ('blue', 'yellow', 'red'))
    norm = plt.Normalize(-150, 300)
    lines = mpl.collections.LineCollection(segments, cmap=temp_cmap, norm=norm, linewidth=3, zorder=0)
    lines.set_array( np.array(color_array) )

    plt.gca().set_xlim([0, 365])
    plt.gca().set_ylim([-30.0, 40.0])
    plt.gca().add_collection(lines)
    
    xs, ys = zip(*scatter_lo_points)
    art1 = plt.scatter(xs, ys, color='blue', zorder=1)

    xs, ys = zip(*scatter_hi_points)
    art2 = plt.scatter(xs, ys, color='red', zorder=1)

    plt.xticks(np.array(list(months.values()) + [365]), list(months.keys()) + ['Jan'])
    
    plt.legend(['High/low record for 2005-2014', 'Record low in 2015', 'Record high in 2015'])

    plt.title("Daily high/low record temperature for years 2005-2014\n(Michigan, United States)", size=24)
    plt.xlabel("Day of year", size=16)
    plt.ylabel("Temperature (°C)", size=16)
    
    plt.tight_layout()
    plt.savefig('plot.png')
    
    return None

plot_stuff()


# In[ ]:




# In[ ]:



