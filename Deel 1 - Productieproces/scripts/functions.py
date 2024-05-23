import glob
import json

def read_daily(city):
    """
    Takes in an abbreviation of a city and reads its json files to a dataframe.
    """
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