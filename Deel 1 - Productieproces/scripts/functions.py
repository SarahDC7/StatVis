import glob
import json
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

def read_daily(city):
    """
    Takes in an abbreviation of a city and reads its json files to a dataframe.
    """
    
    locs = {'input_master_data' : os.path.join('..', 'data', 'input', 'data_productie', 'master_data.json'),
        'input_daily_BRU' : os.path.join('..', 'data', 'input', 'data_productie', 'daily_production', 'BRU'),
        'input_daily_STO' : os.path.join('..', 'data', 'input', 'data_productie', 'daily_production', 'STO')}

    folder_daily = locs[f"input_daily_{city}"]

    # import all files which end with .json from folder
    json_files = glob.glob(os.path.join(folder_daily, '*.json'))
    
    json_list = []
    for file in tqdm(json_files):
        with open(file, 'r') as f:
            data = json.load(f)
        json_list.append(data)
    
    # convert list of dfs to dataframe
    df_daily = pd.json_normalize(json_list)
    return df_daily

def remove_outlier(df):
    """
    Takes in data frame of 1 column (prod_daily) and removes the outliers.
    """
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3-q1 #Interquartile range
    tresh_low  = q1-1.5*iqr
    tresh_high = q3+1.5*iqr
    df_out = df.loc[(df > tresh_low) & (df < tresh_high)]
    return df_out, tresh_low, tresh_high

def verdeling(perc_0, perc_out_low, perc_prod, perc_out_high, msr, avg, std, sample_size = 10 ** 3):
    """
    Functie genereert simulatie data obv parameters van betreffende stad voor n dagen
    TODO: better option for 0 productie
    """
    distributions = [
        {'type': np.random.normal, 'kwargs': {'loc': 0, 'scale': 1/100}},
        {'type': np.random.uniform, 'kwargs': {'low': 0, 'high': tresh_low}},
        {'type': np.random.normal, 'kwargs': {'loc': avg, 'scale': std}},
        {'type': np.random.uniform, 'kwargs': {'low': tresh_high, 'high': msr}}
    ]
    coeff = np.array([perc_0, perc_out_low, perc_prod, perc_out_high])
    coeff /= coeff.sum()
    num_dis = len(distributions)

    data = np.zeros((sample_size, num_dis))
    for idx, distr in enumerate(distributions):
        data[:, idx] = distr['type'](size = (sample_size,), **distr['kwargs'])
    random_idx = np.random.choice(np.arange(num_dis), size = (sample_size,), p = coeff)
    sim_data = data[np.arange(sample_size), random_idx]
    return sim_data