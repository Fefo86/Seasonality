# -*- coding: utf-8 -*-
"""
@autore: Federico Juvara
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import datetime 
from datetime import time
import streamlit as st
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import altair as alt
from vega_datasets import data
from streamlit import session_state as ss

#st.set_page_config(layout="wide")

#CACHE
@st.cache
def expensive_computation(a, b):
   # time.sleep(1)  # 👈 This makes the function take 2s to run
    return a * b
a = 2
b = 21
res = expensive_computation(a, b)
st.sidebar.write("Result:", res)

#TITLE
st.sidebar.title('Seasonals app')

#LAYOUT
col1,col2 = st.columns((0.7,4.3))

#UPLOAD FILE CSV
#uploaded_file = col1.file_uploader("Upload your input CSV file", type=["csv"])
#if not uploaded_file:
    #st.stop()
#df = pd.read_csv(uploaded_file)

path = "."
def file_selector(folder_path = "C:\\Users\\assav\\Streamlit"):
    filenames = os.listdir(folder_path)
    selected_filename = st.sidebar.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)
filename = file_selector()
st.sidebar.write('You selected `%s`' % filename)

#DATA WRANGLING
df = pd.read_csv(filename)
df.set_axis(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)
df = df.set_index(pd.to_datetime(df['Date']))
df.index = pd.to_datetime(df.index, format='%Y%m%d %H%M%S',  utc=True)
df.index = df.index.tz_localize(None)
df.index.rename('date', inplace=True)
df.drop(['Date'], axis=1, inplace=True)
#df = df.set_index("Date") 
#df.index = pd.to_datetime(df.index, format='%Y%m%d %H%M%S',  utc=True)
#df['time'] = pd.to_datetime(df.index, format=r'%Y-%m-%d_%H%M%S').time
#df['Returns'] = df['Close'].pct_change()
df['Close - Close[-1]'] = df['Close'] - df['Close'].shift()
df['Close - Open'] = df['Close'] - df['Open']
df['High - Low'] = df['High'] - df['Low']

#df = df.resample('60T', base=30).sum()

#UNITS
units = col1.selectbox("Unit", ('$', 'Point'), index=0)
#number input tick e valore tick
tick = col1.number_input("importo tick")
tickvalue = col1.number_input("valore tick in dollari/euro")
ticksxpoint = col1.number_input("tick per punto")
if units == "$":  
   #colonne di calcolo per valore tick
   df['Close - Close[-1]']= ((df['Close - Close[-1]']/tick)* tickvalue)
   df['Close - Open']= ((df['Close - Open']/tick)* tickvalue)
   df['High - Low']= ((df['High - Low']//tick)* tickvalue)  
else:
   df['Close - Close[-1]'] = (df['Close - Close[-1]']/tick)/ticksxpoint
   df['Close - Open'] = (df['Close - Open']/tick)/ticksxpoint
   df['High - Low'] = (df['High - Low']/tick)/ticksxpoint
    

df['Date'] = df.index.date
df['HH:MM'] = df.index.time
df['Hour'] = df.index.hour
df['Dayofweek'] = df.index.dayofweek
df['Day'] = df.index.day
df['Month'] = df.index.month
df['Year'] = df.index.year
df['Dayofyear'] = df.index.dayofyear
df['sessione']=np.where((df.Hour<8),"asia", np.where(((df.Hour>7) & (df.Hour<16)),"europa", "usa"))

#METRICS
stats = col1.selectbox(
     'Metrics',
     ('Close - Close[-1]', 'Close - Open', 'High - Low', 'High', 'Low', 'Volume'))

    
#STATS
statistics = col1.selectbox(
     'Stats',
     ('mean','sum','SD'))


df2 = df
#SLIDER YEARS
start = df.index.min()
end = df.index.max()
slider = st.sidebar.select_slider("Years range:", options=df.index.date, value=(start, end))
startyear, endyear = list(slider)[0], list(slider)[1]
df2 = df[((df.index.date >= startyear) & (df.index.date <= endyear))]

#SLIDER HOURS
start_time = datetime.time(00,0,0)
end_time = datetime.time(23,59,0)
#slider2 = col1.slider("Hours range:", min_value = start_time, max_value = end_time, value=(start_time, end_time))
slider2 = st.sidebar.slider("Hours range:", min_value = start_time, max_value = end_time, step = pd.Timedelta(minutes=1), value=(time(00, 00), time(23, 59)))
#startday, endday = list(slider2)[0], list(slider2)[1]
startday, endday = slider2[0], slider2[1]
df2 =  df2.between_time(startday,endday) 



#MESI DELL'ANNO
st.sidebar.text("MESE DELL'ANNO")

if 'msg' not in ss:
    ss.msg = ''

def ind_change():
    """Whenever there are changes to individual cb."""
    ss.sel = 'None'
    ss.msg = ''

def change():
    # If check all
    if ss.sel == 'Check All':
        # We can only check all if at least one is not checked.
        if not all(v for v in [ss.Gennaio, ss.Febbraio, ss.Marzo, ss.Aprile, ss.Maggio, ss.Giugno, ss.Luglio, ss.Agosto, ss.Settembre, ss.Ottobre, ss.Novembre, ss.Dicembre]):
            ss.Gennaio = True
            ss.Febbraio = True
            ss.Marzo = True
            ss.Aprile = True
            ss.Maggio = True
            ss.Giugno = True
            ss.Luglio = True
            ss.Agosto = True
            ss.Settembre = True
            ss.Ottobre = True
            ss.Novembre = True
            ss.Dicembre = True
            
            ss.sel = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot check all if all are already checked.'
    # Else if uncheck all
    elif ss.sel == 'Uncheck All':
        # We can only uncheck all if all are checked already.
        if all(v for v in [ss.Gennaio, ss.Febbraio, ss.Marzo, ss.Aprile, ss.Maggio, ss.Giugno, ss.Luglio, ss.Agosto, ss.Settembre, ss.Ottobre, ss.Novembre, ss.Dicembre]):
            ss.Gennaio = False
            ss.Febbraio = False
            ss.Marzo = False
            ss.Aprile = False
            ss.Maggio = False
            ss.Giugno = False
            ss.Luglio = False
            ss.Agosto = False
            ss.Settembre = False
            ss.Ottobre = False
            ss.Novembre = False
            ss.Dicembre = False
            
            ss.sel = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot uncheck all if all are not yet checked.'
    else:
        ss.msg = ''

gennaio = st.sidebar.checkbox('Gennaio', key='Gennaio', on_change=ind_change)
febbraio = st.sidebar.checkbox('Febbraio', key='Febbraio', on_change=ind_change)
marzo = st.sidebar.checkbox('Marzo', key='Marzo', on_change=ind_change)
aprile = st.sidebar.checkbox('Aprile', key='Aprile', on_change=ind_change)
maggio = st.sidebar.checkbox('Maggio', key='Maggio', on_change=ind_change)
giugno = st.sidebar.checkbox('Giugno', key='Giugno', on_change=ind_change)
luglio = st.sidebar.checkbox('Luglio', key='Luglio', on_change=ind_change)
agosto = st.sidebar.checkbox('Agosto', key='Agosto', on_change=ind_change)
settembre = st.sidebar.checkbox('Settembre', key='Settembre', on_change=ind_change)
ottobre = st.sidebar.checkbox('Ottobre', key='Ottobre', on_change=ind_change)
novembre = st.sidebar.checkbox('Novembre', key='Novembre', on_change=ind_change)
dicembre = st.sidebar.checkbox('Dicembre', key='Dicembre', on_change=ind_change)

if not gennaio:
    df2 = df2.drop(df2.loc[df2.index.month==1].index)
    
if not febbraio:
    df2 = df2.drop(df2.loc[df2.index.month==2].index)

if not marzo:
    df2 = df2.drop(df2.loc[df2.index.month==3].index)
    
if not aprile:
    df2 = df2.drop(df2.loc[df2.index.month==4].index)
    
if not maggio:
    df2 = df2.drop(df2.loc[df2.index.month==5].index)
    
if not giugno:
    df2 = df2.drop(df2.loc[df2.index.month==6].index)
    
if not luglio:
    df2 = df2.drop(df2.loc[df2.index.month==7].index)

if not agosto:
    df2 = df2.drop(df2.loc[df2.index.month==8].index)
    
if not settembre:
    df2 = df2.drop(df2.loc[df2.index.month==9].index)
    
if not ottobre:
    df2 = df2.drop(df2.loc[df2.index.month==10].index)
  
if not novembre:
    df2 = df2.drop(df2.loc[df2.index.month==11].index)
    
if not dicembre:
    df2 = df2.drop(df2.loc[df2.index.month==12].index)
    
    
st.sidebar.radio(
    'Select',
    ['None', 'Check All', 'Uncheck All'],
   
    key='sel',
    on_change=change
)
if ss.msg:
    st.error(ss.msg)
    





#GIORNI DEL MESE
st.sidebar.text('GIORNI DEL MESE')


def change2():
    # If check all
    if ss.sel2 == 'Check All':
        # We can only check all if at least one is not checked.
        if not all(v for v in [ss.G1, ss.G2, ss.G3, ss.G3, ss.G5, ss.G6, ss.G7, ss.G8, ss.G9, ss.G10, ss.G11, ss.G12, ss.G13, ss.G14, ss.G15, ss.G16, ss.G17, ss.G18, ss.G19, ss.G20, ss.G21, ss.G22, ss.G23, ss.G24, ss.G25, ss.G26, ss.G27, ss.G28, ss.G29, ss.G30, ss.G31]):
            ss.G1 = True
            ss.G2 = True
            ss.G3 = True
            ss.G4 = True
            ss.G5 = True
            ss.G6 = True
            ss.G7 = True
            ss.G8 = True
            ss.G9 = True
            ss.G10 = True
            ss.G11 = True
            ss.G12 = True
            ss.G13 = True
            ss.G14 = True
            ss.G15 = True
            ss.G16 = True
            ss.G17 = True
            ss.G18 = True
            ss.G19 = True
            ss.G20 = True
            ss.G21 = True
            ss.G22 = True
            ss.G23 = True
            ss.G24 = True
            ss.G25 = True
            ss.G26 = True
            ss.G27 = True
            ss.G28 = True
            ss.G29 = True
            ss.G30 = True
            ss.G31 = True
            
            ss.sel2 = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot check all if all are already checked.'
    # Else if uncheck all
    elif ss.sel2 == 'Uncheck All':
        # We can only uncheck all if all are checked already.
        if all(v for v in [ss.G1, ss.G2, ss.G3, ss.G3, ss.G5, ss.G6, ss.G7, ss.G8, ss.G9, ss.G10, ss.G11, ss.G12, ss.G13, ss.G14, ss.G15, ss.G16, ss.G17, ss.G18, ss.G19, ss.G20, ss.G21, ss.G22, ss.G23, ss.G24, ss.G25, ss.G26, ss.G27, ss.G28, ss.G29, ss.G30, ss.G31]):
            ss.G1 = False
            ss.G2 = False
            ss.G3 = False
            ss.G4 = False
            ss.G5 = False
            ss.G6 = False
            ss.G7 = False
            ss.G8 = False
            ss.G9 = False
            ss.G10 = False
            ss.G11 = False
            ss.G12 = False
            ss.G13 = False
            ss.G14 = False
            ss.G15 = False
            ss.G16 = False
            ss.G17 = False
            ss.G18 = False
            ss.G19 = False
            ss.G20 = False
            ss.G21 = False
            ss.G22 = False
            ss.G23 = False
            ss.G24 = False
            ss.G25 = False
            ss.G26 = False
            ss.G27 = False
            ss.G28 = False
            ss.G29 = False
            ss.G30 = False
            ss.G31 = False
            
            ss.sel2 = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot uncheck all if all are not yet checked.'
    else:
        ss.msg = ''


day1 = st.sidebar.checkbox('G1', key='G1', on_change=ind_change)
day2 = st.sidebar.checkbox('G2', key='G2', on_change=ind_change)
day3 = st.sidebar.checkbox('G3', key='G3', on_change=ind_change)
day4 = st.sidebar.checkbox('G4', key='G4', on_change=ind_change)
day5 = st.sidebar.checkbox('G5', key='G5', on_change=ind_change)
day6 = st.sidebar.checkbox('G6', key='G6', on_change=ind_change)
day7 = st.sidebar.checkbox('G7', key='G7', on_change=ind_change)
day8 = st.sidebar.checkbox('G8', key='G8', on_change=ind_change)
day9 = st.sidebar.checkbox('G9', key='G9', on_change=ind_change)
day10 = st.sidebar.checkbox('G10', key='G10', on_change=ind_change)
day11 = st.sidebar.checkbox('G11', key='G11', on_change=ind_change)
day12 = st.sidebar.checkbox('G12', key='G12', on_change=ind_change)
day13 = st.sidebar.checkbox('G13', key='G13', on_change=ind_change)
day14 = st.sidebar.checkbox('G14', key='G14', on_change=ind_change)
day15 = st.sidebar.checkbox('G15', key='G15', on_change=ind_change)
day16 = st.sidebar.checkbox('G16', key='G16', on_change=ind_change)
day17 = st.sidebar.checkbox('G17', key='G17', on_change=ind_change)
day18 = st.sidebar.checkbox('G18', key='G18', on_change=ind_change)
day19 = st.sidebar.checkbox('G19', key='G19', on_change=ind_change)
day20 = st.sidebar.checkbox('G20', key='G20', on_change=ind_change)
day21 = st.sidebar.checkbox('G21', key='G21', on_change=ind_change)
day22 = st.sidebar.checkbox('G22', key='G22', on_change=ind_change)
day23 = st.sidebar.checkbox('G23', key='G23', on_change=ind_change)
day24 = st.sidebar.checkbox('G24', key='G24', on_change=ind_change)
day25 = st.sidebar.checkbox('G25', key='G25', on_change=ind_change)
day26 = st.sidebar.checkbox('G26', key='G26', on_change=ind_change)
day27 = st.sidebar.checkbox('G27', key='G27', on_change=ind_change)
day28 = st.sidebar.checkbox('G28', key='G28', on_change=ind_change)
day29 = st.sidebar.checkbox('G29', key='G29', on_change=ind_change)
day30 = st.sidebar.checkbox('G30', key='G30', on_change=ind_change)
day31 = st.sidebar.checkbox('G31', key='G31', on_change=ind_change)

if not day1:
    df2 = df2.drop(df2.loc[df2.index.day==1].index)
    
if not day2:
    df2 = df2.drop(df2.loc[df2.index.day==2].index)

if not day3:
    df2 = df2.drop(df2.loc[df2.index.day==3].index)
    
if not day4:
    df2 = df2.drop(df2.loc[df2.index.day==4].index)

if not day5:
    df2 = df2.drop(df2.loc[df2.index.day==5].index)
    
if not day6:
    df2 = df2.drop(df2.loc[df2.index.day==6].index)

if not day7:
    df2 = df2.drop(df2.loc[df2.index.day==7].index)
    
if not day8:
    df2 = df2.drop(df2.loc[df2.index.day==8].index)

if not day9:
    df2 = df2.drop(df2.loc[df2.index.day==9].index)
    
if not day10:
    df2 = df2.drop(df2.loc[df2.index.day==10].index)

if not day11:
    df2 = df2.drop(df2.loc[df2.index.day==11].index)
    
if not day12:
    df2 = df2.drop(df2.loc[df2.index.day==12].index)

if not day13:
    df2 = df2.drop(df2.loc[df2.index.day==13].index)
    
if not day14:
    df2 = df2.drop(df2.loc[df2.index.day==14].index)

if not day15:
    df2 = df2.drop(df2.loc[df2.index.day==15].index)
    
if not day16:
    df2 = df2.drop(df2.loc[df2.index.day==16].index)

if not day17:
    df2 = df2.drop(df2.loc[df2.index.day==17].index)
    
if not day18:
    df2 = df2.drop(df2.loc[df2.index.day==18].index)

if not day19:
    df2 = df2.drop(df2.loc[df2.index.day==19].index)
    
if not day20:
    df2 = df2.drop(df2.loc[df2.index.day==20].index)

if not day21:
    df2 = df2.drop(df2.loc[df2.index.day==21].index)
    
if not day22:
    df2 = df2.drop(df2.loc[df2.index.day==22].index)

if not day23:
    df2 = df2.drop(df2.loc[df2.index.day==23].index)
    
if not day24:
    df2 = df2.drop(df2.loc[df2.index.day==24].index)

if not day25:
    df2 = df2.drop(df2.loc[df2.index.day==25].index)
    
if not day26:
    df2 = df2.drop(df2.loc[df2.index.day==26].index)

if not day27:
    df2 = df2.drop(df2.loc[df2.index.day==27].index)
    
if not day28:
    df2 = df2.drop(df2.loc[df2.index.day==28].index)

if not day29:
    df2 = df2.drop(df2.loc[df2.index.day==29].index)
    
if not day30:
    df2 = df2.drop(df2.loc[df2.index.day==30].index)

if not day31:
    df2 = df2.drop(df2.loc[df2.index.day==31].index)
    

st.sidebar.radio(
    'Select',
    ['None', 'Check All', 'Uncheck All'],
   
    key='sel2',
    on_change=change2
)
if ss.msg:
    st.error(ss.msg)
    






#GIORNI DELLA SETTIMANA
st.sidebar.text('GIORNI DELLA SETTIMANA')

def change3():
    # If check all
    if ss.sel3 == 'Check All':
        # We can only check all if at least one is not checked.
        if not all(v for v in [ss.Lunedì, ss.Martedì, ss.Mercoledì, ss.Giovedì, ss.Venerdì, ss.Sabato, ss.Domenica]):
            ss.Lunedì = True
            ss.Martedì = True
            ss.Mercoledì = True
            ss.Giovedì = True
            ss.Venerdì = True
            ss.Sabato = True
            ss.Domenica = True
            
            ss.sel3 = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot check all if all are already checked.'
    # Else if uncheck all
    elif ss.sel3 == 'Uncheck All':
        # We can only uncheck all if all are checked already.
        if all(v for v in [ss.Lunedì, ss.Martedì, ss.Mercoledì, ss.Giovedì, ss.Venerdì, ss.Sabato, ss.Domenica]):
            ss.Lunedì = False
            ss.Martedì = False
            ss.Mercoledì = False
            ss.Giovedì = False
            ss.Venerdì = False
            ss.Sabato = False
            ss.Domenica = False
            
            ss.sel3 = 'None'  # reset to None to be ready again
            ss.msg = ''
        else:
            ss.msg = 'You cannot uncheck all if all are not yet checked.'
    else:
        ss.msg = ''

monday = st.sidebar.checkbox('Lunedì', key='Lunedì', on_change=ind_change)
tuesday = st.sidebar.checkbox('Martedì', key='Martedì', on_change=ind_change)
wednesday = st.sidebar.checkbox('Mercoledì', key='Mercoledì', on_change=ind_change)
thursday = st.sidebar.checkbox('Giovedì', key='Giovedì', on_change=ind_change)
friday = st.sidebar.checkbox('Venerdì', key='Venerdì', on_change=ind_change)
saturday = st.sidebar.checkbox('Sabato', key='Sabato', on_change=ind_change)
sunday = st.sidebar.checkbox('Domenica', key='Domenica', on_change=ind_change)

if not monday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==0].index)
    
if not tuesday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==1].index)
    
if not wednesday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==2].index)
    
if not thursday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==3].index)
    
if not friday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==4].index)
    
if not saturday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==5].index)
 
if not sunday:
    df2 = df2.drop(df2.loc[df2.index.dayofweek==6].index)

st.sidebar.radio(
    'Select',
    ['None', 'Check All', 'Uncheck All'],
   
    key='sel3',
    on_change=change3
)
if ss.msg:
    st.error(ss.msg)




   
#GROUP BY
group = col1.selectbox(
     'Group by',
     ('HH:MM','HH:MM Day of week','HH:MM Day of month','HH:MM Month of year','HH:MM Year','Day','Day, Day of week','Day, Day of month','Day, Month of year','Day of week','Day of year'))

#hh:mm
if (group == 'HH:MM'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=df2.index.time).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=df2.index.time).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=df2.index.time).std()
       
if (group == 'HH:MM Day of week'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['HH:MM','Dayofweek']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['HH:MM','Dayofweek']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['HH:MM','Dayofweek']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2[stats]
    column_names = list(df2.columns)
    #column_names[0:8] = ['monday','tuesday','wednesday','Thursday','Friday','Saturday','Sunday']
    df2.columns = column_names
    #df2.columns = df2.columns.droplevel(-1)

if (group == 'HH:MM Day of month'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['HH:MM','Day']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['HH:MM','Day']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['HH:MM','Day']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

if (group == 'HH:MM Month of year'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['HH:MM','Month']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['HH:MM','Month']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['HH:MM','Month']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

if (group == 'HH:MM Year'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['HH:MM','Year']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['HH:MM','Year']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['HH:MM','Year']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

#day
if (group == 'Day'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=df2.index.date).mean()
    if (statistics == 'sum'):
       df2 = df2.groupby(by=df2.index.date).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=df2.index.date).std()

if (group == 'Day, Day of week'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['Date','Dayofweek']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['Date','Dayofweek']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['Date','Dayofweek']).std()
    df2 = df2.unstack(level=-1)
    df2 = df2.interpolate()
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

if (group == 'Day, Day of month'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['Date','Day']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['Date','Day']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['Date','Day']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2.interpolate()
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

if (group == 'Day, Month of year'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=['Date','Month']).mean() 
    if (statistics == 'sum'):
       df2 = df2.groupby(by=['Date','Month']).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=['Date','Month']).std()
    df2 = df2.unstack(level=-1) 
    df2 = df2.interpolate()
    df2 = df2[stats]
    column_names = list(df2.columns)
    df2.columns = column_names

if (group == 'Day of week'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=df2.index.dayofweek).mean()
       #df2.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if (statistics == 'sum'):
       df2 = df2.groupby(by=df2.index.dayofweek).sum()
       #df2.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if (statistics == 'SD'):
       df2 = df2.groupby(by=df2.index.dayofweek).std()
       #df2.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

if (group == 'Day of year'):
    if (statistics == 'mean'):
       df2 = df2.groupby(by=df2.index.dayofyear).mean()
    if (statistics == 'sum'):
       df2 = df2.groupby(by=df2.index.dayofyear).sum()
    if (statistics == 'SD'):
       df2 = df2.groupby(by=df2.index.dayofyear).std()

#CUMSUM
cumsum = col1.checkbox("Cumsum", value=False)    
if cumsum:
     df2 = df2.cumsum() 



#PLOT
plot = col1.radio("Chart type", ('Bar','Line'),index=1)

if (plot == 'Bar'):
 if (group == 'HH:MM Day of week') or (group == 'Day, Day of week'):
  import plotly.express as px
  fig = px.bar(df2, x=df2.index, y=df2.columns)
  newnames = {'0':'Monday', '1':'Tuesday', '2':'Wednesday', '3':'Thursday', '4':'Friday', '5':'Saturday', '6':'Sunday'}
  fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                   legendgroup = newnames[t.name],
                                   hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

 elif (group == 'HH:MM Day of month') or (group == 'Day, Day of month'):
  import plotly.express as px
  fig = px.bar(df2, x=df2.index, y=df2.columns)


 elif (group == 'HH:MM Month of year') or (group == 'Day, Month of year'):
  import plotly.express as px
  fig = px.bar(df2, x=df2.index, y=df2.columns)
  newnames = {'1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December'}
  fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                   legendgroup = newnames[t.name],
                                   hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

 elif (group == 'HH:MM Year'):
  import plotly.express as px
  fig = px.bar(df2, x=df2.index, y=df2.columns)
  

 else:
  import plotly.express as px
  fig = px.bar(df2, x=df2.index, y=df2[stats])



if (plot == 'Line'):
 if (group == 'HH:MM Day of week') or (group == 'Day, Day of week'):
  import plotly.express as px
  fig = px.line(df2, x=df2.index, y=df2.columns)
  newnames = {'0':'Monday', '1':'Tuesday', '2':'Wednesday', '3':'Thursday', '4':'Friday', '5':'Saturday', '6':'Sunday'}
  fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                   legendgroup = newnames[t.name],
                                   hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

 elif (group == 'HH:MM Day of month') or (group == 'Day, Day of month'):
  import plotly.express as px
  fig = px.line(df2, x=df2.index, y=df2.columns)


 elif (group == 'HH:MM Month of year') or (group == 'Day, Month of year'):
  import plotly.express as px
  fig = px.line(df2, x=df2.index, y=df2.columns)
  newnames = {'1':'January', '2':'February', '3':'March', '4':'April', '5':'May', '6':'June', '7':'July', '8':'August', '9':'September', '10':'October', '11':'November', '12':'December'}
  fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                   legendgroup = newnames[t.name],
                                   hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

 elif (group == 'HH:MM Year'):
  import plotly.express as px
  fig = px.line(df2, x=df2.index, y=df2.columns)
 
 else:
  fig = go.Figure([go.Scatter(x=df2.index, y=df2[stats])])
  
  
fig.layout.template = 'ggplot2'
fig.update_xaxes(showgrid=False, rangeslider_visible=True)
fig.update_yaxes(showgrid=False)
if (stats != 'Volume') and (units =='$'):
   fig.update_layout(yaxis_tickprefix = '$', yaxis_tickformat = ',.')
fig.update_layout(height=800)

plot1 = col2.plotly_chart(fig, height=800, use_container_width=True)

#plt = plt.hist(x, bins=50)

#st.sidebar.line_chart(df2)
#col2.write(df2)
