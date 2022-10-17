import io
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import requests

# Path to current directory.
CURRENT_DIR = Path(__file__).parent
# Path to (public) directory where output datasets will be stored.
OUTPUT_DIR = CURRENT_DIR.parent / "datasets"
# Path to (public) directory where input files are stored.
INPUT_DIR = CURRENT_DIR.parent / "input"
# Path to output PIP dataset files.
OUTPUT_CSV_FILE = OUTPUT_DIR / "pip_dataset.csv"
OUTPUT_XLSX_FILE = OUTPUT_DIR / "pip_dataset.xlsx"
# Path to PIP dataset codebook file.
PIP_CODEBOOK_FILE = OUTPUT_DIR / "pip_codebook.csv"
# Path to (ignored) directory where temporary files will be stored.
TEMP_DIR = CURRENT_DIR.parent / "temp"
# Define temporary sub-folders that need to be created.
TEMP_SUB_DIRS = [
    TEMP_DIR / "ppp_2011/raw",
    TEMP_DIR / "ppp_2017/raw"
]
# Path to (ignored) directory where temporary plots will be stored.
GRAPHICS_DIR = CURRENT_DIR.parent / "graphics"
# Define PIP data version (which depends on the PPP version), to pass to the API.
PIP_VERSION = {
    2011: "20220909_2011_02_02_PROD",
    2017: "20220909_2017_01_02_PROD",
}
# Base URL of PIP API.
PIP_API_BASE_URL = "https://api.worldbank.org/pip/v1/"
# Google sheet names and base URL.
GOOGLE_SHEET_NAMES = {
    2011: "pip_ppp_2011",
    2017: "pip_ppp_2017",
}
GOOGLE_SHEET_ID = '1ntYtYF0NqIW2oXuXl_ZJHvuI7n-bik94BEIOvWHrJAI'
GOOGLE_SHEET_BASE_URL = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet='


def pip_query_country(popshare_or_povline, value, country_code="all", year="all", fill_gaps="true", welfare_type="all", reporting_level="all", ppp_version=2011):
    # Get PIP data version from PPP version.
    version = PIP_VERSION[ppp_version]
        
    # Build query
    request_url = f'{PIP_API_BASE_URL}pip?{popshare_or_povline}={value}&country={country_code}&year={year}&fill_gaps={fill_gaps}&welfare_type={welfare_type}&reporting_level={reporting_level}&ppp_version={ppp_version}&version={version}&format=csv'
    status = 0
    
    while status != 200:
        #df = pd.read_csv(request_url)
        response = requests.get(request_url, timeout=500)
        content = response.content
        status = response.status_code
    
    df = pd.read_csv(io.StringIO(content.decode('utf-8')))

    return df


# For world regions, the popshare query is not available (or rather, it returns nonsense).
def pip_query_region(povline, year="all", ppp_version=2011):
    # Get PIP data version from PPP version.
    version = PIP_VERSION[ppp_version]

    # Build query
    request_url = f'{PIP_API_BASE_URL}/pip-grp?country=all&povline={povline}&year={year}&ppp_version={ppp_version}&version={version}&group_by=wb&format=csv'
    status = 0
    
    while status != 200:
        #df = pd.read_csv(request_url)
        response = requests.get(request_url, timeout=500)
        content = response.content
        status = response.status_code
    
    df = pd.read_csv(io.StringIO(content.decode('utf-8')))
    df = df[df['reporting_year']>=1990].reset_index(drop=True)

    return df


# ## Get country data
# This code is to query poverty data from a poverty line (filled or not). Entities are standardised and returns multiple outputs, one raw file with all the results, one only for consumption, one only for income and one for income and consumption dropping duplicates.
def country_data(extreme_povline_cents, filled, ppp, additional_dfs=True):
    #Query for all the countries and for the poverty line defined (only non-filled data)
    df_country = pip_query_country(popshare_or_povline = "povline",
                                    country_code = "all",
                                    year = "all",
                                    welfare_type = "all",
                                    reporting_level = "all",
                                    value = extreme_povline_cents/100,
                                    fill_gaps=filled,
                                    ppp_version=ppp)

    df_country = df_country.rename(columns={'country_name': 'Entity', 'reporting_year': 'Year'})
    
    if additional_dfs:
        
        # Separate out consumption-only, income-only, and both dataframes
        df_country_inc = df_country[df_country['welfare_type']=="income"].reset_index(drop=True).copy()
        df_country_cons = df_country[df_country['welfare_type']=="consumption"].reset_index(drop=True).copy()

        df_country_inc_or_cons = df_country.copy()
        # If both inc and cons are available in a given year, drop inc

        # Flag duplicates – indicating multiple welfare_types
        #Sort values to ensure the welfare_type consumption is marked as False when there are multiple welfare types
        df_country_inc_or_cons.sort_values(by=['Entity', 'Year', 'reporting_level', 'welfare_type'], ignore_index=True, inplace=True)
        df_country_inc_or_cons['duplicate_flag'] = df_country_inc_or_cons.duplicated(subset=['Entity', 'Year', 'reporting_level'])

        #print(f'Checking the data for years with both income and consumption. Before dropping duplicated, there were {len(df_country_inc_or_cons)} rows...')
        # Drop income where income and consumption are available
        df_country_inc_or_cons = df_country_inc_or_cons[(df_country_inc_or_cons['duplicate_flag']==False) | (df_country_inc_or_cons['welfare_type']=='consumption')]
        df_country_inc_or_cons.drop(columns=['duplicate_flag'], inplace=True)

        #print(f'After dropping duplicates there were {len(df_country_inc_or_cons)} rows.')
        
        return df_country, df_country_inc, df_country_cons, df_country_inc_or_cons
    
    else:
        return df_country


# ## Regional data
# Returns standardised regional data
def regional_data(extreme_povline_cents, ppp):
    #Query for all the regions and for the poverty line defined
    df_region = pip_query_region(extreme_povline_cents/100, ppp_version=ppp)

    df_region = df_region.rename(columns={'region_name': 'Entity', 'reporting_year': 'Year'})

    return df_region


