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

    # Default value pathway
    pathway_name = "Pathway 1"

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
        sectors_list = []
        for sector in sorted(df["sector_name"].unique()):
            sectors_list.append(sector)
        selected_sectors = st.pills(
            "Sector(s)", sectors_list, selection_mode="multi")
        if len(selected_sectors) < 1:
            st.text("Please select at least 1 sector")
        else:
            tabs = st.tabs(selected_sectors)
            for i, sector in enumerate(selected_sectors):
                with tabs[i]:
                    all_products = sorted(
                        df[df["sector_name"] == sector]["product_name"].unique()
                    )
                    for product in all_products:
                        with st.expander(f"{sector} - {product}", expanded=False):
                            df_product = df[df["product_name"]
                                            == product].copy()
                            # Default: unselected
                            df_product["selected"] = False

                            # Move "selected" column to front
                            cols = df_product.columns.tolist()
                            cols.remove("selected")
                            df_product = df_product[["selected"] + cols].reset_index(
                                drop=True
                            )

                            edited_df = st.data_editor(
                                df_product,
                                num_rows="fixed",
                                column_config={
                                    "selected": st.column_config.CheckboxColumn(
                                        "selected"
                                    )
                                },
                                column_order=columns_to_show_selection,
                                disabled=df_product.columns.difference(
                                    ["selected"]
                                ).tolist(),
                                hide_index=True,
                                key=f"editor_custom_{sector}_{product}",
                            )

                            # Handle weighting of selected routes
                            selected_df_product = edited_df[
                                edited_df["selected"] == True
                            ].copy()
                            if not selected_df_product.empty:
                                selected_df_product["route_weight"] = (
                                    round(1 / len(selected_df_product), 4) * 100
                                )

                            st.text("Edit the weight (%)")
                            edited_selected_df_product = st.data_editor(
                                selected_df_product,
                                num_rows="fixed",
                                column_config={
                                    "route_weight": st.column_config.NumberColumn(
                                        "route_weight"
                                    )
                                },
                                disabled=selected_df_product.columns.difference(
                                    ["route_weight"]
                                ).tolist(),
                                hide_index=True,
                                column_order=[
                                    "configuration_name", "route_weight"],
                                use_container_width=True,
                                key=f"selected_df_product_custom_{sector}_{product}",
                            )

                            dict_routes_selected[f"{sector}_{product}"] = (
                                edited_selected_df_product
                            )
# --- IMPORT PATHWAY FROM .txt FILE ---
    if upload_mix_checked:
        st.text("Drag & drop .csv file")

        uploaded_file = st.file_uploader(
            "Upload your pathway file here", type=["txt"]
        )
        if uploaded_file:

            configuration_id_EUMIX_weight = import_to_dict(uploaded_file)
            # Convert values to float & int
            configuration_id_EUMIX_weight = {
                int(k): float(v) for k, v in configuration_id_EUMIX_weight.items()
            }

            # List creation to displai tabs and configuration visualisation/modification
            sectors_list = []

            # Ensure configuration_id_EUMIX_weight keys are treated as integers
            valid_config_id = set(
                map(int, configuration_id_EUMIX_weight.keys()))
            # Filter and extract unique, sorted sector names
            filtered_df = df[df["configuration_id"].isin(valid_config_id)]
            unique_sectors = sorted(filtered_df["sector_name"].unique())
            for sector in unique_sectors:
                sectors_list.append(sector)
            tabs = st.tabs(sectors_list)
            for i, sector in enumerate(sectors_list):
                with tabs[i]:
                    all_products = sorted(
                        df[df["sector_name"] == sector]["product_name"].unique()
                    )
                    for product in all_products:
                        with st.expander(f"{product}", expanded=False):
                            # Filter for sector-product sand copy
                            df_product = df[
                                (df["sector_name"] == sector)
                                & (df["product_name"] == product)
                            ].copy()

                            # Preselect configurations relevant to EU-MIX
                            df_product["selected"] = df_product["configuration_id"].isin(
                                valid_config_id
                            )
                            df_product["route_weight"] = (
                                df_product["configuration_id"]
                                .map(configuration_id_EUMIX_weight)
                                .fillna(0)
                            )
                            cols = df_product.columns.tolist()
                            cols.remove("selected")
                            df_product = df_product[["selected"] + cols].reset_index(
                                drop=True
                            )

                            # Show editable checkbox table
                            edited_df = st.data_editor(
                                df_product,
                                num_rows="fixed",
                                column_config={
                                    "selected": st.column_config.CheckboxColumn("selected")
                                },
                                column_order=columns_to_show_selection,
                                disabled=df_product.columns.difference(
                                    ["selected"]
                                ).tolist(),
                                hide_index=True,
                                key=f"editor_eumix_{sector}_{product}",
                            )

                            # Filter selected and apply equal weights if not preset
                            selected_df_product = edited_df[
                                edited_df["selected"] == True
                            ].copy()

                            # Allow user to edit weights manually
                            st.text("Edit the weight (%)")
                            edited_selected_df_product = st.data_editor(
                                selected_df_product,
                                num_rows="fixed",
                                column_config={
                                    "route_weight": st.column_config.NumberColumn(
                                        "route_weight"
                                    )
                                },
                                disabled=selected_df_product.columns.difference(
                                    ["route_weight"]
                                ).tolist(),
                                hide_index=True,
                                column_order=[
                                    "configuration_name", "route_weight"],
                                use_container_width=True,
                                key=f"selected_df_product_eumix_{sector}_{product}",
                            )

                            # Store result in final selection dictionary
                            dict_routes_selected[f"{sector}_{product}"] = (
                                edited_selected_df_product
                            )

            st.text("To build....")

# --- PATHWAY NAMING AND SAVING ---
    if pathway_name in pre_choices_name_list:
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
