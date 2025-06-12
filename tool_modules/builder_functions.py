from tool_modules.categorisation import *
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.import_export_file import *
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st


def edit_dataframe_selection_and_weighting(df):
    st.write(df)

# Streamlit interface and data tools


def _other_sectors_product(df):
    """
    Display configurations not belonging to the main sectors under 'Other sectors'.

    Returns:
    - dict: Mapping from sector_product string to edited dataframe.
    """
    st.write("Under construction")


def preconfigure_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    # Preconfigure mix option
    eumix_options = ["EU-MIX-2018", "EU-MIX-2030",
                     "EU-MIX-2040", "EU-MIX-2050"]

    selected_mix = st.radio(
        "Select an EU-MIX scenario", eumix_options, index=0)
    pathway_name = selected_mix
    if pathway_name in eumix_options:  # only for aidre_eu_mix
        configuration_id_EUMIX_weight = eu_mix_configuration_id_weight(
            pathway_name)
    # Convert values to float & int
    configuration_id_EUMIX_weight = {
        int(k): float(v) for k, v in configuration_id_EUMIX_weight.items()
    }
    # modified verification intialisation
    modified = False
    # List creation to displai tabs and configuration visualisation/modification
    sectors_list = []
    # Ensure configuration_id_EUMIX_weight keys are treated as integers
    valid_config_id = set(map(int, configuration_id_EUMIX_weight.keys()))
    # Filter and extract unique, sorted sector names
    filtered_df = df[df["configuration_id"].isin(valid_config_id)]
    unique_sectors = sorted(filtered_df["sector_name"].unique())
    if st.checkbox("Edit pathway"):
        sectors_list = unique_sectors.copy()
        sectors_list_plus_other = sectors_list + ["Other sectors"]
        selected_sectors = st.pills(
            "Select sector(s) to configure",
            sectors_list_plus_other,
            selection_mode="multi",
            default=sectors_list
        )
        if len(selected_sectors) < 1:
            st.warning("Please select at least one sector")
        else:
            tabs = st.tabs(selected_sectors)
            for i, sector in enumerate(selected_sectors):
                with tabs[i]:
                    if sector == "Other sectors":
                        dict_other = _other_sectors_product(
                            df,
                        )
                        dict_routes_selected.update(dict_other)
                        continue
                    all_products = sorted(
                        df[df["sector_name"] == sector]["product_name"].unique()
                    )
                    for product in all_products:
                        with st.expander(f"{product}", expanded=False):
                            df_product = df[
                                (df["sector_name"] == sector)
                                & (df["product_name"] == product)
                            ].copy()
                            edited_selected_df_product, was_modified = edit_dataframe_selection_and_weighting(
                                df_product, configuration_id_EUMIX_weight, columns_to_show_selection, sector, product, "eumix"
                            )
                            total_weight = edited_selected_df_product["route_weight"].sum(
                            )
                            if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                                dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                            else:
                                st.warning(
                                    f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
                            if was_modified:
                                modified = True
    else:
        for sector in unique_sectors:
            all_products = sorted(
                df[df["sector_name"] == sector]["product_name"].unique()
            )
            for product in all_products:
                # Filter for sector-product and copy
                df_product = df[
                    (df["sector_name"] == sector)
                    & (df["product_name"] == product)
                ].copy()
                df_product["selected"] = df_product["configuration_id"].isin(
                    valid_config_id)
                df_product["route_weight"] = (
                    df_product["configuration_id"].astype(int)
                    .map(configuration_id_EUMIX_weight)
                    .fillna(0)
                )
                total_weight = df_product["route_weight"].sum()
                if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                    dict_routes_selected[f"{sector}_{product}"] = df_product
                else:
                    st.warning(
                        f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
    # Check if modified or not
    if modified:
        pathway_name += " modified"
    return dict_routes_selected, selected_mix, pathway_name


def create_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    # pathway name initial
    pathway_name = "Pathway 1"
    sectors_list = []
    for sector in sorted(df["sector_name"].unique()):
        sectors_list.append(sector)
    sectors_list_plus_other = sectors_list.copy()
    # Add "Other sectors" option
    sectors_list_plus_other.append("Other sectors")
    selected_sectors = st.pills(
        "Sector(s)", sectors_list_plus_other, selection_mode="multi")
    if len(selected_sectors) < 1:
        st.text("Please select at least 1 sector")
    else:
        tabs = st.tabs(selected_sectors)
        for i, sector in enumerate(selected_sectors):
            with tabs[i]:
                if sector == "Other sectors":
                    dict_other = _other_sectors_product(
                        df)
                    dict_routes_selected.update(dict_other)
                    continue
                all_products = sorted(
                    df[df["sector_name"] == sector]["product_name"].unique()
                )
                for product in all_products:
                    with st.expander(f"{sector} - {product}", expanded=False):
                        df_product = df[df["product_name"] == product].copy()
                        # Default: unselected
                        df_product["selected"] = False
                        cols = df_product.columns.tolist()
                        cols.remove("selected")
                        df_product = df_product[[
                            "selected"] + cols].reset_index(drop=True)
                        # Use helper for editing selection and weighting
                        edited_selected_df_product, _ = edit_dataframe_selection_and_weighting(
                            df_product, set(), columns_to_show_selection, sector, product, "custom"
                        )
                        total_weight = edited_selected_df_product["route_weight"].sum(
                        )
                        if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                            dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                        else:
                            st.warning(
                                f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
    all_empty = all(df.empty for df in dict_routes_selected.values())

    if all_empty:
        st.warning("Select at least one production route")
        return {}, pathway_name

    return dict_routes_selected, pathway_name


def upload_path(df, columns_to_show_selection):
    # Initalisation of modifed
    modified = False
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    st.text("Drag & drop .txt pathway file")
    uploaded_file = st.file_uploader(
        "Upload your pathway file here", type=["txt"]
    )
    pathway_name = "Upload file"
    if uploaded_file:

        configuration_id_EUMIX_weight, pathway_name = import_to_dict(
            uploaded_file)

        if configuration_id_EUMIX_weight:
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
            if st.checkbox("Edit pathway:"):
                for sector in unique_sectors:
                    sectors_list.append(sector)
                sectors_list_plus_other = sectors_list.copy()
                # Add "Other sectors" option
                sectors_list_plus_other.append("Other sectors")
                selected_sectors = st.pills(
                    "Sector(s)", sectors_list_plus_other, selection_mode="multi", default=sectors_list)
                if len(selected_sectors) < 1:
                    st.warning("Please select at least 1 sector")
                else:
                    tabs = st.tabs(selected_sectors)
                    for i, sector in enumerate(selected_sectors):
                        with tabs[i]:
                            if sector == "Other sectors":
                                dict_other = _other_sectors_product(
                                    df)
                                dict_routes_selected.update(dict_other)
                                continue
                            all_products = sorted(
                                df[df["sector_name"] ==
                                    sector]["product_name"].unique()
                            )
                            for product in all_products:
                                with st.expander(f"{product}", expanded=False):
                                    df_product = df[
                                        (df["sector_name"] == sector)
                                        & (df["product_name"] == product)
                                    ].copy()
                                    edited_selected_df_product, was_modified = edit_dataframe_selection_and_weighting(
                                        df_product, configuration_id_EUMIX_weight, columns_to_show_selection, sector, product, "eumix"
                                    )
                                    total_weight = edited_selected_df_product["route_weight"].sum(
                                    )
                                    if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                                        dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                                    else:
                                        st.warning(
                                            f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
                                    if was_modified:
                                        modified = True
            else:
                for sector in unique_sectors:
                    all_products = sorted(
                        df[df["sector_name"] == sector]["product_name"].unique()
                    )
                    for product in all_products:
                        # Filter for sector-product and copy
                        df_product = df[
                            (df["sector_name"] == sector)
                            & (df["product_name"] == product)
                        ].copy()
                        df_product["selected"] = df_product["configuration_id"].isin(
                            valid_config_id)
                        df_product["route_weight"] = (
                            df_product["configuration_id"].astype(int)
                            .map(configuration_id_EUMIX_weight)
                            .fillna(0)
                        )
                        total_weight = df_product["route_weight"].sum()
                        if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                            dict_routes_selected[f"{sector}_{product}"] = df_product
                        else:
                            st.warning(
                                f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
    # Check if modified or not
    if modified is True:
        pathway_name += " modified"
    return dict_routes_selected, pathway_name
