import pandas as pd
import joblib


def get_excel_file(file_name):
    return pd.read_excel(f"./static/documents/{file_name}.xlsx")

def get_model(file_name):
    return joblib.load(f"./static/documents/{file_name}.pkl")
     

def convert_df_html(result):
    return [result.to_html(classes="data", header=True)]