# ## Standardize entities
def standardize_entities(orig_df,
                        entity_mapping_url,
                        mapping_varname_raw,
                        mapping_vaname_owid,
                        data_varname_old,
                        data_varname_new):


    # Read in mapping table which maps PWT names onto OWID names.
    df_mapping = pd.read_csv(entity_mapping_url)

    # Merge in mapping to raw
    df_harmonized = pd.merge(orig_df,df_mapping,
      left_on=data_varname_old,right_on=mapping_varname_raw, how='left')
    
    # Drop the old entity names column, and the matching column from the mapping file
    df_harmonized = df_harmonized.drop(columns=[data_varname_old, mapping_varname_raw])
    
    # Rename the new entity column
    df_harmonized = df_harmonized.rename(columns={mapping_vaname_owid:data_varname_new})

    # Move the entity column to front:

    # get a list of columns
    cols = list(df_harmonized)
    
    # move the country column to the first in the list of columns
    cols.insert(0, cols.pop(cols.index(data_varname_new)))
    
    # reorder the columns of the dataframe according to the list
    df_harmonized = df_harmonized.loc[:, cols]

    return df_harmonized


# ## Querying poverty and non-poverty data from the PIP API

#Create a dataframe for each poverty line on the list, including and excluding interpolations and for countries and regions
#Each of these combinations are concatenated in a larger data frame.
def query_poverty(poverty_lines_cents, filled, ppp):

    print('Querying data from several poverty lines from the PIP API...')
    start_time = time.time()

    df_complete = pd.DataFrame()

    # Run the API query and clean the response...
    #... for each poverty line
    for p in poverty_lines_cents:
        
        p_dollar = p/100
        print(p_dollar)

        #.. and for both countries and WB regional aggregates
        for ent_type in ['country', 'region']:

            # Make the API query for country data
            if ent_type == 'country':
                
                df = country_data(p, filled, ppp, additional_dfs=False)

                # Keep only these variables:
                keep_vars = [ 
                    'Entity',
                    'Year',
                    'reporting_level',
                    'welfare_type', 
                    'headcount',
                    'poverty_gap',
                    'poverty_severity', 
                    'watts',
                    'reporting_pop'
                ]

            # Make the API query for region data
            # Note that the filled and not filled data is the same in this case .
            # The code runs it twice anyhow.
            if ent_type == 'region':
                
                df = regional_data(p, ppp)

                keep_vars = [ 
                    'Entity',
                    'Year',
                    'headcount',
                    'poverty_gap',
                    'poverty_severity',
                    'watts',
                    'reporting_pop'
                ]


            df = df[keep_vars]

            # rename columns
            df = df.rename(columns={
            'headcount':'headcount_ratio',
            'poverty_gap': 'poverty_gap_index'})


            # Calculate number in poverty
            df['headcount'] = df['headcount_ratio'] * df['reporting_pop']
            df['headcount'] = df['headcount'].round(0)

            # Calculate shortfall of incomes
            df['total_shortfall'] = df['poverty_gap_index'] * p_dollar * df['reporting_pop']                      

            # Calculate average shortfall of incomes (averaged across population in poverty)
            df['avg_shortfall'] = df['total_shortfall'] / df['headcount']

            # Calculate income gap ratio (according to Ravallion's definition)
            df['income_gap_ratio'] = (df['total_shortfall'] / df['headcount']) / p_dollar


            # Shares to percentages
            # executing the function over list of vars
            var_list = ['headcount_ratio', 'income_gap_ratio', 'poverty_gap_index' ]

            #df[var_list] = df[var_list].apply(multiply_by_100)
            df.loc[:, var_list] = df[var_list] * 100


            # Add poverty line as a var (I add the '_' character, because it being treated as a float later on was causing headaches)
            df['poverty line'] = f'_{p}'
            df['ent_type'] = ent_type

            #Concatenate all the results
            df_complete = pd.concat([df_complete, df],ignore_index=True)

    #I drop 'reporting_pop' for now to avoid it to get multiplied by all the poverty lines in the next section
    df_complete = df_complete.drop(columns=['reporting_pop'])
    df_complete.to_csv(TEMP_DIR / f'ppp_{ppp}/raw/multiple_povlines_long.csv', index=False)

    # Select data for countries 
    headcounts_country = df_complete[(df_complete['ent_type'] == 'country')].reset_index(drop=True)

    # Select data for regions
    headcounts_region = df_complete[(df_complete['ent_type'] == 'region')].reset_index(drop=True)

    #Create pivot tables to make the data wide
    headcounts_country_wide = headcounts_country.pivot_table(index=['Entity', 'Year', 'reporting_level', 'welfare_type'], 
                    columns='poverty line')

    headcounts_region_wide = headcounts_region.pivot_table(index=['Entity', 'Year'], 
                    columns='poverty line')

    #Join multi index columns
    headcounts_country_wide.columns = [''.join(col).strip() for col in headcounts_country_wide.columns.values]
    headcounts_country_wide = headcounts_country_wide.reset_index()

    headcounts_region_wide.columns = [''.join(col).strip() for col in headcounts_region_wide.columns.values]
    headcounts_region_wide = headcounts_region_wide.reset_index()

    #Concatenate country and regional wide datasets
    df_final = pd.concat([headcounts_country_wide, headcounts_region_wide], ignore_index=False)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    return df_final


def query_non_poverty(df_final, df_country, df_region):
    
    #Query the rest of the variables and merge
    
    print('Querying non poverty data and merge...')
    start_time = time.time()

    #Integrate variables not coming from multiple poverty lines

    #Keeping the non-poverty variables for countries
    df_country = df_country[['Entity', 'Year', 'reporting_level', 'welfare_type',
                                         'reporting_pop',
                                         'survey_year',
                                         'survey_comparability', 
                                         'comparable_spell', 
                                         'mean', 
                                         'median', 
                                         'mld',
                                         'gini', 
                                         'polarization', 
                                         'decile1', 'decile2', 'decile3', 'decile4','decile5', 
                                         'decile6', 'decile7', 'decile8', 'decile9', 'decile10',
                                         'cpi', 'ppp', 'reporting_gdp', 'reporting_pce', 
                                         'distribution_type', 'estimation_type']]

    #Changing the decile(i) variables for decile(i)_share
    for i in range(1,11):
        df_country = df_country.rename(columns={f'decile{i}': f'decile{i}_share'})


    #Keeping the non-poverty variables for regions
    df_region = df_region[['Entity', 'Year', 'reporting_pop', 'mean']]

    #Merge poverty variables with non-poverty country data
    df_final = pd.merge(df_final, df_country,
                        how='left', 
                        on=['Entity', 'Year', 'welfare_type', 'reporting_level'],
                        validate='many_to_one')

    #Merge poverty variables with non-poverty regional data
    df_final = pd.merge(df_final, df_region,
                        how='left', 
                        on=['Entity', 'Year'],
                        validate='many_to_one')

    #Fill mean and reporting_pop columns with regional data
    df_final['mean'] = np.where((df_final['mean_x'].isnull()) & ~(df_final['mean_y'].isnull()), df_final['mean_y'], df_final['mean_x'])
    df_final['reporting_pop'] = np.where((df_final['reporting_pop_x'].isnull()) & ~(df_final['reporting_pop_y'].isnull()), df_final['reporting_pop_y'], df_final['reporting_pop_x'])

    df_final = df_final.drop(columns=['mean_x', 'mean_y', 'reporting_pop_x', 'reporting_pop_y'])
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    return df_final


