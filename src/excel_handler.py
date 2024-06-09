
import pandas as pd

def read_excel(file_path):
    return pd.read_excel(file_path)

def add_priority(df, client_name, priority):
    df.loc[df['ClientName'] == client_name, 'Priority'] = priority

def save_excel(df, file_path):
    df.to_excel(file_path, index=False)
