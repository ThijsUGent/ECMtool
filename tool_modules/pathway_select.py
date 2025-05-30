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
    st.write(
        "Choose to select a ready-made path, upload or create your path")

    # Load and clean the per-ton configuration data
    perton_path = "data/perton_all.csv"
    perton_ALL = pd.read_csv(perton_path)

    perton_ALL = perton_ALL.groupby("configuration_id").first().reset_index()

    perton_ALL = process_configuration_dataframe(perton_ALL)

    perton_ALL_no_mix = perton_ALL[~perton_ALL["configuration_name"].str.contains(
        "mix")]

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
        ["Ready-made path", "Upload a path", "Create a path"],
        horizontal=True,
    )
    aidres_mix_checked = selection == "Ready-made path"
    upload_mix_checked = selection == "Upload a path"
    create_mix_checked = selection == "Create a path"

    # --- EU-MIX AUTOMATED PATHWAY SELECTION ---
    if aidres_mix_checked:
        dict_routes_selected, selected_mix, pathway_name = preconfigure_path(
            perton_ALL_no_mix, columns_to_show_selection)

# --- CUSTOM FROM-SCRATCH PATHWAY BUILDING ---
    if create_mix_checked:
        dict_routes_selected, pathway_name = create_path(
            perton_ALL_no_mix, columns_to_show_selection)
# --- IMPORT PATHWAY FROM .txt FILE ---
    if upload_mix_checked:
        dict_routes_selected, pathway_name = upload_path(
            perton_ALL_no_mix, columns_to_show_selection)
    if any(not df.empty for df in dict_routes_selected.values()):
        # At least one DataFrame is not empty

        # Keep only the selected rows (where route_weight not 0)
        for key in dict_routes_selected.keys():
            dict_routes_selected[key] = dict_routes_selected[key][dict_routes_selected[key]
                                                                  ["route_weight"] != 0]

        # --- PATHWAY NAMING AND SAVING ---
        if aidres_mix_checked:
            pathway_name = st.text_input(
                "Enter a name for your pathway", value=pathway_name
            )
        else:
            pathway_name = st.text_input(
                "Enter a name for your pathway", value=pathway_name
            )

        if "Pathway name" not in st.session_state:
            st.session_state["Pathway name"] = {}

        if st.button("Save pathway"):
            if pathway_name.strip() == "":
                st.warning("Please enter a name for the pathway")
            elif pathway_name in st.session_state["Pathway name"]:
                st.warning(f"A pathway named '{pathway_name}' already exists.")
            else:
                st.session_state["Pathway name"][pathway_name] = dict_routes_selected
                st.success(f"Pathway '{pathway_name}' created.")
                st.text("Download pathway configuration in txt format:")
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
