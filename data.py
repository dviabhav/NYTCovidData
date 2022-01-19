import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import datetime as dt
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory
import matplotlib.pyplot as plt
import os
import time
start_time = time.time()
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#cases should be of the form Series
def splice_TS_weekly(case_TS, weekday = 0):
    df = pd.DataFrame(case_TS)
    df.reset_index(inplace = True)
    df['weekday'] = df.apply( lambda row: row.date.weekday(), axis = 1 )
    res = df.loc[df.weekday == weekday].set_index('date').cases
    return res

#######################################################################################################################
#######################################################################################################################
def select_top(cases, sum_list = 1, top = 10 ):
    temp = {}
    if type( list(cases.keys())[0] ) == pd.Timestamp:
        for time, val in cases.items():
            temp[str(time.date())] = [val]
        cases = temp
    net_cases = {}
    result = []
    for st in cases:
        if sum_list:
            net_cases[st] = sum(cases[st].dropna())
        else:
            net_cases[st] = cases[st][-1]
    order = list(net_cases.values())
    order.sort(reverse = True)
    if top > 0:
        result = [key for key, value in net_cases.items() if value in order[:top] ]
    else:
        result = [key for key, value in net_cases.items() if value in order[top:] ]
    return result

#######################################################################################################################
#######################################################################################################################
def download():
    start_time = time.time()
    print("Downloading data...\n")

    #####################################Source URLs#####################################
    US_data_source = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
    US_State_data_source = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    US_County_data_source = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    State_neighbors = 'https://raw.githubusercontent.com/ubikuity/List-of-neighboring-states-for-each-US-state/master/neighbors-states.csv'
    Postal_code = 'https://www.infoplease.com/us/postal-information/state-abbreviations-and-state-postal-codes'
    Global_data_source = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv"
    # WHO_Global_Data = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSe-8lf6l_ShJHvd126J-jGti992SUbNLu-kmJfx1IRkvma_r4DHi0bwEW89opArs8ZkSY5G2-Bc1yT/pub?gid=0&single=true&output=csv'

    #######################################US DATA#######################################
    raw_US = pd.read_csv(US_data_source, index_col = 'date',parse_dates = True).sort_index()
    fatality_rates_US = 100*raw_US.deaths/raw_US.cases

    #####################################US State DATA###################################
    raw_states = pd.read_csv(US_State_data_source, index_col = 'date', parse_dates = True).sort_index()

    population = pd.read_csv('state_population.csv').set_index('State')["Population estimate, July 1, 2019[2]"]

    pop_dict = dict(population)
    pop_dict['Virgin Islands'] = pop_dict['U.S. Virgin Islands']

    raw_states['cases per million'] = raw_states.apply(lambda row: 1000000*row.cases/pop_dict[row.state], axis = 1)
    raw_states['deaths per million'] = raw_states.apply(lambda row: 1000000*row.deaths/pop_dict[row.state], axis = 1)
    list_of_states = raw_states['state'].unique()

    #####################################US political data##############################
    df = pd.read_csv('party_affiliation.csv' )[['State', 'Party.1']]
    states_D = []
    states_R = []
    governors = pd.DataFrame()
    governors['State'] = df['State']
    governors['Party'] = df['Party.1']
    gov = governors.set_index('State').to_dict()['Party']
    for st, party in gov.items():
        if(party == 'Democratic'):
            states_D.append(st)
        else:
            states_R.append(st)

    US_state_neighbors = pd.read_csv(State_neighbors) #not used at the moment
    state_code = pd.read_html(Postal_code)[0][ ['Postal Code', 'State Name/District'] ].set_index('Postal Code').to_dict()

    ###################################US County DATA###################################
    raw_County = pd.read_csv(US_County_data_source, dtype = { 'fips' : str }, index_col = 'date', parse_dates = True).sort_index()
    raw_County.dropna(inplace = True)

    cty_population = pd.read_csv('county population.csv', encoding='cp1252',
                                 dtype = {'STATE' : str,
                                        'COUNTY': str },
                                 usecols = [ 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'POPESTIMATE2019' ]
                                )
    cty_population['fips'] = cty_population.apply(lambda row: ("0" + row.STATE)[-2:] + ("00" + row.COUNTY )[-3:], axis = 1 )
    cty_population = cty_population[['STNAME', 'CTYNAME', 'fips', 'POPESTIMATE2019' ]]
    cty_population.columns = ['state', 'county', 'fips', 'population']
    cty_population = cty_population.loc[cty_population.state != cty_population.county]
    cty_population = cty_population.set_index('fips')

    ###################################Global Data######################################
    raw_Global = pd.read_csv(Global_data_source,
                            ).groupby('Country/Region').sum().transpose()[2:]
    EU_nation = ["Austria", "Belgium", "Bulgaria", "Croatia", 
                 "Cyprus", "Czechia", "Denmark", "Estonia", 
                 "Finland", "France", "Germany", "Greece", 
                 "Hungary", "Ireland", "Italy", "Latvia", 
                 "Lithuania","Luxembourg", "Malta", "Netherlands", 
                 "Poland", "Portugal", "Romania", "Slovakia", 
                 "Slovenia", "Spain", "Sweden"]

    raw_Global['EU'] = 0
    for countries in EU_nation:
        raw_Global['EU'] = raw_Global[countries] + raw_Global['EU']

    raw_Global.index = pd.to_datetime(raw_Global.index)
    #population = pd.read_html('https://simple.wikipedia.org/wiki/List_of_U.S._states_by_population')[0].set_index(['State'])["Population estimate, July 1, 2019[2]"]

    #######################################################################################################################
    ###################################Initialise variables################################################################
    #######################################################################################################################
    new_weekly_cases_state = {}
    new_weekly_deaths_state = {}
    percent_weekly_cases = {}
    change_in_new_cases = {}
    new_cases_per_mil = {}
    new_death_per_mil = {}

    cases_D = {}
    cases_R = {}
    pop_D = 0
    pop_R = 0
    cases_D['Weekly Cases'] = 0
    cases_R['Weekly Cases'] = 0
    cases_D['Weekly Deaths'] = 0
    cases_R['Weekly Deaths'] = 0
    cases_D['cases per mil'] = 0
    cases_R['cases per mil'] = 0


    wk_cases_county = {}
    wk_deaths_county = {}
    cases_cty_thou = {}

    #######################################################################################################################
    #######################################################################################################################
    print("Parsing through data for US states and counties...")
    #######################################################################################################################
    #####################################Loop Around state and county data#################################################
    #######################################################################################################################
    for state in list_of_states: #loop over states
        if state in [ 'District of Columbia', 'Puerto Rico'] or ( pop_dict[state] < 500000):  
            continue #removing US territories

        #####################################Working on state data##################################################
        #print("Analyzing data for ", state)
        total_case = round(100*raw_states.loc[raw_states['state'] == state].cases[-1]/raw_US.cases[-1], 4)
        wk_cases_county[state] = {}
        wk_deaths_county[state] = {}

        new_weekly_cases_state[state] = raw_states.loc[raw_states['state'] == state].cases.diff(7)
        new_weekly_deaths_state[state] = raw_states.loc[raw_states['state'] == state].deaths.diff(7)
        new_cases_per_mil[state] = raw_states.loc[raw_states['state'] == state]['cases per million'].diff(7)
        new_death_per_mil[state] = raw_states.loc[raw_states['state'] == state]['deaths per million'].diff(7)
        percent_weekly_cases[state] = 100*new_weekly_cases_state[state]/raw_US.cases.diff(7)
        change_in_new_cases[state] = 100*new_cases_per_mil[state].diff(14)[-1]/new_cases_per_mil[state][-15]


        if(state in states_R):
            cases_R['Weekly Cases'] = cases_R['Weekly Cases'] + new_weekly_cases_state[state]
            cases_R['Weekly Deaths'] = cases_R['Weekly Deaths'] + new_weekly_deaths_state[state]
            pop_R = pop_R + pop_dict[state]
        else:
            if(state in states_D):
                cases_D['Weekly Cases'] = cases_D['Weekly Cases'] + new_weekly_cases_state[state]
                cases_D['Weekly Deaths'] = cases_D['Weekly Deaths'] + new_weekly_deaths_state[state]
                pop_D = pop_D + pop_dict[state]        

        #####################################Working on county data#################################################

        temp_county = raw_County.loc[raw_County.state == state]
        cases_cty_thou[state] = {}        
        for cnty in temp_county.county.unique():
            fip = temp_county.loc[temp_county.county == cnty].fips.unique()[0]
            if fip not in cty_population.index:
                print( "County not found: ", cnty, " in state:", state )
                continue
            wk_cases_county[state][cnty] = temp_county.loc[temp_county.county == cnty ].cases.diff(7)
            wk_deaths_county[state][cnty] = temp_county.loc[temp_county.county == cnty ].deaths.diff(7)
            cty_popu = cty_population.loc[fip].population
            cases_cty_thou[state][cnty] = 1000*wk_cases_county[state][cnty]/cty_popu


    cases_D['cases per mil'] = 1000000*cases_D['Weekly Cases']/pop_D
    cases_D['deaths per mil'] = 1000000*cases_D['Weekly Deaths']/pop_D
    cases_R['cases per mil'] = 1000000*cases_R['Weekly Cases']/pop_R
    cases_R['deaths per mil'] = 1000000*cases_R['Weekly Deaths']/pop_R

    print('\nData downloaded in ', round(time.time()-start_time, 2), " seconds")

    data = {'raw_US' : raw_US,
            'raw_states' : raw_states,
            'raw_County' : raw_County,
            'raw_Global' : raw_Global,
            'fatality_rates_US' : fatality_rates_US,
    #'EU' : EU,
            'EU_nation' : EU_nation,
            'cty_population' : cty_population,
            'pop_dict' : pop_dict,
            'states_D' : states_D,
            'states_R' : states_R,
            'US_state_neighbors' : US_state_neighbors,
            'state_code' : state_code,
            'new_weekly_cases_state' : new_weekly_cases_state,
            'new_weekly_deaths_state' : new_weekly_deaths_state,
            'percent_weekly_cases' : percent_weekly_cases,
            'change_in_new_cases' : change_in_new_cases,
            'new_cases_per_mil' : new_cases_per_mil,
            'new_death_per_mil' : new_death_per_mil,
            'cases_D' : cases_D,
            'cases_R' : cases_R,
            'pop_D' : pop_D,
            'pop_R' : pop_R,
            'wk_cases_county' : wk_cases_county,
            'wk_deaths_county': wk_deaths_county,
            'cases_cty_thou' : cases_cty_thou
           }
    return(data)