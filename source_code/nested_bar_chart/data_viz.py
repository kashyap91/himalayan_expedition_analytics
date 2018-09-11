#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:09:54 2018

@author: kashyap
"""

#import numpy as np
import pandas as pd
from bokeh.themes import Theme
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

####data import and preparation
#exped import and prep
expedimport = pd.read_csv("/Users/kashyap/Desktop/exped.csv", sep = ',', header = 0, low_memory=False)
expedselect2 = expedimport[['YEAR','PEAKID','TOTMEMBERS','SMTMEMBERS','TOTHIRED','SMTHIRED']]


#peak import and prep
peaksimport = pd.read_csv('/Users/kashyap/Desktop/peaks.csv',sep = ',', header=0, low_memory=False)
peaksfilt = peaksimport[['peakid','pkname']]
peaksfilt.columns = ['PEAKID','PeakName']

#Climber pnumbers rocessing
expedteam1 = expedselect2[['YEAR','PEAKID','TOTMEMBERS','SMTMEMBERS','TOTHIRED','SMTHIRED']]
expedteam1=expedteam1.groupby(['YEAR','PEAKID'],as_index = False).sum()
expedteam1['AllClimbersTotal']= expedteam1.iloc[:, 2:6].sum(axis=1)
expedteam = expedteam1[['PEAKID', 'AllClimbersTotal']]
expedteam2 = expedteam.groupby('PEAKID', as_index = False).sum()
expedL = expedteam2.nlargest(6, ['AllClimbersTotal'])
expedteam3=expedL.merge(expedteam1, left_on = ['PEAKID'], right_on=['PEAKID'], how = 'inner')
expedteam3 = expedteam3.sort_values('YEAR').loc[lambda expedteam3: expedteam3.YEAR > 2014]
expedteam4 = expedteam3[['PEAKID','YEAR','AllClimbersTotal_y']]
exped = expedteam4.merge(peaksfilt, on = 'PEAKID', how = 'inner').drop(['PEAKID'], axis = 1)

#Final Cleanup
exped.columns = ['Year','TotalClimbers', 'PeakName']
exped = exped.sort_values('PeakName', ascending = True)

#visualisation
output_file("bar_nested_colormapped.html")

PeakNames = exped.drop_duplicates(subset='PeakName')
PeakNames = PeakNames['PeakName'].tolist()
years = exped.drop_duplicates(subset='Year')
years = years['Year'].tolist()
PeakNames = ['Ama Dablam', 'Cho Oyu', 'Dhaulagiri I', 'Everest', 'Lhotse', 'Manaslu']
years = ['2015', '2016', '2017']

data = {'PeakNames' : PeakNames,
        '2015'   : [422, 61,10, 963, 138, 291],
        '2016'   : [680, 533,76, 1594, 72, 327],
        '2017'   : [609, 183,200, 1745, 204, 799]}

palette = ["#c9d9d3", "#718dbf", "#e84d60"]

# this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
x = [ (PeakName, year) for PeakName in PeakNames for year in years ]
counts = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=counts))

p = figure(x_range=FactorRange(*x), plot_height=350, title="Total Climbers - Mountain & Year", toolbar_location=None, tools="")

p.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
       fill_color=factor_cmap('x', palette=palette, factors=years, start=1, end=2))

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

show(p)

    


