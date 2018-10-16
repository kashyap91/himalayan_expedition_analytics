#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 19:21:10 2018

@author: kashyap
"""
#import numpy as np
import pandas as pd
from bokeh.layouts import row, widgetbox, layout
from bokeh.models import Select
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure
from bokeh.themes import Theme
from bokeh.models import Div
from bokeh.models.widgets import PreText


####data import and preparation
#exped import and prep
expedimport = pd.read_csv("/Users/kashyap/Desktop/exped.csv", sep = ',', header = 0, low_memory=False)
expedselect = expedimport[['PEAKID','SUCCESS1', 'SUCCESS2','SUCCESS3', 'SUCCESS4','TOTMEMBERS','SMTMEMBERS','MDEATHS','TOTHIRED','SMTHIRED','HDEATHS',]]
expedselect['TotalExpeditions']=1
expedselect.SUCCESS1 = expedselect.SUCCESS1.astype(int)
expedselect.SUCCESS2 = expedselect.SUCCESS2.astype(int)
expedselect.SUCCESS3 = expedselect.SUCCESS3.astype(int)
expedselect.SUCCESS4 = expedselect.SUCCESS4.astype(int)
expedselect2 = expedselect.groupby(['PEAKID'], as_index = False).sum()

#peak import and prep
peaksimport = pd.read_csv('/Users/kashyap/Desktop/peaks.csv',sep = ',', header=0, low_memory=False)
peaksfilt = peaksimport[['peakid','heightm','pkname']]
peaksfilt.columns = ['PEAKID', 'PeakHeightMeters','PeakName']
expedfilt=expedselect2.merge(peaksfilt, on = 'PEAKID', how = 'inner')

#success processing
expedsuc1 = expedfilt[['PEAKID', 'SUCCESS1', 'SUCCESS2', 'SUCCESS3','SUCCESS4','TotalExpeditions']]
expedsuc2=expedsuc1.groupby(['PEAKID'],as_index = False).sum()
expedsuc2['suctot']= expedsuc2.iloc[:, 1:5].sum(axis=1)
expedsuc2['SuccessPercent'] = (expedsuc2['suctot'] / expedsuc2['TotalExpeditions']) *100
expedsuc = expedsuc2[['PEAKID','SuccessPercent']]
expedfilt1 = pd.merge(expedfilt,expedsuc, left_on = ['PEAKID'], right_on=['PEAKID'], how = 'outer').drop(['SUCCESS1', 'SUCCESS2','SUCCESS3', 'SUCCESS4'], axis = 1)

#Climber pnumbers rocessing
expedteam1 = expedfilt1[['PEAKID','TOTMEMBERS','SMTMEMBERS','TOTHIRED','SMTHIRED']]
expedteam1=expedteam1.groupby(['PEAKID'],as_index = False).sum()
expedteam1['AllClimbersTotal']= expedteam1.iloc[:, 1:5].sum(axis=1)
expedteam1['MemberClimbersTotal']= expedteam1.iloc[:, 1:3].sum(axis=1)
expedteam1['HiredClimbersTotal']= expedteam1.iloc[:, 3:5].sum(axis=1)
expedteam = expedteam1[['PEAKID', 'AllClimbersTotal', 'MemberClimbersTotal', 'HiredClimbersTotal']]
expedfilt2=expedfilt1.merge(expedteam, left_on = ['PEAKID'], right_on=['PEAKID'], how = 'outer').drop(['TOTMEMBERS','SMTMEMBERS','TOTHIRED','SMTHIRED'], axis =1)

#Climber Death processing
expedfilt2['AllClimberDeaths']= expedfilt2.iloc[:, 1:3].sum(axis=1)
expeddeath1 = expedfilt2.drop(['SuccessPercent'],axis=1)
expeddeath2=expeddeath1.groupby(['PEAKID'],as_index = False).sum()
expeddeath2['AllClimberDeathPercent'] = (expeddeath2['AllClimberDeaths'] / expeddeath2['AllClimbersTotal']) *100
expeddeath2['MemberClimberDeathPercent'] = (expeddeath2['MDEATHS'] / expeddeath2['MemberClimbersTotal']) *100
expeddeath2['HiredClimberDeathPercent'] = (expeddeath2['HDEATHS'] / expeddeath2['HiredClimbersTotal']) *100
expeddeath3 = expeddeath2[['PEAKID','AllClimberDeathPercent','MemberClimberDeathPercent','HiredClimberDeathPercent']]
exped = expedfilt2.merge(expeddeath3, left_on = ['PEAKID'], right_on=['PEAKID'], how = 'outer').fillna(0).drop(['PEAKID','PeakName'], axis = 1)

#Final Cleanup

exped.columns = ['MemberClimberDeaths','HiredClimberDeaths','TotalExpeditions', 'PeakHeightMeters', 'ExpeditionSuccessPercent', 'TotalClimbers','TotalMemberClimbers','TotalHiredClimbers','TotalClimberDeaths','AllClimberDeathPercent','MemberClimberDeathPercent','HiredClimberDeathPercent']
maxVal = 100
exped = exped.where(exped['ExpeditionSuccessPercent'] <= maxVal, maxVal)
exped = exped.where(exped['HiredClimberDeathPercent'] <= maxVal, maxVal)
wrong_indexes = [76, 120, 148, 151, 235, 365, 366]
exped=exped.drop(wrong_indexes,axis='rows')

#visualisation

SIZES = list(range(6, 22, 3))
COLORS = Spectral5
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)

columns = sorted(exped.columns)
columns1 = ['PeakHeightMeters']
discrete = [x for x in columns if exped[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
continuous.remove('PeakHeightMeters')
columns.remove('PeakHeightMeters')

def create_figure():
    xs = exped[x.value].values
    ys = exped[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    p = figure(plot_height=600, plot_width=630, tools='pan,box_zoom,hover,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if size.value != 'None':
        if len(set(exped[size.value])) > N_SIZES:
            groups = pd.qcut(exped[size.value].values, N_SIZES, duplicates='drop')
        else:
            groups = pd.Categorical(exped[size.value])
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        if len(set(exped[color.value])) > N_SIZES:
            groups = pd.qcut(exped[color.value].values, N_COLORS, duplicates='drop')
        else:
            groups = pd.Categorical(exped[color.value])
        c = [COLORS[xx] for xx in groups.codes]
        
    p.circle(x=xs, y=ys, color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)

    return p

def update(attr, old, new):
    layout.children[1] = create_figure()
    

x = Select(title='X-Axis', value='PeakHeightMeters', options=columns1)
x.on_change('value', update)

y = Select(title='Y-Axis', value='TotalClimbers', options=columns)
y.on_change('value', update)
  
size = Select(title='Size', value='None', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='None', options=['None'] + continuous)
color.on_change('value', update)


theme = Theme(json={
    'attrs':{
    'Figure':{
        'background_fill_color': '#2F2F2F',
        'border_fill_color': '#2F2F2F',
        'outline_line_color': '#444444'
        },
    'Axis':{
        'axis_line_color': "white",
        'axis_label_text_color': "white",
        'major_label_text_color': "white",
        'major_tick_line_color': "white",
        'minor_tick_line_color': "white",
        'minor_tick_line_color': "white"
        },
    'Grid':{
        'grid_line_dash': [6, 4],
        'grid_line_alpha': .3
        },
    'Title':{
        'text_color': "white"
        }
     }   
   }) 

 
div = Div(text="<img src='App2/static/image2.png'>")
curdoc().add_root(div)
    
controls = widgetbox([x, y, color, size], width=200)
layout = row(controls, create_figure())
doc = curdoc()
doc.theme = theme
curdoc().add_root(layout)

div = PreText(text= "..............................................................................................................................")
curdoc().add_root(div)

div = Div(text="<img src='App2/static/image.png'>")
curdoc().add_root(div)
curdoc().title = "DataVis"
    