def integrate_relative_poverty(df_final, df_country, answer, ppp):
    
    relative_poverty_lines = [40, 50, 60]
    
    if answer:
        print("Generating relative poverty values... (takes about 1.5 hours)")
        start_time = time.time()
        df = median_patch(df_country, ppp)
        
        for pct in relative_poverty_lines:
            df[f'median_{pct}'] = df['median'] * pct/100
            
        generate_relative_poverty(df, relative_poverty_lines, ppp)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'Done. Execution time: {elapsed_time/60} minutes')
    
    print('Integrating relative poverty data...')
    start_time = time.time()
    df_relative = pd.read_csv(TEMP_DIR / f'ppp_{ppp}/raw/relative_poverty.csv')

    df_final = pd.merge(df_final, df_relative, 
                        how='left', on=['Entity', 'Year', 'reporting_level', 'welfare_type'])

    #Save the relative poverty variables to order the final output
    col_relative = list(df_relative.columns)
    col_relative = [e for e in col_relative if e not in ['Entity', 'Year', 'reporting_level', 'welfare_type']]

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    
    return df_final, col_relative


def generate_relative_poverty(df, relative_poverty_lines, ppp):

    # Initialise list to fill with headcount (ratio) data for 40%, 50% and 60% of the median
    headcount_40_list = []
    headcount_50_list = []
    headcount_60_list = []

    pgi_40_list = []
    pgi_50_list = []
    pgi_60_list = []

    pov_severity_40_list = []
    pov_severity_50_list = []
    pov_severity_60_list = []

    watts_40_list = []
    watts_50_list = []
    watts_60_list = []

    # For each row of the dataset
    for i in range(len(df)):
        
        print(f'Generating relative poverty values for {df.country_code[i]} ({df.Year[i]})...')

        # Run 3 queries, one for each relative poverty line, to get the headcount (ratio)
        df_query_40 = pip_query_country(popshare_or_povline = "povline",
                                        country_code = df['country_code'][i],
                                        year = df['Year'][i],
                                        welfare_type = df['welfare_type'][i],
                                        reporting_level = df['reporting_level'][i],
                                        value = df['median_40'][i],
                                        fill_gaps="false",
                                        ppp_version=ppp)

        df_query_50 = pip_query_country(popshare_or_povline = "povline",
                                        country_code = df['country_code'][i],
                                        year = df['Year'][i],
                                        welfare_type = df['welfare_type'][i],
                                        reporting_level = df['reporting_level'][i],
                                        value = df['median_50'][i],
                                        fill_gaps="false",
                                        ppp_version=ppp)

        df_query_60 = pip_query_country(popshare_or_povline = "povline",
                                        country_code = df['country_code'][i],
                                        year = df['Year'][i],
                                        welfare_type = df['welfare_type'][i],
                                        reporting_level = df['reporting_level'][i],
                                        value = df['median_60'][i],
                                        fill_gaps="false",
                                        ppp_version=ppp)

        # If there is no error, get the headcount value and append it to a list
        try:
            headcount_40_value = df_query_40['headcount'][0]
            headcount_40_list.append(headcount_40_value)
            pgi_40_value = df_query_40['poverty_gap'][0]
            pgi_40_list.append(pgi_40_value)
            pov_severity_40_value = df_query_40['poverty_severity'][0]
            pov_severity_40_list.append(pov_severity_40_value)
            watts_40_value = df_query_40['watts'][0]
            watts_40_list.append(watts_40_value)

            headcount_50_value = df_query_50['headcount'][0]
            headcount_50_list.append(headcount_50_value)
            pgi_50_value = df_query_50['poverty_gap'][0]
            pgi_50_list.append(pgi_50_value)
            pov_severity_50_value = df_query_50['poverty_severity'][0]
            pov_severity_50_list.append(pov_severity_50_value)
            watts_50_value = df_query_50['watts'][0]
            watts_50_list.append(watts_50_value)

            headcount_60_value = df_query_60['headcount'][0]
            headcount_60_list.append(headcount_60_value)
            pgi_60_value = df_query_60['poverty_gap'][0]
            pgi_60_list.append(pgi_60_value)
            pov_severity_60_value = df_query_60['poverty_severity'][0]
            pov_severity_60_list.append(pov_severity_60_value)
            watts_60_value = df_query_60['watts'][0]
            watts_60_list.append(watts_60_value)

        # If there is an error, append a null value to the list
        except:
            headcount_40_list.append(np.nan)
            pgi_40_list.append(np.nan)
            pov_severity_40_list.append(np.nan)
            watts_40_list.append(np.nan)

            headcount_50_list.append(np.nan)
            pgi_50_list.append(np.nan)
            pov_severity_50_list.append(np.nan)
            watts_50_list.append(np.nan)

            headcount_60_list.append(np.nan)
            pgi_60_list.append(np.nan)
            pov_severity_60_list.append(np.nan)
            watts_60_list.append(np.nan)


    # The lists converted into new columns
    df['headcount_ratio_40_median'] = headcount_40_list
    df['headcount_ratio_50_median'] = headcount_50_list
    df['headcount_ratio_60_median'] = headcount_60_list

    df['poverty_gap_index_40_median'] = pgi_40_list
    df['poverty_gap_index_50_median'] = pgi_50_list
    df['poverty_gap_index_60_median'] = pgi_60_list

    df['poverty_severity_40_median'] = pov_severity_40_list
    df['poverty_severity_50_median'] = pov_severity_50_list
    df['poverty_severity_60_median'] = pov_severity_60_list

    df['watts_40_median'] = watts_40_list
    df['watts_50_median'] = watts_50_list
    df['watts_60_median'] = watts_60_list

    for pct in relative_poverty_lines:
        df[f'headcount_{pct}_median'] = df[f'headcount_ratio_{pct}_median'] * df['reporting_pop']
        df[f'headcount_{pct}_median'] = df[f'headcount_{pct}_median'].round(0)
        df[f'total_shortfall_{pct}_median'] = df[f'poverty_gap_index_{pct}_median'] * df[f'median_{pct}'] * df['reporting_pop']
        df[f'avg_shortfall_{pct}_median'] = df[f'total_shortfall_{pct}_median'] / df[f'headcount_{pct}_median']
        df[f'income_gap_ratio_{pct}_median'] = (df[f'total_shortfall_{pct}_median'] / df[f'headcount_{pct}_median']) / df[f'median_{pct}']
        df[f'headcount_ratio_{pct}_median'] = df[f'headcount_ratio_{pct}_median'] * 100
        df[f'income_gap_ratio_{pct}_median'] = df[f'income_gap_ratio_{pct}_median'] * 100
        df[f'poverty_gap_index_{pct}_median'] = df[f'poverty_gap_index_{pct}_median'] * 100

    #Calculate numbers in poverty between pov lines for stacked area charts
    #Make sure the poverty lines are in order, lowest to highest
    relative_poverty_lines.sort()

    col_stacked_n = []
    col_stacked_pct = []

    #For each poverty line in relative_poverty_lines
    for i in range(len(relative_poverty_lines)):
        #if it's the first value only get people below this poverty line (and percentage)
        if i == 0:
            varname_n = f'headcount_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_n] = df[f'headcount_{relative_poverty_lines[i]}_median']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_pct] = df[varname_n] / df['reporting_pop']
            col_stacked_pct.append(varname_pct)

        #If it's the last value calculate the people between this value and the previous 
        #and also the people over this poverty line (and percentages)
        elif i == len(relative_poverty_lines)-1:

            varname_n = f'headcount_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_n] = df[f'headcount_{relative_poverty_lines[i]}_median'] - df[f'headcount_{relative_poverty_lines[i-1]}_median']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_pct] = df[varname_n] / df['reporting_pop']
            col_stacked_pct.append(varname_pct)

            varname_n = f'headcount_stacked_above_{relative_poverty_lines[i]}_median'
            df[varname_n] = df['reporting_pop'] - df[f'headcount_{relative_poverty_lines[i]}_median']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_above_{relative_poverty_lines[i]}_median'
            df[varname_pct] = df[varname_n] / df['reporting_pop']
            col_stacked_pct.append(varname_pct)

        #If it's any value between the first and the last calculate the people between this value and the previous (and percentage)
        else:
            varname_n = f'headcount_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_n] = df[f'headcount_{relative_poverty_lines[i]}_median'] - df[f'headcount_{relative_poverty_lines[i-1]}_median']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{relative_poverty_lines[i]}_median'
            df[varname_pct] = df[varname_n] / df['reporting_pop']
            col_stacked_pct.append(varname_pct)

    df.loc[:, col_stacked_pct] = df[col_stacked_pct] * 100
    
    
    col_povlines = []
    col_headcount = []
    col_headcount_ratio = []
    col_pgi = []
    col_severity = []
    col_watts = []
    col_total_shortfall = []
    col_avg_shortfall = []
    col_income_gap_ratio = []

    for pct in relative_poverty_lines:
        col_povlines.append(f'median_{pct}')
        col_headcount.append(f'headcount_{pct}_median')
        col_headcount_ratio.append(f'headcount_ratio_{pct}_median')
        col_pgi.append(f'poverty_gap_index_{pct}_median')
        col_severity.append(f'poverty_severity_{pct}_median')
        col_watts.append(f'watts_{pct}_median')
        col_total_shortfall.append(f'total_shortfall_{pct}_median')
        col_avg_shortfall.append(f'avg_shortfall_{pct}_median')
        col_income_gap_ratio.append(f'income_gap_ratio_{pct}_median')

    df = df[['Entity', 'Year', 'reporting_level', 'welfare_type'] + col_povlines + col_headcount + col_headcount_ratio + col_pgi + col_total_shortfall + col_avg_shortfall + col_income_gap_ratio + col_severity + col_watts + col_stacked_n + col_stacked_pct]
    df.to_csv(TEMP_DIR / f'ppp_{ppp}/raw/relative_poverty.csv', index=False)


