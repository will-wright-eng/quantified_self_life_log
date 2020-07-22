# from __future__ import print_function
# %reset -f

import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import calmap

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import 

import config_lifelogs

# pd.set_option("display.max_rows", 200)
# pd.set_option("display.max_columns", 200)

class life_log(object):
    '''docstring for life_log class'''
    def __init__(self,spreadsheet_id,sample_range,mapping_table,grouping,auto_run=True):
        self.spreadsheet_id = spreadsheet_id
        self.sample_range = sample_range
        self.mapping_table = mapping_table
        self.grouping = grouping
        if auto_run:
            self.run_analysis(self.spreadsheet_id,self.sample_range,self.mapping_table,self.grouping)
            
    def run_analysis(self, spreadsheet_id, sample_range, mapping_table, grouping):
    	'''docstring for run_analysis function'''
        df = self.return_dataframe_from_sheet(spreadsheet_id,sample_range)
        df_mapping_table = self.return_dataframe_from_sheet(spreadsheet_id,mapping_table)
        cols, noncols, cols0, cols1 = self.split_cols(df)
        df, df0 = self.clean_dataframe(df, df_mapping_table, cols, grouping)
        df1 = self.process_substance_cols(df, cols0)
        ###
        ###
        df3 = df1.merge(df0,left_index=True, right_index=True)
        for col in list(df3):
            df3[col] = df3[col].astype(int)
        df = df3.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        self.df = df
        # add section that combines like columns, in cases where grouping != 'descriptor'
        # other options being 'secondary_group' or 'full_descriptor'
        
    def return_dataframe_from_sheet(self,spreadsheet_id,sample_range):
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
        ###
        df = pd.DataFrame(values)
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header
        return df

    def split_cols(self, df):
    	'''docstring for split_cols function'''
        # create col lists for components of dataframe: category model, dr
        cols = []
        noncols = []
        # category model v. non-category model
        for col in list(df):
            try:
                int(col)
                cols.append(col)
            except ValueError as e:
                noncols.append(col)
        # from non-cateogry model: substance model v non-substance model
        cols0 = [i for i in noncols if '(' in i]
        cols1 = [i for i in noncols if '(' not in i]
        return cols, noncols, cols0, cols1
    
    def clean_dataframe(self, df, df_mapping_table, cols, grouping):
    	'''docstring for clean_dataframe function'''
        # trim down imported dataframe and set Date as index
        ndf = df[cols+['Date']]
        ndf = ndf.set_index('Date')
        # value counts row for each category model row
        dfs = []
        for i in range(len(ndf)):
            dfs.append(pd.DataFrame(ndf.iloc[i].value_counts()).T)
        # dataframe of category model value counts
        df0 = pd.concat(dfs,axis=0,sort=False)
        # clean
        cols = [i for i in list(df0) if i!='']
        df0 = df0[cols]
        df0 = df0.fillna(0)
        ###
        map_from = 'number'
        map_to = grouping
        # map catogry model labels onto column headers
        df_mapping_table[map_from] = df_mapping_table[map_from].astype(str)
        # create dictionary
        model_dict = {}
        for i in range(len(df_mapping_table)):
            model_dict[df_mapping_table[map_from].iloc[i]] = df_mapping_table[map_to].iloc[i]
        # map dictionary onto dataframe column headers
        df0.columns = pd.Series(list(df0)).map(model_dict)
        return df, df0

    def process_substance_cols(self, df, cols0):
    	'''docstring for process_substance_cols function'''
        # trim down imported dataframe and set Date as index
        ndf = df[cols0+['Date']]
        ndf = ndf.set_index('Date')

        # convert all values to int
        dfs = []
        for i in range(len(ndf)):
            dfs.append([0 if i=='' else int(i) for i in ndf.iloc[i]])

        df1 = pd.DataFrame(dfs)
        df1.columns = list(ndf)
        df1.index = ndf.index
        return df1

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

def calplot_funk(df,keycol):
	'''docstring for calplot_funk function'''
    fig,ax=calmap.calendarplot(df[keycol],
                        fillcolor='grey',# linewidth=0,#cmap='RdYlGn',
                        fig_kws=dict(figsize=(17,12)), subplot_kws={'title':keycol}, vmin=0)
    fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist(), orientation='horizontal')
    return #plt.show()

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
	cols = list(df)
	for col in cols:
	    calplot_funk(df,col)

if __name__ == '__main__':
    main()
    print('program successful!\n')