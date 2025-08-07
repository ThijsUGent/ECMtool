from tool_modules.categorisation import *
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.import_export_file import *
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st


import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sectors_list_all = ["Cement", "Chemical",
                    "Fertilisers", "Glass", "Refineries", "Steel"]


def edit_dataframe_selection_and_weighting(df_product, columns_to_show_selection, sector, product, mode_key, df_upload=None):
    """
    Allows user to select and assign weights to production routes using Streamlit data editors.

    Parameters:
    - df_product (pd.DataFrame): Subset of the main dataframe for one sector-product.
    - columns_to_show_selection (list): Ordered list of columns to display in the selection editor.
    - sector (str): Sector name.
    - product (str): Product name.
    - mode_key (str): Prefix key for Streamlit widget keys to differentiate mode (e.g., 'eumix', 'custom').
    - df_upload (pd.DataFrame, optional): Previously uploaded selection with 'route_name' and 'route_weight'.

    Returns:
    - pd.DataFrame: Edited DataFrame containing selected routes with parameters and weights.
    - bool: True if edited, False otherwise.
    """
    columns_param = [
        "electricity_[gj/t]", "alternative_fuel_mixture_[gj/t]", "biomass_[gj/t]",
        "biomass_waste_[gj/t]", "coal_[gj/t]", "coke_[gj/t]", "crude_oil_[gj/t]",
        "hydrogen_[gj/t]", "methanol_[gj/t]", "ammonia_[gj/t]", "naphtha_[gj/t]",
        "natural_gas_[gj/t]", "plastic_mix_[gj/t]", "alternative_fuel_mixture_[t/t]",
        "biomass_[t/t]", "biomass_waste_[t/t]", "coal_[t/t]", "coke_[t/t]",
        "crude_oil_[t/t]", "hydrogen_[t/t]", "methanol_[t/t]", "ammonia_[t/t]",
        "naphtha_[t/t]", "natural_gas_[t/t]", "plastic_mix_[t/t]",
        "co2_allowance_[eur/t]", "direct_emission_[tco2/t]", "total_emission_[tco2/t]",
        "direct_emission_reduction_[%]", "total_emission_reduction_[%]", "captured_co2_[tco2/t]"
    ]

    # Apply uploaded data if available
    if df_upload is not None:
        df_product["selected"] = df_product["route_name"].isin(
            df_upload["route_name"])
        df_upload_map = df_upload.set_index(
            "route_name")["route_weight"].to_dict()
        df_product["route_weight"] = df_product["route_name"].map(
            df_upload_map).fillna(0)
    else:
        df_product["selected"] = False
        df_product["route_weight"] = None

    # Reorder columns to place 'selected' first
    cols = df_product.columns.tolist()
    cols.remove("selected")
    df_product = df_product[["selected"] + cols].reset_index(drop=True)

    # Selection editor
    edited_df = st.data_editor(
        df_product,
        num_rows="fixed",
        column_config={
            "selected": st.column_config.CheckboxColumn("selected")},
        column_order=columns_to_show_selection,
        disabled=df_product.columns.difference(["selected"]).tolist(),
        hide_index=True,
        key=f"editor_{mode_key}_{sector}_{product}",
    )

    selected_df = edited_df[edited_df["selected"] == True].copy()
    modified = not edited_df.equals(df_product)

    if modified:
        if not selected_df.empty:
            selected_df["route_weight"] = round(1 / len(selected_df), 4) * 100
        else:
            selected_df["route_weight"] = 0

    # Streamlit tabs for editing weights and parameters
    tab1, tab2 = st.tabs(["Edit the weight (%)", "Edit route parameters"])

    with tab1:
        edited_selected_df = st.data_editor(
            selected_df,
            num_rows="fixed",
            column_config={
                "route_weight": st.column_config.NumberColumn("route_weight")},
            disabled=selected_df.columns.difference(["route_weight"]).tolist(),
            hide_index=True,
            column_order=["route_name", "route_weight"],
            use_container_width=True,
            key=f"weight_editor_{mode_key}_{sector}_{product}",
        )

    with tab2:
        column_to_show = ["route_name"] + columns_param

        edited_selected_df = st.data_editor(
            edited_selected_df,
            num_rows="fixed",
            disabled=selected_df.columns.difference(columns_param).tolist(),
            hide_index=True,
            column_order=column_to_show,
            use_container_width=True,
            key=f"param_editor_{mode_key}_{sector}_{product}",
        )

        # Optional: flag modified routes by checking parameter changes
        for route in edited_selected_df["route_name"].unique():
            edited_subset = edited_selected_df[edited_selected_df["route_name"]
                                               == route][columns_param]
            original_subset = selected_df[selected_df["route_name"]
                                          == route][columns_param]

            if not edited_subset.equals(original_subset):
                edited_selected_df.loc[
                    edited_selected_df["route_name"] == route, "route_name"
                ] = route + " modified"
                modified = True

            edited_subset_weight = edited_selected_df["route_weight"]
            original_subset_weight = selected_df["route_weight"]

            if not edited_subset_weight.equals(original_subset_weight):
                modified = True

    if modified:
        st.markdown("**Changes made:**")

        col1, col2 = st.columns(2)

        # ---- COLUMN 1: ROUTE WEIGHT CHANGES ----
        with col1:
            st.text("⚖️ Weight changes")
            found_weight_change = False

            for route in edited_selected_df["route_name"].unique():
                base_route = route.replace(" modified", "")
                edited_row = edited_selected_df[edited_selected_df["route_name"] == route]
                original_row = selected_df[selected_df["route_name"]
                                           == base_route]

                if original_row.empty:
                    continue  # skip unmatched

                if "route_weight" in edited_row.columns:
                    old_weight = original_row["route_weight"].values[0]
                    new_weight = edited_row["route_weight"].values[0]

                    if not pd.isna(old_weight) or not pd.isna(new_weight):
                        if old_weight != new_weight:
                            st.write(
                                f"- `{base_route}`: `{old_weight}` → `{new_weight}`")
                            found_weight_change = True

            if not found_weight_change:
                st.write("No weight changes.")

        # ---- COLUMN 2: ROUTE PARAMETER CHANGES ----
        with col2:
            st.text("⚙️ Parameter changes")
            found_param_change = False

            for route in edited_selected_df["route_name"].unique():
                base_route = route.replace(" modified", "")
                edited_row = edited_selected_df[edited_selected_df["route_name"] == route]
                original_row = selected_df[selected_df["route_name"]
                                           == base_route]

                if original_row.empty:
                    continue  # skip unmatched

                for col in edited_row.columns:
                    if col == "route_weight" or col == "route_name" or col not in original_row.columns:
                        continue  # skip weight column

                    old_value = original_row[col].values[0]
                    new_value = edited_row[col].values[0]

                    if pd.isna(old_value) and pd.isna(new_value):
                        continue
                    if old_value != new_value:
                        st.write(
                            f"- {base_route} *modified* | **{col}**: `{old_value}` → `{new_value}`"
                        )
                        found_param_change = True

            if not found_param_change:
                st.write("No parameter changes.")

    return edited_selected_df, modified
