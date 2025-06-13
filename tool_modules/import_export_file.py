import pandas as pd
import streamlit as st


def export_to_txt(df):
    """
    Converts a DataFrame into CSV format and returns it as a plain text string.

    Parameters:
        df (pd.DataFrame): DataFrame to be exported.

    Returns:
        str: CSV-formatted string.
    """
    return df.to_csv(index=False)


def import_to_dict(uploaded_file):
    """
    Extracts dataframe from a TXT file and returns it as a pandas DataFrame.
    """
    try:
        df = pd.read_csv(uploaded_file, sep=",")
    except Exception:
        st.error(
            "The uploaded file is not in the correct format. Please upload the lastest format from the tool")
        return pd.DataFrame()

    required_columns = {"route_weight", "route_name"}
    if not required_columns.issubset(df.columns):
        st.error("The uploaded file does not contain the required format.")
        return pd.DataFrame()

    return df