def thresholds(df_final, answer, ppp):
    #Decile thresholds

    if answer:
        print("Generating percentile values... (takes about 1.5 DAYS)")
        start_time = time.time()
        # Define list of poverty lines to query (max 500 requests per category)

        under_5_dollars = list(range(1,500, 1))
        between_5_and_10_dollars = list(range(500,1000, 1))
        between_10_and_20_dollars = list(range(1000,2000, 2))
        between_20_and_30_dollars = list(range(2000,3000, 2))
        between_30_and_55_dollars = list(range(3000,5500, 5))
        between_55_and_80_dollars = list(range(5500,8000, 5))
        between_80_and_100_dollars = list(range(8000,10000, 5))
        between_100_and_150_dollars = list(range(10000,15000, 10))
        between_150_and_175_dollars = list(range(15000,17500, 10))

        #Define dictionary to iterate with
        povline_list_dict = {
            'under_5_dollars': under_5_dollars, 
            'between_5_and_10_dollars': between_5_and_10_dollars,
            'between_10_and_20_dollars': between_10_and_20_dollars,
            'between_20_and_30_dollars': between_20_and_30_dollars,
            'between_30_and_55_dollars': between_30_and_55_dollars,
            'between_55_and_80_dollars': between_55_and_80_dollars,
            'between_80_and_100_dollars': between_80_and_100_dollars,
            'between_100_and_150_dollars': between_100_and_150_dollars,
            'between_150_and_175_dollars': between_150_and_175_dollars
                           }
        
        df_closest_complete = generate_percentiles_countries(povline_list_dict, ppp)
        df_closest_complete_regions = generate_percentiles_regions(povline_list_dict, ppp)
        df_percentiles = pd.concat([df_closest_complete, df_closest_complete_regions], ignore_index=True)
        df_percentiles = df_percentiles.rename(columns={'poverty_line': 'percentile_value'})
        
        #Export concatenation
        df_percentiles.to_csv(TEMP_DIR / f'ppp_{ppp}/raw/percentiles.csv', index=False)
        #To use it in PIP issues
        # df_percentiles.to_csv(f'notebooks/percentiles_ppp_{ppp}.csv', index=False)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'Done. Total execution time for percentile generation: {elapsed_time/3600} hours')

    print('Integrating decile thresholds...')
    start_time = time.time()
    df_percentiles = pd.read_csv(TEMP_DIR / f'ppp_{ppp}/raw/percentiles.csv')
    deciles = []

    for i in range(10,100,10):
        deciles.append(f'P{i}')

    df_percentiles = df_percentiles[df_percentiles['target_percentile'].isin(deciles)].reset_index(drop=True)
    df_percentiles = pd.pivot(df_percentiles, 
                              index=['Entity', 'Year', 'reporting_level', 'welfare_type'], 
                              columns='target_percentile', 
                              values='percentile_value').reset_index()

    for i in range(10,100,10):
        df_percentiles = df_percentiles.rename(columns={f'P{i}': f'decile{int(i/10)}_thr'})

    df_final = pd.merge(df_final, df_percentiles, 
                        how='left', 
                        on=['Entity', 'Year', 'welfare_type', 'reporting_level'],
                        validate='many_to_one')

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    return df_final