# Streamlit interface and data tools


def _other_sectors_product(df_template=None):
    """
    Display configurations not belonging to the main sectors under 'No-AIDRES products'.

    Returns:
    - dict: Mapping from sector_product string to edited dataframe.
    """
    columns = [
        "electricity_[gj/t]", "alternative_fuel_mixture_[gj/t]", "biomass_[gj/t]",
        "biomass_waste_[gj/t]", "coal_[gj/t]", "coke_[gj/t]", "crude_oil_[gj/t]",
        "hydrogen_[gj/t]", "methanol_[gj/t]", "ammonia_[gj/t]", "naphtha_[gj/t]",
        "natural_gas_[gj/t]", "plastic_mix_[gj/t]", "alternative_fuel_mixture_[t/t]",
        "biomass_[t/t]", "biomass_waste_[t/t]", "coal_[t/t]", "coke_[t/t]",
        "crude_oil_[t/t]", "hydrogen_[t/t]", "methanol_[t/t]", "ammonia_[t/t]",
        "naphtha_[t/t]", "natural_gas_[t/t]", "plastic_mix_[t/t]",
        "co2_allowance_[eur/t]", "direct_emission_[tco2/t]", "total_emission_[tco2/t]",
        "direct_emission_reduction_[%]", "total_emission_reduction_[%]", "captured_co2_[tco2/t]"
    ]
    columns_fixed = ["route_name", "product_name"]

    with st.expander("Energy parameters", expanded=False):
        columns_selected = st.pills(
            "Select energy parameters to edit",
            options=columns,
            default=columns[0],
            selection_mode="multi",
            key="other_sectors_product_selection"
        )
    column_df = columns_fixed + columns_selected
    if df_template is None:
        df_template = pd.DataFrame(
            columns=column_df,
        )
    else:
        df_template = df_template[df_template["sector_name"]
                                  == "No-AIDRES products"].copy()
        for col in column_df:
            if col not in df_template.columns:
                df_template[col] = np.nan
        df_template = df_template[column_df]
    # Enforce data types
    for col in columns_fixed:
        df_template[col] = df_template[col].astype(str)
    for col in columns_selected:
        df_template[col] = df_template[col].astype(float)

    df_edit = st.data_editor(
        df_template,
        num_rows="dynamic",
        hide_index=True,
        column_order=column_df,
        use_container_width=True,
        key="other_sectors_product"
    )
    df_edit[[col for col in columns if col not in columns_selected]] = 0
    df_edit["sector_name"] = "No-AIDRES products"
    df_edit["energy_feedstock"] = " "
    df_edit["route_weight"] = 100

    result_dict = {}
    grouped = df_edit.groupby(["sector_name", "product_name"])
    for (sector, product), group_df in grouped:
        result_dict[f"{sector}_{product}"] = group_df
    return result_dict


