import pandas as pd
import pickle
from google.cloud import bigquery
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def download_table_from_gbq(project_name, dataset_name, table_name):
    '''
    download_table_from_gbq(project_name, dataset_name, table_name)
    project_name: bq project
    dataset_name: bq dataset
    table_name: bq table
    '''
    # https://cloud.google.com/bigquery/docs/pandas-gbq-migration
    client = bigquery.Client()
    sql = """SELECT * FROM `{project}.{dataset}.{table}`"""
    query = sql.format(project=project_name,
                       dataset=dataset_name,
                       table=table_name)
    # Run a Standard SQL query using the environment's default project
    df = client.query(sql).to_dataframe()
    # Run a Standard SQL query with the project set explicitly
    project_id = 'peronal-data-projects'
    df = client.query(sql, project=project_id).to_dataframe()
    return df


def upload_table_to_gbq(df, dataset_name, table_name):
    '''docstring for upload_table_to_gbq'''
    #https://cloud.google.com/bigquery/docs/pandas-gbq-migration
    client = bigquery.Client()
    table_id = dataset_name + '.' + table_name
    job = client.load_table_from_dataframe(df, table_id)
    # Wait for the load job to complete.
    print('job complete')
    return job.result()


def return_dataframe_from_sheet(self, spreadsheet_id, sample_range):
    '''docstring for return_dataframe_from_sheet function
    sample_range: string that indexes table range in gsheet (be sure to select only columns with non-null headers)
    '''
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
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=sample_range).execute()
    values = result.get('values', [])
    ###
    df = pd.DataFrame(values)
    new_header = df.iloc[0]  #grab the first row for the header
    df = df[1:]  #take the data less the header row
    df.columns = new_header  #set the header row as the df header
    return df
