# Streamlit interface and data tools
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json

from tool_modules.import_export_file import *
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.builder_functions import *


def select_page():
    st.title("Pathway Builder")
    st.write("Choose to create your pathway, aidres mix, or upload a mix")

    # Load and clean the per-ton configuration data
    perton_path = "data/perton_all.csv"
    perton_ALL = pd.read_csv(perton_path)

    perton_ALL = perton_ALL.groupby("configuration_id").first().reset_index()

    perton_ALL = process_configuration_dataframe(perton_ALL)

    # Columns to be shown in the route selection editor
    columns_to_show_selection = [
        "selected",
        "configuration_name",
        "horizon",
        "fuel",
        "technology_category",
        "hydrogen_source",
    ]

    selection = st.radio(
        "Choose an option",
        ["AIDRES-MIX", "Create a MIX", "Upload MIX"],
        horizontal=True,
    )
    aidres_mix_checked = selection == "AIDRES-MIX"
    create_mix_checked = selection == "Create a MIX"
    upload_mix_checked = selection == "Upload MIX"

    # --- EU-MIX AUTOMATED PATHWAY SELECTION ---
    if aidres_mix_checked:
        dict_routes_selected, pre_choices_name_list, selected_mix, pathway_name = preconfigure_path(
            perton_ALL, columns_to_show_selection)

# --- CUSTOM FROM-SCRATCH PATHWAY BUILDING ---
    if create_mix_checked:
        dict_routes_selected, pathway_name = create_path(
            perton_ALL, columns_to_show_selection)
# --- IMPORT PATHWAY FROM .txt FILE ---
    if upload_mix_checked:
        dict_routes_selected, pathway_name = upload_path(
            perton_ALL, columns_to_show_selection)

# --- PATHWAY NAMING AND SAVING ---
    if aidres_mix_checked:
        pathway_name = st.text_input(
            "Enter a name for your pathway", value=selected_mix
        )
    else:
        pathway_name = st.text_input(
            "Enter a name for your pathway", value=pathway_name
        )

    if "Pathway name" not in st.session_state:
        st.session_state["Pathway name"] = {}

    if st.button("Create pathway"):
        if pathway_name.strip() == "":
            st.warning("Please enter a name for the pathway")
        elif pathway_name in st.session_state["Pathway name"]:
            st.warning(f"A pathway named '{pathway_name}' already exists.")
        else:
            st.session_state["Pathway name"][pathway_name] = dict_routes_selected
            st.success(f"Pathway '{pathway_name}' created.")
            st.text("Preview of the file content:")
            combined_df = pd.concat(
                dict_routes_selected.values(), ignore_index=True)
            exported_txt = export_to_txt(
                combined_df, pathway_name)
            # Offer as download
            st.download_button(
                label="Download Pathway File",
                data=exported_txt,
                file_name=f"ECM_Tool_{pathway_name}.txt",
                mime="text/plain"
            )
