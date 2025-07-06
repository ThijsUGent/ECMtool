import streamlit as st
import json
import pandas as pd
import matplotlib as plt
import pydeck as pdk


import streamlit as st
import json
import pydeck as pdk

import streamlit as st
import pydeck as pdk
import json
import pandas as pd


def profile_load():
    df_time_cluster = pd.read_csv(
        "data/ELMAS_dataset/Time_series_18_clusters.csv", sep=";")
    df_cluster_NACE = pd.read_csv(
        "data/ELMAS_dataset/Clusters_after_manual_reclassification.csv", sep=";")
    df_nace = pd.read_csv(
        "data/ELMAS_dataset/NACE_classification.csv", sep=';')
    df_cluster_NACE["Class_description"] = df_cluster_NACE["class"].map(
        df_nace.set_index("class")["Class_description"]
    )
    st.write(df_cluster_NACE)
