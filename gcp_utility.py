def download_table_from_gbq(project_name, dataset_name, table_name):
    '''docstring for download_table_from_gbq'''
    # https://cloud.google.com/bigquery/docs/pandas-gbq-migration
    client = bigquery.Client()
    sql = """
        SELECT *
        FROM `{project}.{dataset}.{table}`
        """
    query = sql.format(project=project_name, dataset=dataset_name, table=table_name)
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
    table_id = dataset_name+'.'+table_name
    job = client.load_table_from_dataframe(df, table_id)
    # Wait for the load job to complete.
    print('job complete')
    return job.result()

# ###
# # download table from google bigquery script_uploads dataset
# project_name = 'peronal-data-projects'
# dataset_name = 'script_uploads'
# table_name = 'raw_twl_customer_table'
# df = download_table_from_gbq(project_name, dataset_name, table_name)

# ###
# # upload dataframe to google bigquery script_uploads dataset
# dataset_name = 'script_uploads'
# table_name = 'raw_recurring_spend_tracking_sheet'
# upload_table_to_gbq(ndf, dataset_name, table_name)