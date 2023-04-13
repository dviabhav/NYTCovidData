import streamlit as st
import pandas as pd
import numpy as np
import data
from data import select_top
import datetime as dt
import matplotlib.pyplot as plt

@st.cache_data
def download_cache(todays_date):
    return data.download(todays_date)

st.header("Covid data API uising streamlit")
data_load_state = st.text("Loading Data...")

todays_date = dt.date.today()
Data = download_cache(todays_date)

raw_US 	=	Data['raw_US']
raw_states 	=	Data['raw_states']
raw_County 	=	Data['raw_County']
raw_Global 	=	Data['raw_Global']
fatality_rates_US = Data['fatality_rates_US']
EU_nation 	=	Data['EU_nation']
cty_population 	=	Data['cty_population']
pop_dict 	=	Data['pop_dict']
states_D 	=	Data['states_D']
states_R 	=	Data['states_R']
US_state_neighbors 	=	Data['US_state_neighbors']
state_code 	=	Data['state_code']
new_weekly_cases_state 	=	Data['new_weekly_cases_state']
new_weekly_deaths_state 	=	Data['new_weekly_deaths_state']
percent_weekly_cases 	=	Data['percent_weekly_cases']
change_in_new_cases 	=	Data['change_in_new_cases']
new_cases_per_mil 	=	Data['new_cases_per_mil']
new_death_per_mil 	=	Data['new_death_per_mil']
cases_D 	=	Data['cases_D']
cases_R 	=	Data['cases_R']
pop_D 	=	Data['pop_D']
pop_R 	=	Data['pop_R']
wk_cases_county 	=	Data['wk_cases_county']
wk_deaths_county 	=	Data['wk_deaths_county']
cases_cty_thou 	=	Data['cases_cty_thou']

data_load_state.text("Done loading")

fig, ax = plt.subplots(figsize = (20, 10))
ax.plot(raw_US.cases[30:]/1000000, label = "US total (in millions)" )
#ax.set_yscale('log')
ax.grid(axis = 'y')
ax.legend()
ylim = ax.get_ylim()
ax.fill_between(raw_US.index[-150:], 0, raw_US.cases[-150:]/1000000, alpha = 0.1)

st.pyplot(fig)


fig, ax = plt.subplots(figsize = (20, 10))
ax.plot(raw_US.cases.diff(7)[30:]/10000, label = "US weekly cases (in ten thousands)" )
ax.plot(raw_Global.EU.diff(7)[30:]/10000, label = "EU weekly cases (in ten thousands)")
ax.plot((raw_US.cases.diff(7) - (new_weekly_cases_state['New York'] + new_weekly_cases_state['New Jersey'] ))[30:]/10000, 'r--', label = "US Cases without NY and NJ (in ten thousands)" )
ax.plot(((new_weekly_cases_state['New York'] + new_weekly_cases_state['New Jersey'] ))[:]/10000, 'rx' , label = "NY and NJ (in ten thousands)" )
#plt.plot(raw_Global['US'].diff(7), label = "Global" )
ax.grid(axis = 'y')
ax.legend()
ylim = ax.get_ylim()
ax.fill_between(raw_US.index[-15:], 0, raw_US.cases.diff(7)[-15:]/10000, alpha = 0.1)

st.pyplot(fig)

state_list = raw_states.state.unique()

state = st.selectbox('Select state', state_list)

st.line_chart(new_weekly_cases_state[state])
######################################################################################################
######################################################################################################
######################################################################################################
worst_cases = select_top( cases_cty_thou[state], sum_list = 1, top = 20 )

top_10 = pd.DataFrame()
for cnty in worst_cases:
    top_10[cnty] = wk_cases_county[state][cnty].dropna()
top_10.dropna(inplace = True)    

