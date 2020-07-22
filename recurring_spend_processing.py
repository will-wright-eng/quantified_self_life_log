# from __future__ import print_function
# %reset -f

import pandas as pd
import os
import glob
import numpy as np
import datetime as dt
import pickle
import os.path

from google.cloud import bigquery

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import config_google
import config_recurringspend
from gcp_utility import download_table_from_gbq, upload_table_to_gbq
# df = download_table_from_gbq(project_name, dataset_name, table_name)
# upload_table_to_gbq(ndf, dataset_name, table_name)

# pd.set_option("display.max_rows", 200)
# pd.set_option("display.max_columns", 200)

def return_dataframe_from_sheet(spreadsheet_id,sample_range):
    '''docstring for return_dataframe_from_sheet function'''
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,range=sample_range).execute()
    values = result.get('values', [])
    ###
    df = pd.DataFrame(values)
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    return df

def blank_to_nan(df):
    '''docstring for blank_to_nan function'''
    # replace blank elements (of length zero) with numpy nan
    data = []
    for i in list(df):
        temp = []
        for j in df[i]:
            if len(j)==0:
                temp.append(np.nan)
            else:
                temp.append(j)
        data.append(temp)
    return data

def generate_time_series_v1(df, start_col, cost_col):
    '''docstring for generate_time_series_v1 function'''
    # generate time series by service_name
    ndf = df
    df_list = []
    for name in ndf['service_name'].unique():
        temp = ndf.loc[ndf['service_name']==name]
        dfs = []
        for index, row in temp.iterrows():
            df = pd.DataFrame(list(pd.date_range(row[start_col].date(), row['end_date'].date())))
            df.columns = ['dates']
            df['service'] = name
            df['cost'] = float(row[cost_col])/7
            dfs.append(df)
        df = pd.concat(dfs)
        df = df.sort_values('dates',ascending=True)
        df_list.append(df)
    df = pd.concat(df_list)
    print(df.shape)
    return df

def generate_time_series_v2(df, start_col, cost_col):
    '''docstring for generate_time_series_v2 function'''
    # generate time series by service_name
    min_start = min(df[start_col])
    max_end = max(df['end_date'])
    base_df = pd.DataFrame(list(pd.date_range(min_start.date(), max_end.date())))
    base_df.columns = ['dates']
    for name in df['service_name'].unique():
        temp = df.loc[df['service_name']==name]
        dfs = []
        for index, row in temp.iterrows():
            ndf = pd.DataFrame(list(pd.date_range(row[start_col].date(), row['end_date'].date())))
            ndf.columns = ['dates']
            ndf[name] = float(row[cost_col])/7
            dfs.append(ndf)
        if len(dfs)>1:
            for i in range(len(dfs)-1):
                temp = dfs[i].set_index('dates').add(dfs[i+1].set_index('dates'), fill_value=0).reset_index()
        else:
            temp = dfs[0]
        base_df = pd.merge(base_df,temp,left_on='dates',right_on='dates',how='left')
    return base_df

def generate_time_series_v3(df, start_col, cost_col):
    '''docstring for generate_time_series_v3 function'''
    # generate time series by service_name
    min_start = min(df[start_col])
    max_end = max(df['end_date'])
    base_df = pd.DataFrame(list(pd.date_range(min_start.date(), max_end.date())))
    base_df.columns = ['dates']
    for name in df['service_name'].unique():
        temp = df.loc[df['service_name']==name]
        dfs = []
        for index, row in temp.iterrows():
            ndf = pd.DataFrame(list(pd.date_range(row[start_col].date(), row['end_date'].date())))
            ndf.columns = ['dates']
            ndf[name] = float(row[cost_col])
            dfs.append(ndf)
        base_df = pd.merge(base_df,dfs[0],left_on='dates',right_on='dates',how='left')
        base_df.fillna(0,inplace=True)
        if len(dfs)>1:
            for i in range(1,len(dfs)):
                base_df = base_df.set_index('dates').add(dfs[i].set_index('dates'), fill_value=0).reset_index()
        else:
            pass
    return base_df

def main():
    '''docstring for main function'''
    ###
    spreadsheet_id = config_recurringspend.spreadsheet_id
    sample_range = config_recurringspend.sample_range
    df = return_dataframe_from_sheet(spreadsheet_id,sample_range)
    print(df.shape)
    ###
    # clean dataframe and remove irrelevant rows/columns
    cols = list(df)
    data = blank_to_nan(df)
    ndf = pd.DataFrame(data).T
    ndf.columns = cols
    ndf = ndf[[i for i in list(ndf) if 'relative' not in i]]
    ndf.columns = [i.replace(' ','_').replace('/','_').replace('$','money').replace('[','').replace(']','') for i in list(ndf)]
    # key cols
    start_col = 'start_date'
    cost_col = 'cost_day_money_time'
    ndf = ndf.loc[pd.isnull(ndf[cost_col])==False]
    ndf = ndf.loc[pd.isnull(ndf[start_col])==False]
    ndf[cost_col] = ndf[cost_col].apply(lambda x: x.replace('$','').replace(',',''))
    today = str(dt.datetime.today()).split(' ')[0]
    ndf = ndf.loc[ndf[start_col]<today]
    date_cols = [i for i in list(ndf) if 'date' in i]
    for col in date_cols:
        ndf[col] = pd.to_datetime(ndf[col])
    credential_path = config_google.gbq_credential_path
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    dataset_name = config_google.uploads_dataset_name
    table_name = 'raw_recurring_spend_tracking_sheet'
    upload_table_to_gbq(ndf, dataset_name, table_name)
    df = generate_time_series_v3(ndf, start_col, cost_col)
    print(df.shape)
    df.columns = [i.replace(' ','_') for i in list(df)]
    table_name = 'recurring_spend_time_series_v3'
    return upload_table_to_gbq(df, dataset_name, table_name)

if __name__ == '__main__':
    main()
    print('program successful!\n')