def preconfigure_path(df, columns_to_show_selection):
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    # Preconfigure mix option
    premade_choice = ["EU-MIX-2018", "EU-MIX-2030",
                      "EU-MIX-2040", "EU-MIX-2050", "IEA Net Zero Emissions Scenario", "Electrification ECM Scenario"]
    AIDRES_options = ["EU-MIX-2018", "EU-MIX-2030",
                      "EU-MIX-2040", "EU-MIX-2050",]

    # Load CSV with scenario info
    pathway_description = pd.read_csv(
        "data/premade_pathway/premade_pathway_description.csv")

    # Extract list of scenarios for the radio options
    premade_choice = pathway_description["Scenario"].tolist()

    # Radio button for scenario selection
    selected_mix = st.radio("Select an EU-MIX scenario",
                            premade_choice, index=0)

    # Filter dataframe for the selected scenario info
    info = pathway_description[pathway_description["Scenario"]
                               == selected_mix].iloc[0]

    # Display info below the radio buttons
    st.markdown(f"**Description:** {info['Description']}")
    if pd.notna(info["Reference"]) and info["Reference"].strip():
        if "ReferenceURL" in info and pd.notna(info["ReferenceURL"]) and info["ReferenceURL"].strip():
            st.markdown(
                f"**Reference:** [{info['Reference']}]({info['ReferenceURL']})")
        else:
            st.markdown(f"**Reference:** {info['Reference']}")
    pathway_name = selected_mix
    if pathway_name in AIDRES_options:  # only for aidre_eu_mix
        df_upload = eu_mix_configuration_id_weight(
            pathway_name)
    else:  # for custom pathway
        if pathway_name == "IEA Net Zero Emissions Scenario":
            file_premade = pd.read_csv(
                "data/premade_pathway/ECM_Tool_IEA-NET-ZERO-2050.txt")
        elif pathway_name == "Electrification ECM Scenario":
            file_premade = pd.read_csv(
                "data/premade_pathway/ECM_Tool_EU-MIX-2050-ELECTRIFICATION.txt")
        df_upload = file_premade
    # modified verification intialisation
    modified = False
    # List creation to displai tabs and configuration visualisation/modification
    sectors_list = []

    # Filter and extract unique, sorted sector names
    filtered_df = df[df["route_name"].isin(
        df_upload["route_name"])]
    unique_sectors = sorted(filtered_df["sector_name"].unique())
    if st.checkbox("Edit pathway"):
        sectors_list = unique_sectors.copy()
        sectors_list_plus_other = sectors_list_all + ["No-AIDRES products"]
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
                    if sector == "No-AIDRES products":
                        dict_other = _other_sectors_product(

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
                                df_product, columns_to_show_selection, sector, product, "eumix", df_upload
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
                df_product["selected"] = df_product["route_name"].isin(
                    df_upload["route_name"])
                df_upload_map = df_upload.set_index("route_name")[
                    "route_weight"].to_dict()

                df_product["route_weight"] = (
                    df_product["route_name"]
                    .map(df_upload_map)
                    .fillna(0)
                )
                total_weight = df_product["route_weight"].sum()
                if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                    dict_routes_selected[f"{sector}_{product}"] = df_product
                else:
                    st.warning(
                        f"Sum of weights should be approximately 100%, not {total_weight:.2f}")
    if any("No-AIDRES products" in key.split("_")[0] for key in dict_routes_selected.keys()):
        modified = True
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
    # Add "No-AIDRES products" option
    sectors_list_plus_other.append("No-AIDRES products")
    selected_sectors = st.pills(
        "Sector(s)", sectors_list_plus_other, selection_mode="multi")
    if len(selected_sectors) < 1:
        st.text("Please select at least 1 sector")
    else:
        tabs = st.tabs(selected_sectors)
        for i, sector in enumerate(selected_sectors):
            with tabs[i]:
                if sector == "No-AIDRES products":
                    dict_other = _other_sectors_product(
                    )
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
                            df_product, columns_to_show_selection, sector, product, "custom"
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
    # Initialisiation list of sectors

    sectors_list_plus_other = sectors_list_all.copy()
    # Add "No-AIDRES products" option
    sectors_list_plus_other.append("No-AIDRES products")
    # Initalisation of modifed
    modified = False
    # Dictionary to collect selected routes per sector-product
    dict_routes_selected = {}
    st.text("Drag & drop .txt pathway file")
    uploaded_file = st.file_uploader(
        "Upload your pathway file here", type=["txt"]
    )
    pathway_name = "Upload file"
    if uploaded_file is not None:
        pathway_name = uploaded_file.name.replace(
            "ECM_Tool_", "").replace("_", " ").rsplit(".", 1)[0]
        df_upload = import_to_dict(uploaded_file)
        if not df_upload.empty:
            # List creation to display tabs and configuration visualisation/modification
            sectors_list = []
            unique_sectors = sorted(df_upload["sector_name"].unique())
            if st.checkbox("Edit pathway:"):
                for sector in unique_sectors:
                    sectors_list.append(sector)
                selected_sectors = st.pills(
                    "Sector(s)", sectors_list_plus_other, selection_mode="multi", default=sectors_list)
                if len(selected_sectors) < 1:
                    st.warning("Please select at least 1 sector")
                else:
                    tabs = st.tabs(selected_sectors)
                    for i, sector in enumerate(selected_sectors):
                        with tabs[i]:
                            if sector == "No-AIDRES products":
                                if "No-AIDRES products" not in df_upload["sector_name"].values:
                                    dict_other = _other_sectors_product(
                                    )
                                else:
                                    dict_other = _other_sectors_product(
                                        df_template=df_upload
                                    )
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
                                        df_product, columns_to_show_selection, sector, product, "eumix", df_upload
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
                    if sector == "No-AIDRES products":
                        df_upload_other = df_upload[df_upload["sector_name"]
                                                    == "No-AIDRES products"]
                        dict_routes_other = {}
                        for product in df_upload_other["product_name"].unique():

                            dict_routes_other[f"{sector}_{product}"] = df_upload[df_upload["route_name"] == product]
                        dict_routes_selected.update(dict_routes_other)
                        continue
                    all_products = sorted(
                        df[df["sector_name"] == sector]["product_name"].unique()
                    )
                    for product in all_products:
                        # Filter for sector-product and copy
                        df_product = df[
                            (df["sector_name"] == sector)
                            & (df["product_name"] == product)
                        ].copy()
                        df_product["selected"] = df_product["route_name"].isin(
                            df_upload["route_name"])
                        df_upload_map = df_upload.set_index("route_name")[
                            "route_weight"].to_dict()

                        df_product["route_weight"] = (
                            df_product["route_name"]
                            .map(df_upload_map)
                            .fillna(0)
                        )
                        total_weight = df_product["route_weight"].sum()
                        if 99.95 <= total_weight <= 100.05 or total_weight == 0:
                            dict_routes_selected[f"{sector}_{product}"] = df_product
                        else:
                            st.warning(
                                f"Sum of weights should be approximately 100%, not {total_weight:.2f}")

        if any("No-AIDRES products" in key.split("_")[0] for key in dict_routes_selected.keys()):
            modified = True
        # Check if modified or not
        if modified is True:
            pathway_name += " modified"
    return dict_routes_selected, pathway_name
