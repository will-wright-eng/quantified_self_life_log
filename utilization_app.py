import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import calmap
import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import config_lifelogs
import config_google
from lifelog import life_log
from gcp_utility import download_table_from_gbq, upload_table_to_gbq#, return_dataframe_from_sheet


def combine_like_cols(df):
    '''docstring for combine_like_cols function'''
    # select non-substance columns
    # create set of non-substance cols
    # loop through each col, summing along row axis=1
    # assemble summed cols and merge with substance cols
    cols = list(df)
    groups = list(set([i for i in cols if '(' not in i]))
    group_vecs = []
    for col in groups:
        if list(df[col]).count(col)>1:
            group_vecs.append(df[col].sum(axis=1))
        else:
            group_vecs.append(df[col])
    temp = pd.concat(group_vecs,axis=1)
    temp.columns = groups
    return temp.merge(df[[i for i in cols if '(' in i]],left_index=True,right_index=True)

def main():
    '''docstring for main function'''
    grouping = 'descriptor'
    lls = []
    for i in range(3):
        spreadsheet_id = config_lifelogs.spreadsheet_ids[i]
        sample_range = config_lifelogs.sample_ranges[i]
        mapping_table = config_lifelogs.mapping_tables[i]
        lls.append(life_log(spreadsheet_id, sample_range, mapping_table, grouping))

    ###
    temp = [i.df for i in lls]
    dfs = []
    for df in temp:
        df = combine_like_cols(df)
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        dfs.append(df)
    df = pd.concat(dfs,sort=False)
    df = df.fillna(0)
    
    credential_path = config_google.gbq_credential_path
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    dataset_name = config_google.uploads_dataset_name
    table_name = 'raw_lifelog_daycount'
    upload_table_to_gbq(df, dataset_name, table_name)

if __name__ == '__main__':
    main()
    print('program successful!\n')