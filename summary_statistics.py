# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 13:50:04 2019

@author: Mia Tran
"""

import pandas as pd
import numpy as np
def roundtostring(df, col):
    return round(df[col], 2).astype(str)

def value_freq(df, col):
    '''
    Return list of value, list of value_counts for col in df
    '''

    return [k for k,v in df[col].value_counts().items()], [v for k,v in df[col].value_counts().items()]

def createtable(df):

    t = df.describe().transpose()
    t['Mean (std)'] = roundtostring(t, 'mean') + ' (' + roundtostring(t,'std') + ')'
    t['Median (IQR)'] = roundtostring(t, '50%') \
                                + ' (' + roundtostring(t,'25%') +', '+ roundtostring(t,'75%') +')'
    t['Min-Max'] = ' (' + roundtostring(t,'min') +', '+ roundtostring(t,'max') +')'

    return t[['Mean (std)', 'Median (IQR)','Min-Max']]                           

def table_style(themecolor = 'standard'):
    '''
    Return style for table
    Styles to choose: ['standard', 'pink', 'green', 'blue']
    '''
    THEMEDICT = {'standard': 'grey', 'pink': '#F08080', 'green': '#3CB371', 'blue': '#20B2AA'}
    assert themecolor in THEMEDICT, "Unspecified themecolor. Choose from %s" %(list(THEMEDICT.keys()))
    return [\
    {'selector': 'tr :first-child', 'props': [('display', 'none')]}, \
    {'selector': 'tr:hover td', 'props': [('background-color',  'silver')]}, \
    {'selector': 'th, td', 'props': [('border', '0.054px solid silver'), \
                                     ('padding', '4px'), \
                                     ('text-align', 'center')]}, \
    {'selector': 'th', 'props': [('font-weight', 'normal'), ('color',THEMEDICT[themecolor]), ('font-family', 'Verdana')]}, \
    {'selector': 'td', 'props': [('color','grey'), ('font-family', 'Verdana')]}, \
    {'selector': 'caption', 'props': [('font-weight', 'bold'), ('color', THEMEDICT[themecolor]), ('text-align', 'center'), \
                                      ('font-size', '16px'), ('font-family', 'Verdana')]}, \
    {'selector': '', 'props': [('border-collapse', 'collapse'),\
                               ('border', '0.02px solid silver')]} \
    ]

def summarize_statistics_for_cont_data(df, col = None, cont=None, themecolor = 'standard', nonstyle = False, caption_prefix ='Data Summary'):
    '''
    Create table of summarized statistics for data (df) by feature (col)
    If col are not specified (by default), this function apply to the entire dataframe. 
    *** Suggested usage: This function is helpful for continuous data. 
        Run suggesting_column_types() first to find continuous columns (cont). 
    
    ---------------------------------------------
    Parameters:
    - dataframe: your dataframe of interest
    - col: variable name to stratify. e.g. 'Diseases'
    - cont: list of continuous variables
    - Caption prefixed: Specify the caption, by default 'Data Summary'
    - themecolor: a playful feature to choose how the table looks like
    '''
        
    if not col:
        col = 'all'
        df[col] = '' # a simple trick to create a placeholder column to loop through
        
    else: 
        assert col in df.columns, "Columns to stratify not in table! "
    
    if cont: 
        df = pd.concat([df[cont], df[col]], axis=1)
    df = df.loc[:,~df.columns.duplicated()] #remove dupplicated columns
    
    values, counts = value_freq(df, col)
    list_df = []
    subgroup = []
    for v, c in zip(values, counts):
        subgroup.append(col+'='+str(v) +' (N = ' + str(c) +')')
        subtable = (df[df[col]==v]).drop(columns=col)
        summarized_subtable = createtable(subtable)
        list_df.append(summarized_subtable)

    newdf = pd.concat(list_df, axis=1, keys=subgroup)#.swaplevel(0, 0, 1)#pd.concat(list_df, ignore_index=False, axis=1)
    newdf.index.name = 'Features'
    newdf = newdf.reset_index()
    
    if nonstyle:
        return newdf
    else:
        return newdf.style.set_table_styles(table_style(themecolor)).set_caption(caption_prefix +' by ' +col)


def suggesting_column_types(df, cutoff = 10):
    '''
    Help function to quickly identify categorical/continuous col. 
    Cutoff values is helpful when variables are continous/discretes 
    but the number of values are less than a cutoff value (e.g. 10) so that you want to
    use this variables as categorical variables instead. 
    
    Parameters
    --------------------------------------
    df: dataframe
    cutoff: cutoff value to decide whether category or continuous variables. Default is 10
    '''
    list_cat = []
    list_cont = []
    for col in df.columns:
        if len(value_freq(df, col)[0]) <=cutoff:
            list_cat.append(col)
        else: 
            list_cont.append(col)
    return list_cat, list_cont 

def statistics_for_cat_data(df, col = None, cats=None, themecolor = 'standard', caption_prefix ='Data Summary'):
    '''
    Create table of summarized statistics for data (df) by feature (col)
    If col are not specified (by default), this function apply to the entire dataframe. 
    *** Suggested usage: This function is helpful for categorical data. 
        Run suggesting_column_types() first to find categorical columns (cont). 
    
    ---------------------------------------------
    Parameters:
    - dataframe: your dataframe of interest
    - col: variable name to stratify. e.g. 'Diseases'
    - cont: list of continuous variables
    - Caption prefixed: Specify the caption, by default 'Data Summary'
    - themecolor: a playful feature to choose how the table looks like
    '''
    from termcolor import cprint    
    if not col:        
        col = 'all'
        df[col] = '' # a simple trick to create a placeholder column to loop through
    else: 
        assert col in df.columns, "Columns to stratify not in table! "
    
    
    if col: 
        df = pd.concat([df[cats], df[col]], axis=1)
    df = df.loc[:,~df.columns.duplicated()] #remove dupplicated columns
    
    list_df = []
    for cat in cats:
        row_temp = []
        if not col:
            values, counts = value_freq(df, cat)
            for v, c in zip(values, counts):
                
                row_temp.append([cat, v, c, round(c/sum(counts)*100,2)])
            
        if col: 
            for stratified_value in df[col].unique():
                values, counts = value_freq(df[df[col]==stratified_value], cat)
                for v, c in zip(values, counts):
                    row_temp.append([stratified_value, v, c, round(c/sum(counts)*100,2)])
        df_temp = pd.DataFrame(row_temp, columns = ['GROUP','VALUES', 'COUNT', 'PERCENT']).sort_values('COUNT', ascending = False)
        
        df_temp = df_temp.pivot(index = 'VALUES', columns = 'GROUP').swaplevel(0, 1, 1).sort_index(axis=1)
        df_temp['FEATURES'] = cat
        list_df.append(df_temp)

    
    newdf = pd.concat(list_df, axis=0)#, keys=['FEATURES' , 'VALUES', 'COUNT', 'PERCENT'])#.swaplevel(0, 0, 1)#pd.concat(list_df, ignore_index=False, axis=1)
    
    newdf = newdf.reset_index().set_index('FEATURES').reset_index().fillna(0)
    newdf = newdf.style.set_table_styles(table_style(themecolor)).set_caption(caption_prefix +' by ' +col)
    
    return newdf
statistics_for_cat_data(df, cats = cat_list, themecolor = 'blue')