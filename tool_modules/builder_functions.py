# Streamlit interface and data tools
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json

from tool_modules.import_export_file import *
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *


def preconfigure_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    # Preconfigure mix option
    eumix_options = ["EU-MIX-2018", "EU-MIX-2030",
                     "EU-MIX-2040", "EU-MIX-2050"]

    selected_mix = st.radio(
        "Select an EU-MIX scenario", eumix_options, index=0)
    pathway_name = selected_mix
    configuration_id_EUMIX_weight = eu_mix_configuration_id_weight(
        pathway_name)
    # Convert values to float & int
    configuration_id_EUMIX_weight = {
        int(k): float(v) for k, v in configuration_id_EUMIX_weight.items()
    }

    # List creation to displai tabs and configuration visualisation/modification
    sectors_list = []
    # Ensure configuration_id_EUMIX_weight keys are treated as integers
    valid_config_id = set(map(int, configuration_id_EUMIX_weight.keys()))
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
                    # Filter for sector-product and copy
                    df_product = df[
                        (df["sector_name"] == sector)
                        & (df["product_name"] == product)
                    ].copy()

                    # Preselect configurations relevant to EU-MIX
                    df_product["selected"] = df_product["configuration_id"].isin(
                        valid_config_id
                    )
                    df_product["route_weight"] = (
                        df_product["configuration_id"].astype(int)
                        .map(configuration_id_EUMIX_weight)
                        .fillna(0)
                    )

                    # Move "selected" column to front
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
                    total_weight = edited_selected_df_product["route_weight"].sum(
                    )

                    if 99.99 < total_weight < 100.01:
                        # Store result in final selection dictionary
                        dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                    else:
                        st.error(
                            f"Sum of weights should be approximately 100%, not {total_weight:.2f}")

    return dict_routes_selected, selected_mix, pathway_name


def create_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    # pathway name initial
    pathway_name = "Pathway 1"
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
                        total_weight = edited_selected_df_product["route_weight"].sum(
                        )
                        if 99.99 <= total_weight <= 100.01:
                            # Store result in final selection dictionary
                            dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                        else:
                            st.error(
                                f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
    return dict_routes_selected, pathway_name


def upload_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    st.text("Drag & drop .csv file")
    uploaded_file = st.file_uploader(
        "Upload your pathway file here", type=["txt"]
    )
    pathway_name = "Imported pathway"

    if uploaded_file:

        configuration_id_EUMIX_weight, pathway_name = import_to_dict(
            uploaded_file)
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

                        total_weight = edited_selected_df_product["route_weight"].sum(
                        )
                        if 99.99 <= total_weight <= 100.01:
                            # Store result in final selection dictionary
                            dict_routes_selected[f"{sector}_{product}"] = edited_selected_df_product
                        else:
                            st.error(
                                f"Sum of weights should be approximately 100%, not {total_weight:.2f}")

    return dict_routes_selected, pathway_name