def generate_percentiles_countries(povline_list_dict, ppp):

    start_time_overall = time.time()
    query_durations = {"povline":[],"duration":[]}

    for key in povline_list_dict:

        df_complete = pd.DataFrame()

        for povline in povline_list_dict[key]:

            start_time = time.time()

            povline_dollars = povline/100
            print(f'Fetching country headcounts for: ${povline_dollars} a day')

            df = country_data(povline, filled="false", ppp=ppp, additional_dfs=False)
            df_complete = pd.concat([df_complete, df],ignore_index=True)

            end_time = time.time()
            query_durations["povline"].append(povline_dollars)
            query_durations["duration"].append(end_time - start_time)


        #Write the complete data to csv
        df_complete.to_csv(TEMP_DIR / f'ppp_{ppp}/full_dist/{key}.csv', index=False)

    end_time_overall = time.time()
    elapsed_time_overall = end_time_overall - start_time_overall
    print(f'Execution time: {elapsed_time_overall/3600} hours')

    # Take a look at how long each query took
    df_query_durations = pd.DataFrame.from_dict(query_durations)
    fig = px.line(df_query_durations, x="povline", y="duration", title=f'Execution time for poverty line queries')
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/time_plot.svg')
    
    df_complete = pd.DataFrame()
    for key in povline_list_dict:
        df = pd.read_csv(TEMP_DIR / f'ppp_{ppp}/full_dist/{key}.csv')
        df_complete = pd.concat([df_complete, df], ignore_index=True)

    # Find closest to percentiles
    print("Find closest to percentiles after the extraction")
    start_time = time.time()

    percentiles = range(1, 100, 1)
    df_closest_complete = pd.DataFrame()

    for p in percentiles:
        df_complete['distance_to_p'] = abs(df_complete['headcount']-p/100)
        df_closest = df_complete.sort_values("distance_to_p").groupby(['Entity', 'Year','reporting_level','welfare_type'], as_index=False).first()
        df_closest['target_percentile'] = f'P{p}'
        df_closest = df_closest[['Entity', 'Year','reporting_level','welfare_type', 'target_percentile', 'poverty_line', 'headcount', 'distance_to_p']]
        df_closest_complete = pd.concat([df_closest_complete, df_closest],ignore_index=True)

    end_time = time.time()
    print(f'Execution time: {(end_time - start_time)/60} minutes')

    #Charts to check results
    fig = px.scatter(df_closest_complete, x="target_percentile", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year'], opacity=0.5,
                     title="<b>Target p vs. Distance to p</b><br>Percentiles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_percentiles.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_percentiles.html')

    fig = px.scatter(df_closest_complete, x="poverty_line", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year', 'target_percentile'], opacity=0.5,
                     title="<b>Poverty line vs. Distance to p</b><br>Percentiles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_percentiles.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_percentiles.html')

    fig = px.histogram(df_closest_complete, x="distance_to_p", histnorm="percent", marginal="box")
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/distance_percentiles_histogram.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/distance_percentiles_histogram.html')

    deciles = []

    for i in range(10,100,10):
        deciles.append(f'P{i}')

    df_closest_deciles = df_closest_complete[df_closest_complete['target_percentile'].isin(deciles)].copy().reset_index(drop=True)

    fig = px.scatter(df_closest_deciles, x="target_percentile", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year'], opacity=0.5,
                     title="<b>Target p vs. Distance to p</b><br>Deciles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_deciles.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_deciles.html')

    fig = px.scatter(df_closest_deciles, x="poverty_line", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year', 'target_percentile'], opacity=0.5,
                     title="<b>Poverty line vs. Distance to p</b><br>Deciles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_deciles.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_deciles.html')

    fig = px.histogram(df_closest_deciles, x="distance_to_p", histnorm="percent", marginal="box")
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/distance_deciles_histogram.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/distance_deciles_histogram.html')

    df_closest_complete.to_csv(TEMP_DIR / f'ppp_{ppp}/full_dist/percentiles_countries.csv', index=False)
    
    return df_closest_complete


def generate_percentiles_regions(povline_list_dict, ppp):

    start_time_overall = time.time()
    query_durations_regions = {"povline":[],"duration":[]}

    for key in povline_list_dict:

        df_complete_regions = pd.DataFrame()

        for povline in povline_list_dict[key]:

            start_time = time.time()

            povline_dollars = povline/100
            print(f'Fetching regional headcounts for: ${povline_dollars} a day')

            df = regional_data(povline, ppp)
            df_complete_regions = pd.concat([df_complete_regions, df],ignore_index=True)

            end_time = time.time()
            query_durations_regions["povline"].append(povline_dollars)
            query_durations_regions["duration"].append(end_time - start_time)


        #Write the complete data to csv
        df_complete_regions.to_csv(TEMP_DIR / f'ppp_{ppp}/full_dist_regions/{key}_regions.csv', index=False)

    end_time_overall = time.time()
    elapsed_time_overall = end_time_overall - start_time_overall
    print(f'Execution time: {elapsed_time_overall/3600} hours')

    # Take a look at how long each query took
    df_query_durations_regions = pd.DataFrame.from_dict(query_durations_regions)

    fig = px.line(df_query_durations_regions, x="povline", y="duration", title=f'Execution time for poverty line queries (regions)')

    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/time_plot_regions.svg')
    
    df_complete_regions = pd.DataFrame()
    for key in povline_list_dict:
        df = pd.read_csv(TEMP_DIR / f'ppp_{ppp}/full_dist_regions/{key}_regions.csv')
        df_complete_regions = pd.concat([df_complete_regions, df], ignore_index=True)

    # Find closest to percentiles

    start_time = time.time()

    percentiles = range(1, 100, 1)

    df_closest_complete_regions = pd.DataFrame()

    for p in percentiles:

        df_complete_regions['distance_to_p'] = abs(df_complete_regions['headcount']-p/100)

        df_closest = df_complete_regions.sort_values("distance_to_p").groupby(['Entity', 'Year'], as_index=False).first()

        df_closest['target_percentile'] = f'P{p}'

        df_closest = df_closest[['Entity', 'Year', 'target_percentile', 'poverty_line', 'headcount', 'distance_to_p']]

        df_closest_complete_regions = pd.concat([df_closest_complete_regions, df_closest],ignore_index=True)

    end_time = time.time()
    print(f'Execution time: {end_time - start_time} seconds')

    fig = px.scatter(df_closest_complete_regions, x="target_percentile", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year'], opacity=0.5,
                     title="<b>Target p vs. Distance to p for regions</b><br>Percentiles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_percentiles_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_percentiles_regions.html')

    fig = px.scatter(df_closest_complete_regions, x="poverty_line", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year', 'target_percentile'], opacity=0.5,
                     title="<b>Poverty line vs. Distance to p for regions</b><br>Percentiles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_percentiles_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_percentiles_regions.html')

    fig = px.histogram(df_closest_complete_regions, x="distance_to_p", histnorm="percent", marginal="box")
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/distance_percentiles_histogram_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/distance_percentiles_histogram_regions.html')

    deciles = []

    for i in range(10,100,10):
        deciles.append(f'P{i}')

    df_closest_deciles_regions = df_closest_complete_regions[df_closest_complete_regions['target_percentile'].isin(deciles)].copy().reset_index(drop=True)

    fig = px.scatter(df_closest_deciles_regions, x="target_percentile", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year'], opacity=0.5,
                     title="<b>Target p vs. Distance to p for regions</b><br>Deciles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_deciles_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/target_p_vs_distance_deciles_regions.html')

    fig = px.scatter(df_closest_deciles_regions, x="poverty_line", y="distance_to_p", color="Entity",
                     hover_data=['poverty_line', 'headcount', 'Year', 'target_percentile'], opacity=0.5,
                     title="<b>Poverty line vs. Distance to p for regions</b><br>Deciles",
                     log_y=False,
                     height=600)
    fig.update_traces(marker=dict(size=10, line=dict(width=0, color='blue')))
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_deciles_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/povline_vs_distance_deciles_regions.html')

    fig = px.histogram(df_closest_deciles_regions, x="distance_to_p", histnorm="percent", marginal="box")
    fig.write_image(GRAPHICS_DIR / f'ppp_{ppp}/distance_deciles_histogram_regions.svg')
    fig.write_html(GRAPHICS_DIR / f'ppp_{ppp}/distance_deciles_histogram_regions.html')

    df_closest_complete_regions.to_csv(TEMP_DIR / f'ppp_{ppp}/full_dist_regions/percentiles_regions.csv', index=False)
    
    return df_closest_complete_regions


# ## Data transformations
def additional_variables_and_check(df_final, poverty_lines_cents, col_relative, ppp):
    
    #Define groups of columns
    col_ids = ['Entity', 'Year', 'reporting_level', 'welfare_type']
    col_avg_shortfall = []
    col_headcount = []
    col_headcount_ratio = []
    col_incomegap = []
    col_povertygap = []
    col_tot_shortfall = []
    col_poverty_severity = []
    col_watts = []
    col_central = ['mean', 'median', 'reporting_pop']
    col_extra = ['survey_year', 'survey_comparability', 'comparable_spell', 'distribution_type', 'estimation_type',
                'cpi', 'ppp', 'reporting_gdp', 'reporting_pce']

    for i in range(len(poverty_lines_cents)):
        col_avg_shortfall.append(f'avg_shortfall_{poverty_lines_cents[i]}')
        col_headcount.append(f'headcount_{poverty_lines_cents[i]}')
        col_headcount_ratio.append(f'headcount_ratio_{poverty_lines_cents[i]}')
        col_incomegap.append(f'income_gap_ratio_{poverty_lines_cents[i]}')
        col_povertygap.append(f'poverty_gap_index_{poverty_lines_cents[i]}')
        col_tot_shortfall.append(f'total_shortfall_{poverty_lines_cents[i]}')
        col_poverty_severity.append(f'poverty_severity_{poverty_lines_cents[i]}')
        col_watts.append(f'watts_{poverty_lines_cents[i]}')
        
    #///////////////////////////////////////////////////////////////////////////////
    #//////////////////////////////////////////////////////////////////////////////
    
    #Above variables

    print('Calculating number of people above poverty lines...')
    start_time = time.time()
    
    col_above_n = []
    col_above_pct = []

    #For each poverty line in poverty_lines_cents
    for i in poverty_lines_cents:
        
        varname_n = f'headcount_above_{i}'
        df_final[varname_n] = df_final['reporting_pop'] - df_final[f'headcount_{i}']
        col_above_n.append(varname_n)
        
        varname_pct = f'headcount_ratio_above_{i}'
        df_final[varname_pct] = (df_final['reporting_pop'] - df_final[f'headcount_{i}']) / df_final['reporting_pop']
        col_above_pct.append(varname_pct)

    df_final.loc[:, col_above_pct] = df_final[col_above_pct] * 100
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    #///////////////////////////////////////////////////////////////////////////////
    #//////////////////////////////////////////////////////////////////////////////

    #Stacked variables

    print('Calculating variables between poverty lines...')
    start_time = time.time()

    #Calculate numbers in poverty between pov lines for stacked area charts
    
    #Remove the high income countries poverty line to the in-between calculations
    if ppp == 2011:
        poverty_lines_cents = [e for e in poverty_lines_cents if e not in [2170]]
    elif ppp == 2017:
        poverty_lines_cents = [e for e in poverty_lines_cents if e not in [2435]]
    
    #Make sure the poverty lines are in order, lowest to highest
    poverty_lines_cents.sort()

    col_stacked_n = []
    col_stacked_pct = []

    #For each poverty line in poverty_lines_cents
    for i in range(len(poverty_lines_cents)):
        #if it's the first value only get people below this poverty line (and percentage)
        if i == 0:
            varname_n = f'headcount_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_n] = df_final[f'headcount_{poverty_lines_cents[i]}']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_pct] = df_final[varname_n] / df_final['reporting_pop']
            col_stacked_pct.append(varname_pct)

        #If it's the last value calculate the people between this value and the previous 
        #and also the people over this poverty line (and percentages)
        elif i == len(poverty_lines_cents)-1:

            varname_n = f'headcount_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_n] = df_final[f'headcount_{poverty_lines_cents[i]}'] - df_final[f'headcount_{poverty_lines_cents[i-1]}']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_pct] = df_final[varname_n] / df_final['reporting_pop']
            col_stacked_pct.append(varname_pct)

            varname_n = f'headcount_stacked_above_{poverty_lines_cents[i]}'
            df_final[varname_n] = df_final['reporting_pop'] - df_final[f'headcount_{poverty_lines_cents[i]}']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_above_{poverty_lines_cents[i]}'
            df_final[varname_pct] = df_final[varname_n] / df_final['reporting_pop']
            col_stacked_pct.append(varname_pct)

        #If it's any value between the first and the last calculate the people between this value and the previous (and percentage)
        else:
            varname_n = f'headcount_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_n] = df_final[f'headcount_{poverty_lines_cents[i]}'] - df_final[f'headcount_{poverty_lines_cents[i-1]}']
            col_stacked_n.append(varname_n)

            varname_pct = f'headcount_ratio_stacked_below_{poverty_lines_cents[i]}'
            df_final[varname_pct] = df_final[varname_n] / df_final['reporting_pop']
            col_stacked_pct.append(varname_pct)

    df_final.loc[:, col_stacked_pct] = df_final[col_stacked_pct] * 100
    
    #Calculate stacked variables which "jump" the original order
    
    df_final[f'headcount_stacked_between_{poverty_lines_cents[1]}_{poverty_lines_cents[4]}'] = df_final[f'headcount_{poverty_lines_cents[4]}'] - df_final[f'headcount_{poverty_lines_cents[1]}']
    df_final[f'headcount_stacked_between_{poverty_lines_cents[4]}_{poverty_lines_cents[6]}'] = df_final[f'headcount_{poverty_lines_cents[6]}'] - df_final[f'headcount_{poverty_lines_cents[4]}']
    col_stacked_n_extra = [f'headcount_stacked_between_{poverty_lines_cents[1]}_{poverty_lines_cents[4]}', f'headcount_stacked_between_{poverty_lines_cents[4]}_{poverty_lines_cents[6]}']
    
    df_final[f'headcount_ratio_stacked_between_{poverty_lines_cents[1]}_{poverty_lines_cents[4]}'] = df_final[f'headcount_ratio_{poverty_lines_cents[4]}'] - df_final[f'headcount_ratio_{poverty_lines_cents[1]}']
    df_final[f'headcount_ratio_stacked_between_{poverty_lines_cents[4]}_{poverty_lines_cents[6]}'] = df_final[f'headcount_ratio_{poverty_lines_cents[6]}'] - df_final[f'headcount_ratio_{poverty_lines_cents[4]}']
    col_stacked_pct_extra = [f'headcount_ratio_stacked_between_{poverty_lines_cents[1]}_{poverty_lines_cents[4]}', f'headcount_ratio_stacked_between_{poverty_lines_cents[4]}_{poverty_lines_cents[6]}']

    

#     df_final['headcount_stacked_between_190_1000'] = df_final['headcount_1000'] - df_final['headcount_190']
#     df_final['headcount_stacked_between_1000_3000'] = df_final['headcount_3000'] - df_final['headcount_1000']
#     col_stacked_n_extra = ['headcount_stacked_between_190_1000', 'headcount_stacked_between_1000_3000']

#     df_final['headcount_ratio_stacked_between_190_1000'] = df_final['headcount_ratio_1000'] - df_final['headcount_ratio_190']
#     df_final['headcount_ratio_stacked_between_1000_3000'] = df_final['headcount_ratio_3000'] - df_final['headcount_ratio_1000']
#     col_stacked_pct_extra = ['headcount_ratio_stacked_between_190_1000', 'headcount_ratio_stacked_between_1000_3000']

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')


    #///////////////////////////////////////////////////////////////////////////////
    #//////////////////////////////////////////////////////////////////////////////
    #Decile averages and inequality ratios
    
    print('Calculating decile averages and inequality ratios...')
    start_time = time.time()
    # Create average decile income/consumption
    col_decile_share = []
    col_decile_avg = []
    col_decile_thr = []

    for i in range(1,11):

        if i !=10:
            varname_thr = f'decile{i}_thr'
            col_decile_thr.append(varname_thr)

        varname_share = f'decile{i}_share'
        varname_avg = f'decile{i}_avg'
        df_final[varname_avg] = df_final[varname_share] * df_final['mean'] / 0.1

        col_decile_share.append(varname_share)
        col_decile_avg.append(varname_avg)

    #Multiplies decile columns by 100
    df_final.loc[:, col_decile_share] = df_final[col_decile_share] * 100
    
    #Quintile shares
    
    col_quintile_share = []
    for q in range(1,6):
        varname_share = f'quintile{q}_share'
        df_final[varname_share] = df_final[f'decile{2*q-1}_share'] + df_final[f'decile{2*q}_share']
        col_quintile_share.append(varname_share)

    #Palma ratio and other average/share ratios
    df_final['palma_ratio'] = df_final['decile10_share'] / (df_final['decile1_share'] + df_final['decile2_share'] + df_final['decile3_share'] + df_final['decile4_share'])
    df_final['s80_s20_ratio'] =  (df_final['decile9_share'] + df_final['decile10_share']) / (df_final['decile1_share'] + df_final['decile2_share'])
    df_final['p90_p10_ratio'] =  df_final['decile9_thr'] / df_final['decile1_thr']
    df_final['p90_p50_ratio'] =  df_final['decile9_thr'] / df_final['decile5_thr']
    df_final['p50_p10_ratio'] =  df_final['decile5_thr'] / df_final['decile1_thr']
    
    col_inequality = ['mld', 'gini', 'polarization', 'palma_ratio', 's80_s20_ratio', 'p90_p10_ratio', 'p90_p50_ratio', 'p50_p10_ratio']


    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    #///////////////////////////////////////////////////////////////////////////////
    #//////////////////////////////////////////////////////////////////////////////
    
    #Get all the columns to order the final output
    cols = col_ids + col_central + col_headcount + col_headcount_ratio + col_povertygap + col_tot_shortfall + \
            col_avg_shortfall + col_incomegap + col_above_n + col_above_pct + col_poverty_severity + col_watts + \
            col_stacked_n + col_stacked_n_extra + col_stacked_pct + col_stacked_pct_extra + \
            col_relative +  \
            col_decile_share + col_quintile_share + col_decile_thr + col_decile_avg + col_inequality + \
            col_extra
    
    #Export all the data to use it in PIP_issues
    # df_final.to_csv(f'notebooks/allthedata_ppp_{ppp}.csv', index=False)
    
    #######################################################################################
    
    #Dropping errors
    
    print('Dropping rows with issues...')
    start_time = time.time()

    # stacked values not adding up to 100%
    print(f'{len(df_final)} rows before stacked values check')
    df_final['sum_pct'] = df_final[col_stacked_pct].sum(axis=1)
    df_final = df_final[~((df_final['sum_pct'] >= 100.1) | (df_final['sum_pct'] <= 99.9))].reset_index(drop=True)
    print(f'{len(df_final)} rows after stacked values check')

    #missing poverty values (headcount, poverty gap, total shortfall)
    print(f'{len(df_final)} rows before missing values check')
    cols_to_check = col_headcount + col_headcount_ratio + col_povertygap + col_tot_shortfall + col_stacked_n + col_stacked_pct
    df_final = df_final[~df_final[cols_to_check].isna().any(1)].reset_index(drop=True)
    print(f'{len(df_final)} rows after missing values check')

    # headcount monotonicity check
    print(f'{len(df_final)} rows before headcount monotonicity check')
    m_check_vars = []
    for i in range(len(col_headcount)):
        if i > 0:
            check_varname = f'm_check_{i}'
            df_final[check_varname] = df_final[f'{col_headcount[i]}'] >= df_final[f'{col_headcount[i-1]}']
            m_check_vars.append(check_varname)       
    df_final['check_total'] = df_final[m_check_vars].all(1)
    df_final = df_final[df_final['check_total'] == True].reset_index(drop=True)
    print(f'{len(df_final)} rows after headcount monotonicity check')

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    return df_final, cols


def median_patch(df_final, ppp):
    
    print('Patching missing median values...')
    start_time = time.time()

    input_file = TEMP_DIR / f'ppp_{ppp}/raw/percentiles.csv'
    df_median = pd.read_csv(input_file)
    df_median = df_median[df_median['target_percentile'] == "P50"].reset_index(drop=True)

    df_final = pd.merge(df_final, 
                        df_median[['Entity', 'Year', 'reporting_level', 'welfare_type',
                                   'percentile_value']], 
                        how='left', 
                        on=['Entity', 'Year', 'reporting_level', 'welfare_type'],
                        validate='many_to_one')

    #Create the column median2, a combination between the old and new median values
    df_final['median2'] = np.where((df_final['median'].isnull()) & ~(df_final['percentile_value'].isnull()), df_final['percentile_value'], df_final['median'])

    #Median nulls in original and new columns
    null_median = (df_final['median'].isnull()).sum()
    null_median2 = (df_final['median2'].isnull()).sum()

    #Print these two different values to show the change generated by the patch 
    print(f'Before patching: {null_median} nulls for median')
    print(f'After patching: {null_median2} nulls for median')

    #This is a quick last check to compare previous and new median values
    df_final['median_ratio'] = df_final['median'] / df_final['median2']
    median_ratio_median = (df_final['median_ratio']).median()
    median_ratio_min = (df_final['median_ratio']).min()
    median_ratio_max = (df_final['median_ratio']).max()

    if median_ratio_median == 1 and median_ratio_min == 1 and median_ratio_max == 1:
        print(f'Patch successful.')
        print(f'Ratio between old and new variable: Median = {median_ratio_median}, Min = {median_ratio_min}, Max = {median_ratio_max}')
    else:
        print(f'Patch changed some median values. Please check for errors.')
        print(f'Ratio between old and new variable: Median = {median_ratio_median}, Min = {median_ratio_min}, Max = {median_ratio_max}')   

    #Drop the check and the old median and rename the new median
    df_final.drop(columns=['median', 'median_ratio', 'percentile_value'], inplace=True)
    df_final.rename(columns={'median2': 'median'}, inplace=True)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Done. Execution time:', elapsed_time, 'seconds')
    
    return df_final


def standardise(df_final, cols, ppp):
    
    print('Standardising entities...')

    mapping_file = INPUT_DIR / f"ppp_{ppp}/countries_standardized.csv"
    # Standardize entity names
    df_final = standardize_entities(
        orig_df = df_final,
        entity_mapping_url = mapping_file,
        mapping_varname_raw ='country',
        mapping_vaname_owid = 'Our World In Data Name',
        data_varname_old = 'Entity',
        data_varname_new = 'Entity'
    )
    
    #Reorder columns according to cols
    df_final = df_final[cols]
    
    #Removing above and stacked variables, only meant for internal purposes
    above_columns = list(df_final.filter(like="above", axis=1).columns)
    stacked_columns = list(df_final.filter(like="stacked", axis=1).columns)
    remove_columns = above_columns + stacked_columns
    public_columns = [c for c in df_final.columns if c not in remove_columns]
    df_final = df_final[public_columns]
    
    #Align format of entity and year columns to the rest of the dataset
    df_final = df_final.rename(columns={'Entity': 'country',
                                       'Year': 'year'})
    #Add ppp_version column
    df_final['ppp_version'] = ppp
    
    df_final.to_csv(TEMP_DIR / f'pip_dataset_ppp{ppp}.csv', index=False)
    
    return df_final

def combine_2011_and_2011_data():
    #Read the respective 2011 and 2017 PPP file
    input_2011_file = TEMP_DIR / 'pip_dataset_ppp2011.csv'
    input_2017_file = TEMP_DIR / 'pip_dataset_ppp2017.csv'

    if input_2011_file.is_file() and input_2017_file.is_file():
        df_2011 = pd.read_csv(input_2011_file)
        df_2017 = pd.read_csv(input_2017_file)
        
        #Replace international lines numbers to text
        df_2011.columns = df_2011.columns.str.replace("190", "international_povline")
        df_2011.columns = df_2011.columns.str.replace("320", "lower_mid_income_povline")
        df_2011.columns = df_2011.columns.str.replace("550", "upper_mid_income_povline")
        df_2011.columns = df_2011.columns.str.replace("2170", "high_income_povline")

        df_2017.columns = df_2017.columns.str.replace("215", "international_povline")
        df_2017.columns = df_2017.columns.str.replace("365", "lower_mid_income_povline")
        df_2017.columns = df_2017.columns.str.replace("685", "upper_mid_income_povline")
        df_2017.columns = df_2017.columns.str.replace("2435", "high_income_povline")
        
        #Concatenate both 2011 and 2017 PPPs
        df_final = pd.concat([df_2011, df_2017], ignore_index=True)
        
        #Get columns from codebook and only keep those variables
        df_codebook = pd.read_csv(PIP_CODEBOOK_FILE)
        variable_list = list(df_codebook['column'])
        df_final = df_final[variable_list]
        
        # Set an appropriate index and sort conveniently.
        df_final = df_final.sort_values(["ppp_version", "country", "year", "reporting_level", "welfare_type"]).\
            set_index(["country", "year", "reporting_level", "welfare_type", "ppp_version"], verify_integrity=True)

        #Export
        df_final.to_csv(OUTPUT_CSV_FILE)
        df_final.to_excel(OUTPUT_XLSX_FILE, sheet_name="pip")
    else:
        print("Run script for ppp 2011 and 2017 so that both can be combined into a final dataset.")
