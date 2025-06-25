import os
import io
import math
import base64
from io import BytesIO

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageDraw
from shapely import wkt, wkb
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler

from tool_modules.cluster import *

type_ener_feed = ["electricity_[mwh/t]",
                  "electricity_[gj/t]",
                  "alternative_fuel_mixture_[gj/t]",
                  "biomass_[gj/t]",
                  "biomass_waste_[gj/t]",
                  "coal_[gj/t]",
                  "coke_[gj/t]",
                  "crude_oil_[gj/t]",
                  "hydrogen_[gj/t]",
                  "methanol_[gj/t]",
                  "ammonia_[gj/t]",
                  "naphtha_[gj/t]",
                  "natural_gas_[gj/t]",
                  "plastic_mix_[gj/t]",
                  "alternative_fuel_mixture_[t/t]",
                  "biomass_[t/t]",
                  "biomass_waste_[t/t]",
                  "coal_[t/t]",
                  "coke_[t/t]",
                  "crude_oil_[t/t]",
                  "hydrogen_[t/t]",
                  "methanol_[t/t]",
                  "ammonia_[t/t]",
                  "naphtha_[t/t]",
                  "natural_gas_[t/t]",
                  "plastic_mix_[t/t]"]

# Original color map
color_map = {
    "electricity_[gj/t]": "#ffeda0",   # yellow pastel
    "alternative_fuel_mixture_[gj/t]": "#fdd49e",  # light orange
    "biomass_[gj/t]": "#c7e9c0",       # light green
    "biomass_waste_[gj/t]": "#a1d99b",  # green pastel
    "coal_[gj/t]": "#cccccc",          # light grey
    "coke_[gj/t]": "#bdbdbd",          # grey
    "crude_oil_[gj/t]": "#fdae6b",     # orange pastel
    "hydrogen_[gj/t]": "#b7d7f4",      # light blue
    "methanol_[gj/t]": "#fdd0a2",      # soft orange
    "ammonia_[gj/t]": "#d9f0a3",       # lime pastel
    "naphtha_[gj/t]": "#fcbba1",       # peach
    "natural_gas_[gj/t]": "#89a0d0",   # light blue
    "plastic_mix_[gj/t]": "#e5e5e5",   # very light grey
}

# Extend with cleaned keys (underscore removed, suffix dropped, and underscore replaced with space)
color_map.update({
    " ".join(key.split("_")[:-1]): value
    for key, value in color_map.items()
})

# Radius scale


def _get_radius(df):

    top_1_val = df["total_energy"].quantile(0.99)
    top_10_val = df["total_energy"].quantile(0.90)
    mean_val = df["total_energy"].mean()

    def classify(val):
        if val >= top_1_val:
            return 20000
        elif val >= top_10_val:
            return 12000
        elif val >= mean_val:
            return 9700
        else:
            return 8000

    return df["total_energy"].apply(classify)


def map_per_utlisation_rate():
    st.write("In progress")


def map_per_pathway():
    path = "data/production_site.csv"
    df = pd.read_csv(path)

    df = df[df["wp1_model_product_name"] != "not included in blue-print model"]

    if "Pathway name" not in st.session_state or not st.session_state["Pathway name"]:
        st.info("No selections stored yet.")
        return

    pathways_names = list(
        st.session_state["Pathway name"].keys())

    # Initialisation of all sectors
    sectors_all_list = ["Chemical", "Cement",
                        "Refineries", "Fertilisers", "Steel", "Glass"]

    type_ener_feed_gj = [item for item in type_ener_feed if "[gj/t]" in item]
    type_ener_feed_t = [item for item in type_ener_feed if "[t/t]" in item]
    type_ener_feed_mwh = [item for item in type_ener_feed if "[mwh/t]" in item]

    # Labels only (without unit suffix)
    type_ener_name = [" ".join(item.split("_")[:-1])
                      for item in type_ener_feed_gj]
    type_feed_name = [" ".join(item.split("_")[:-1])
                      for item in type_ener_feed_t]

    col1, col2 = st.columns([1, 4])  # 3:1 ratio, left wide, right narrow

    with col1:
        unit = st.radio(
            "Select unit", ["GJ", "t"], horizontal=True
        )

        if unit == "GJ":
            with st.expander("Energy carriers"):
                select_all_energy = st.toggle(
                    "Select all", key="select_all_energy", value=True)

                if select_all_energy:
                    default_ener = type_ener_name
                else:
                    default_ener = []

                options_energy = type_ener_name
                values_energy = type_ener_feed_gj

                selected_energy_labels = st.pills(
                    "Choose energy carriers",
                    options_energy,
                    default=default_ener,
                    label_visibility="visible",
                    selection_mode="multi",
                    key="energy_pills"
                )

                selected_columns = [
                    values_energy[options_energy.index(label)] for label in selected_energy_labels
                ]

        elif unit == "t":
            st.markdown("""*Electricity excluded*""")
            with st.expander("Feedstock"):
                select_all_feed = st.toggle(
                    "Select all", key="select_all_feed", value=True)

                if select_all_feed:
                    default_feed = type_feed_name
                else:
                    default_feed = []

                options_feed = type_feed_name
                values_feed = type_ener_feed_t

                selected_feed_labels = st.pills(
                    "Choose feedstock",
                    options_feed,
                    default=default_feed,
                    label_visibility="visible",
                    selection_mode="multi",
                    key="feed_pills"
                )

                selected_columns = [
                    values_feed[options_feed.index(label)] for label in selected_feed_labels
                ]
        st.divider()
        st.text('Edit utilisation rate per sector')
        st.markdown(""" *Default value 100 %* """)
        with st.expander("Utilisation rate"):
            sector_utilization = _get_utilization_rates(sectors_all_list)
        dict_gdf = {}
        pathways_names_filtered = []
        for pathway in pathways_names:
            gdf_prod_x_perton = _get_gdf_prod_x_perton(
                df, pathway, sector_utilization, selected_columns)
            # Convert to GeoDataFrame
            if gdf_prod_x_perton is not None:
                dict_gdf[pathway] = gdf_prod_x_perton
                pathways_names_filtered.append(pathway)
        st.divider()
        choice = st.radio("Cluster method", [
                          "DBSCAN", "KMEANS", "KMEANS (weighted)"])
        min_samples, radius, n_cluster = _edit_clustering(choice)
        dict_gdf_clustered = {}
        for pathway in pathways_names_filtered:
            gdf_clustered = _run_clustering(
                choice, dict_gdf[pathway], min_samples, radius, n_cluster)
            dict_gdf_clustered[pathway] = gdf_clustered

    with col2:
        col_map_param, col_layers = st.columns([2, 1])
        with col_map_param:
            if pathways_names_filtered == []:
                # or pathways_names.tolist() if it's a Pandas Series
                names = list(pathways_names)
                # Format each name in italics using Markdown
                italic_names = [f"*{name}*" for name in names]

                if len(italic_names) == 1:
                    text = f"{italic_names[0]} not in AIDRES scope"
                elif len(italic_names) == 2:
                    text = f"{italic_names[0]} & {italic_names[1]} not in AIDRES scope"
                else:
                    text = f"{', '.join(italic_names[:-1])} & {italic_names[-1]} not in AIDRES scope"

                st.markdown(text)
                st.warning("Please select a pathway within AIDRES scope")
                st.stop()

            pathway = st.radio("Select a pathway",
                               pathways_names_filtered, horizontal=True)

            sectors_included = dict_gdf_clustered[pathway]["aidres_sector_name"].unique(
            ).tolist()
            sector_seleted = st.pills("Sector(s) included within the pathway:",
                                      sectors_included, selection_mode="multi", default=sectors_included)
            st.markdown(
                '<span style="font-size: 0.85em;">*Only sectors & products included in AIDRES database*</span>', unsafe_allow_html=True)

            map_choice_toggle = st.toggle("Site view")

            if map_choice_toggle:
                map_choice = "site"
                toggle_text = "Site "
            else:
                map_choice = "cluster centroid"
                toggle_text = "Cluster centroid "
            with col_layers:
                gdf_layer = None
                layer_options = None
                # Define display labels and internal values
                layer_options = {
                    "RES potential": "enspresso",
                    "RES production": "RES"
                }

                # # Show radio with display labels
                # layer_label = st.pills(
                #     "Add a layer", list(layer_options.keys()))

                # if layer_label:
                #     # Get internal value
                #     layer = layer_options[layer_label]
                #     if layer == "enspresso":
                #         st.write("Under construction")

                #     elif layer == "RES":
                #         gdf_layer = _layer_RES_generation()
                #         st.write(gdf_layer.columns)

            # Selected sectors
            dict_gdf_clustered[pathway].copy()
            dict_gdf_clustered[pathway] = dict_gdf_clustered[pathway][dict_gdf_clustered[pathway]
                                                                      ["aidres_sector_name"].isin(sector_seleted)]

        if map_choice == "cluster centroid":
            df_selected_site = None
            gdf_clustered_centroid = _summarise_clusters_by_centroid(
                dict_gdf_clustered[pathway])
            st.markdown(
                """*Click on a cluster centroid to see details **below the map***""")
            df_selected = _mapping_chart_per_ener_feed_cluster(
                gdf_clustered_centroid, color_map, unit, gdf_layer)
        if map_choice == "site":
            df_selected = None
            df_selected_site = _mapping_chart_per_ener_feed_sites(
                dict_gdf_clustered[pathway], gdf_layer)
        if df_selected_site is not None:
            _chart_site(df_selected_site, unit)

        if df_selected is not None:
            chart = st.radio("Select an option ", ["Treemap",
                             "Sankey Diagram"])
            df_filtered_cluster = _site_within_cluster(
                df_selected, pathway, dict_gdf_clustered)
            if chart == "Treemap":
                _tree_map(df_selected)
            elif chart == "Sankey Diagram":
                _sankey(df_filtered_cluster, unit)
            with st.expander("Show  or download sites within the cluster"):
                st.text(
                    "It is possible to download the cluster configuration to use it in the cluster tool")
                if df_filtered_cluster is not None:
                    if (df_filtered_cluster["cluster"] == 0).any():
                        # FOR NIENKE FILE

                        # Dictionary of European countries and their codes
                        country_dict = {
                            "Belgium": "BE",
                            "Netherlands": "NL",
                            "France": "FR",
                            "Germany": "DE",
                            "Luxembourg": "LU",
                            "Italy": "IT",
                            "Spain": "ES",
                            "Austria": "AT",
                            "Denmark": "DK",
                            "Sweden": "SE",
                            "Norway": "NO",
                            "Finland": "FI",
                            "Ireland": "IE",
                            "Portugal": "PT",
                            "Poland": "PL",
                            "Czech Republic": "CZ",
                            "Hungary": "HU",
                            "Greece": "GR"
                        }

                        # Let the user choose the country by name
                        selected_country = st.selectbox(
                            "Select a country", list(country_dict.keys()))

                        # Get the corresponding code
                        country = country_dict[selected_country]
                        # Filter + select columns
                        columns_nienke = [
                            "site_name",
                            "aidres_sector_name",
                            "geometry",
                            "electricity_[gj/t] ton",
                            "alternative_fuel_mixture_[gj/t] ton",
                            "biomass_[gj/t] ton",
                            "biomass_waste_[gj/t] ton",
                            "coal_[gj/t] ton",
                            "coke_[gj/t] ton",
                            "crude_oil_[gj/t] ton",
                            "hydrogen_[gj/t] ton",
                            "methanol_[gj/t] ton",
                            "ammonia_[gj/t] ton",
                            "naphtha_[gj/t] ton",
                            "natural_gas_[gj/t] ton",
                            "plastic_mix_[gj/t] ton",
                            "total_energy",
                            "lon",
                            "lat"
                        ]
                        # Filter by NUTS3 and select columns
                        df_filtered_nienke = df_filtered_cluster[df_filtered_cluster["nuts3_code"].str.contains(
                            country)]
                        df_filtered_nienke = df_filtered_nienke[columns_nienke]

                        # Convert geometry from WKT if needed
                        if isinstance(df_filtered_nienke["geometry"].iloc[0], str):
                            df_filtered_nienke["geometry"] = df_filtered_nienke["geometry"].apply(
                                wkt.loads)

                        # Convert to GeoDataFrame
                        gdf = gpd.GeoDataFrame(
                            df_filtered_nienke, geometry="geometry", crs="EPSG:4326")

                        # Write GeoJSON to BytesIO
                        buffer = io.BytesIO()
                        gdf.to_file(buffer, driver="GeoJSON")
                        buffer.seek(0)  # reset pointer

                        # Streamlit download button
                        st.download_button(
                            label="Download GeoJSON for PyPSA",
                            data=buffer,
                            file_name=f"{pathway}_{country}.geojson",
                            mime="application/geo+json"
                        )

                        ############
                    df_filtered_cluster_show = df_filtered_cluster[[
                        "site_name", "aidres_sector_name", "product_name", "prod_cap", "prod_rate", "utilization_rate", "total_energy"]]

                    df_filtered_cluster_show.columns = [
                        col.replace(
                            'utilization rate', 'utilisation rate').replace("site_name", "site").replace("aidres_sector_name", "sector").replace("product_name", "product").replace("prod_cap", "production capacity (kt)").replace("prod_rate", "production rate (kt)").replace("total_energy", "total energy")
                        for col in df_filtered_cluster_show.columns
                    ]
                    st.write(df_filtered_cluster_show)
                    df_filtered_cluster_download = df_filtered_cluster_show[[
                        "site", "sector", "product", "production capacity (kt)"]]
                    cluster = st.text_input(
                        "Enter a name for the cluster",)
                    st.download_button(
                        label="Download cluster configuration",
                        data=df_filtered_cluster_download.to_csv(
                            index=False, sep=","),
                        file_name=f"ECM_Tool_{cluster}_cluster.txt",
                        mime='text/plain'
                    )


def _chart_site(df, unit):
    df["unit"] = unit
    desired_cols = [
        "site_name",
        "sector_name", "product_name", "prod_cap",
        "prod_rate",
        "utilization_rate",
        "total_energy",
        "alternative fuel mixture",
        "ammonia",
        "biomass",
        "biomass waste",
        "coal",
        "coke",
        "crude oil",
        "electricity",
        "hydrogen",
        "methanol",
        "naphtha",
        "natural gas",
        "plastic mix",
        "unit"
    ]

    # Only keep columns that exist in df
    existing_cols = [col for col in desired_cols if col in df.columns]

    st.write(df[existing_cols])


def _site_within_cluster(df_selected, pathway, dict_gdf_clustered):
    if df_selected is not None:
        df = dict_gdf_clustered[pathway]
        nbr_cluster = int(df_selected["cluster"])
        df_filtered_cluster = df[df["cluster"] == nbr_cluster]
        return df_filtered_cluster
    else:
        return None


def _energy_convert(value, unit, elec=False):
    """
    Converts energy values from GJ to higher units (TJ, PJ) or to MWh/TWh if elec=True.

    Parameters:
        value (float): Energy value
        unit (str): Initial unit, expected to be 'GJ'
        elec (bool): If True, converts to MWh or TWh

    Returns:
        (rounded_value, new_unit)
    """
    if unit == "t":
        if value >= 1_000_000:
            return round(value / 1_000_000, 2), "Mt"
        elif value >= 1_000:
            return round(value / 1_000, 2), "kt"
        else:
            return round(value, 2), "t"

    if elec:
        # 1 GJ = 0.277778 MWh
        value_mwh = value * 0.277778
        if value_mwh >= 1_000_000:
            return round(value_mwh / 1_000_000), "TWh"
        else:
            return round(value_mwh), "MWh"
    else:
        if value >= 1_000_000:
            return round(value / 1e6), "PJ"
        elif value >= 1_000:
            return round(value / 1e3), "TJ"
        else:
            return round(value), "GJ"


def _tree_map(df):
    if df is not None and not df.empty:
        # Select relevant columns
        columns_plot = [
            col for col in df.columns
            if any(col.startswith(feed.split("_")[0]) for feed in type_ener_feed)
        ]
        # Extract the single row of interest
        row = df.iloc[0]
        if columns_plot == ["electricity"]:
            elec = True
        else:
            elec = False
        # Prepare long-form dataframe for plotting
        df_long = pd.DataFrame({
            "energy_source": columns_plot,
            "value": [row[col] for col in columns_plot],
            # fallback colour
            "color_value": [color_map.get(col, "#cccccc") for col in columns_plot],
        })

        # Add cleaned label and unit
        df_long["label"] = df_long["energy_source"].str.replace(
            r"_\[.*?\]$", "", regex=True).str.replace("_", " ")
        df_long["unit"] = row["unit"] if "unit" in row else ""

        # Total energy calculation and conversion
        total_energy = df_long["value"].sum()
        unit = df_long["unit"].iloc[0]
        total_energy, unit_real = _energy_convert(total_energy, unit, elec)
        # Create treemap
        fig = px.treemap(
            df_long,
            path=["label"],
            values="value",
            color="energy_source",
            hover_data={"value": True, "unit": True},
            color_discrete_map=dict(
                zip(df_long["energy_source"], df_long["color_value"]))
        )

        fig.update_layout(
            title_text=f"Energy Use Breakdown<br><sub>Total energy per annum: {total_energy} {unit_real}</sub>")

        st.plotly_chart(fig)


def _sankey(df, unit):
    if df is not None:
        energy_cols = [col for col in df.columns if any(
            col.startswith(feed) for feed in type_ener_feed)]

        # Option 1: remove last underscore segment and join with space
        carrier_labels = [" ".join(col.split("_")[:-1]) for col in energy_cols]

        sector_labels = df['aidres_sector_name'].unique().tolist()

        labels = carrier_labels + sector_labels
        label_indices = {label: i for i, label in enumerate(labels)}

        sources, targets, values = [], [], []

        for _, row in df.iterrows():
            sector = row['aidres_sector_name']
            for i, col in enumerate(energy_cols):
                value = row[col]
                if pd.notna(value) and value > 0:
                    source_label = carrier_labels[i]
                    sources.append(label_indices[source_label])
                    targets.append(label_indices[sector])
                    values.append(value)

        link_colors = []
        for s in sources:
            carrier_label = labels[s]
            link_colors.append(color_map.get(carrier_label, 'lightgray'))

        node_colors = []

        # assign colors per node, not per source link
        for label in labels:
            if label in color_map:
                # carrier node color
                node_colors.append(color_map[label])
            else:
                # sector node color
                node_colors.append('lightgrey')
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                line=dict(color="black", width=0.2),
                label=labels,
                color=node_colors,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors
            )
        )])
        total_energy = df["total_energy"].sum()
        total_energy, unit_real = _energy_convert(total_energy, unit)

        fig.update_layout(
            hovermode='x',
            title=dict(
                text=f"Energy Carrier to Sector <br> <sub> Total energy per annum: {total_energy:.2f} {unit_real}</sub>"
            ),
            font=dict(color="black", size=12),
            hoverlabel=dict(font=dict(color="black"))
        )

        st.plotly_chart(fig, use_container_width=True)


def _get_utilization_rates(sectors):
    sector_utilization_defaut = {
        "Fertilisers": 100,
        "Steel": 100,
        "Cement": 100,
        "Refineries": 100,
        "Chemical": 100,
        "Glass": 100,
    }
    sector_utilization = {}
    for sector in sectors:
        st.text("Ulisation rate (%)")
        value = st.slider(f"{sector}", 0, 100,
                          value=sector_utilization_defaut[sector])
        sector_utilization[sector] = value
    return sector_utilization


def _get_gdf_prod_x_perton(df, pathway, sector_utilization, selected_columns):
    perton = st.session_state["Pathway name"][pathway]
    list_keys = list(perton.keys())
    sectors_list = []
    for key in list_keys:
        sectors_list.append(key.split("_")[0])
    unique_sectors = set(sectors_list)
    if unique_sectors == {"No-AIDRES products"}:

        return None

        # Convert WKB hex to geometry
    df['geometry'] = df['geom'].apply(lambda x: wkb.loads(bytes.fromhex(x)))

    # Convert to GeoDataFrame
    gdf_production_site = gpd.GeoDataFrame(
        df.drop(columns="geom"), geometry='geometry', crs="EPSG:4326")

    for sector, utilization_rate in sector_utilization.items():

        # Matching sector & utlisation rate
        matching = gdf_production_site["aidres_sector_name"] == sector
        gdf_production_site.loc[matching,
                                "utilization_rate"] = utilization_rate

    # Condition : prod_rate if prod_cap extist, but not prod_rate
    prod_rate_cap_utli_condi_1 = gdf_production_site["utilization_rate"] / \
        100 * gdf_production_site["prod_cap"]

    condition_1 = (gdf_production_site["prod_rate"].isna() &
                   gdf_production_site["prod_cap"].notna() &
                   gdf_production_site["utilization_rate"].notna())

    gdf_production_site["prod_rate"] = np.where(
        condition_1, prod_rate_cap_utli_condi_1, gdf_production_site["prod_rate"])

    # Condition : prod_rate if prod_rate exist but not prod_cap
    prod_rate_cap_utli_condi_2 = gdf_production_site["utilization_rate"] / \
        100 * gdf_production_site["prod_rate"]

    condition_2 = (gdf_production_site["prod_rate"].notna() &
                   gdf_production_site["prod_cap"].isna() &
                   gdf_production_site["utilization_rate"].notna())

    gdf_production_site["prod_rate"] = np.where(
        condition_2, prod_rate_cap_utli_condi_2, gdf_production_site["prod_rate"])

    # Condition : prod_rate if prod_rate exist and prod_cap
    prod_rate_cap_utli_condi_3 = gdf_production_site["utilization_rate"] / \
        100 * gdf_production_site["prod_cap"]

    condition_3 = (gdf_production_site["prod_rate"].isna() &
                   gdf_production_site["prod_cap"].isna() &
                   gdf_production_site["utilization_rate"].notna())

    gdf_production_site["prod_rate"] = np.where(
        condition_3, prod_rate_cap_utli_condi_3, gdf_production_site["prod_rate"])

    # Multiply per ton with matching product
    sectors_products = list(perton.keys())
    df_pathway_weighted = pd.DataFrame()
    columns = selected_columns

    for sector_product in sectors_products:
        product = sector_product.split("_")[-1]
        sector = sector_product.split("_")[0]
        dfs_dict_path = st.session_state["Pathway name"][pathway]
        df_path = pd.concat(dfs_dict_path.values(), ignore_index=True)

        df_filtered = df_path[df_path["product_name"] == product]

        if not df_filtered.empty:
            def weighted_avg(df, value_cols, weight_col):
                return pd.Series({
                    col: np.average(df[col], weights=df[weight_col]) for col in value_cols
                })

            df_filtered_weight = df_filtered.groupby("product_name").apply(
                weighted_avg, value_cols=columns, weight_col="route_weight"
            ).reset_index()

            df_filtered_weight["sector_name"] = sector  # retain sector info

            # Correct way to append data to the final DataFrame
            df_pathway_weighted = pd.concat(
                [df_pathway_weighted, df_filtered_weight], ignore_index=True)

    # Optional: only display once, outside the loop

    gdf_prod_x_perton = gdf_production_site.merge(
        df_pathway_weighted,
        how="left",
        left_on="wp1_model_product_name",
        right_on="product_name",
    )

    for column in columns:
        gdf_prod_x_perton[column] = gdf_prod_x_perton[column] * \
            gdf_prod_x_perton["prod_rate"] * 1000  # prod rate kt

    gdf_prod_x_perton['total_energy'] = gdf_prod_x_perton[columns].sum(
        axis=1)

    for column in columns:
        gdf_prod_x_perton.rename(
            columns={column: f"{column} ton"}, inplace=True)
    gdf_prod_x_perton = gdf_prod_x_perton[gdf_prod_x_perton["sector_name"].notnull(
    )]

    return gdf_prod_x_perton


def _mapping_chart_per_ener_feed_cluster(gdf, color_map, unit, gdf_layer):

    # --- Prepare Data ---
    type_ener_feed = list(color_map.keys())
    energy_cols = [col for col in gdf.columns if "[" in col]
    rename_map = {col: " ".join(col.split("_")[:-1]) for col in energy_cols}
    gdf = gdf.rename(columns=rename_map)

    energy_cols = [col for col in gdf.columns if any(
        col.startswith(feed.split("_")[0]) for feed in type_ener_feed)]

    if (gdf[energy_cols].sum(axis=1) == 0).all():
        return st.warning("Select feedstock(s) or energy carrier(s)")

    elec = energy_cols == ["electricity"]
    gdf["total_energy"] = gdf[energy_cols].sum(axis=1)
    gdf = gdf[gdf["total_energy"] > 0].copy()
    gdf["unit"] = unit
    gdf["total_energy_rounded"] = gdf["total_energy"].round().astype(int)
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y
    gdf["radius"] = _get_radius(gdf)

    def polar_to_cartesian(cx, cy, r, angle_deg):
        angle_rad = math.radians(angle_deg)
        return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

    def generate_pie_svg_base64(row):
        values = row[energy_cols]
        segments = [(col, val)
                    for col, val in zip(energy_cols, values) if val > 0]
        if not segments:
            return ""
        total = sum(val for _, val in segments)
        cx, cy, r = 50, 50, 50
        paths = []

        if len(segments) == 1:
            col, _ = segments[0]
            colour = color_map.get(col, "#000000")
            paths.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{colour}" />')
        else:
            start_angle = 0
            for col, val in segments:
                pct = val / total
                end_angle = start_angle + pct * 360
                x1, y1 = polar_to_cartesian(cx, cy, r, start_angle)
                x2, y2 = polar_to_cartesian(cx, cy, r, end_angle)
                large_arc_flag = 1 if end_angle - start_angle > 180 else 0
                colour = color_map.get(col, "#000000")
                d = f"M {cx},{cy} L {x1},{y1} A {r},{r} 0 {large_arc_flag} 1 {x2},{y2} Z"
                paths.append(f'<path d="{d}" fill="{colour}" />')
                start_angle = end_angle

        svg = f'<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">{"".join(paths)}</svg>'
        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"

    gdf["icon_url"] = gdf.apply(generate_pie_svg_base64, axis=1)

    def build_total_html(row):
        total_formatted, unit_formatted = _energy_convert(
            row['total_energy_rounded'], row['unit'], elec)
        return f"{total_formatted} {unit_formatted}"

    gdf["total_html"] = gdf.apply(build_total_html, axis=1)

    def generate_pie_legend(row):
        values = row[energy_cols]
        segments = [(col, val)
                    for col, val in zip(energy_cols, values) if val > 0]
        if not segments:
            return ""
        total = sum(val for _, val in segments)
        legend_rows = []
        start = 0
        for col, val in segments:
            colour = color_map.get(col, "#000000")
            legend_rows.append(f"""
                <div style="display: flex; align-items: center; margin-bottom: 2px;">
                    <div style="width: 12px; height: 12px; background-color: {colour}; margin-right: 6px; border-radius: 2px;"></div>
                    <span style="font-size: 11px; color: white;">{col}</span>
                </div>
            """)
        return "".join(legend_rows)

    gdf["pie_html"] = gdf.apply(generate_pie_legend, axis=1)

    icon_data = gdf.copy()
    icon_data["icon"] = icon_data.apply(lambda row: {
        "url": row["icon_url"],
        "width": 100,
        "height": 100,
        "anchorY": 50
    }, axis=1)

    # layers
    layers = []

    if gdf_layer is not None and not gdf_layer.empty:
        extra_layer = pdk.Layer(
            "GeoJsonLayer",
            id="geojson_layer",
            data=gdf_layer,
            get_fill_color=[0, 0, 255, 50],
            get_line_color=[0, 0, 180],
            line_width_min_pixels=1,
            pickable=True
        )
        layers.append(extra_layer)

    icon_layer = pdk.Layer(
        "IconLayer",
        id="pie_chart_icons",
        data=icon_data,
        get_icon="icon",
        get_position=["lon", "lat"],
        get_size="radius",
        size_scale=0.002,
        pickable=True
    )
    layers.append(icon_layer)

    # unified tooltip
    tooltip = {
        "html": """
            <b>Total energy:</b> {total_html}<br/>{pie_html}
        """,
        "style": {
            "backgroundColor": "rgba(0,0,0,0.7)",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px",
            "borderRadius": "5px"
        }
    }

    view_state = pdk.ViewState(
        latitude=gdf["lat"].mean(),
        longitude=gdf["lon"].mean(),
        zoom=5
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=None
    )

    event = st.pydeck_chart(
        deck,
        selection_mode="single-object",
        on_select="rerun"
    )

    df = None
    if event.selection and "objects" in event.selection:
        cluster_objs = event.selection["objects"].get("pie_chart_icons", [])
        if cluster_objs:
            df = pd.DataFrame([cluster_objs[0]])
    return df


def _mapping_chart_per_ener_feed_sites(gdf, gdf_layer):
    import matplotlib.pyplot as plt
    import base64
    import io
    from PIL import Image, ImageDraw
    import pydeck as pdk
    import pandas as pd
    import streamlit as st

    color_choice = st.radio(
        "Site color select", ["Per cluster", "Per sector"], horizontal=True)

    # --- Preprocessing (your original preprocessing) ---
    type_ener_feed = list(color_map.keys())
    energy_cols = [col for col in gdf.columns if "[" in col]
    rename_map = {col: " ".join(col.split("_")[:-1]) for col in energy_cols}
    gdf = gdf.rename(columns=rename_map)

    energy_cols = [col for col in gdf.columns if any(
        col.startswith(feed.split("_")[0]) for feed in type_ener_feed)]

    if (gdf[energy_cols].sum(axis=1) == 0).all():
        return st.warning("Select feedstock(s) or energy carrier(s)")
    elec = energy_cols == ["electricity"]

    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y
    gdf["total_energy"] = gdf[energy_cols].sum(axis=1)
    gdf["radius"] = _get_radius(gdf)

    # --- Cluster colouring ---
    base_cmap = plt.get_cmap("tab20")
    max_colors = base_cmap.N
    unique_clusters = sorted(gdf["cluster"].unique())

    base_colors_rgb = [
        [int(255 * c) for c in base_cmap(i)[:3]]
        for i in range(max_colors)
    ]

    cluster_color_map = {
        cluster: [0, 0, 0] if cluster == -
        1 else base_colors_rgb[idx % max_colors]
        for idx, cluster in enumerate(unique_clusters)
    }

    # --- Sector colouring ---
    sector_cmap = {
        "Cement":      [102, 102, 102],   # grey
        "Chemical":    [31, 119, 180],    # blue
        "Fertilisers": [44, 160, 44],     # green
        "Glass":       [148, 103, 189],   # purple
        "Refineries":  [255, 127, 14],    # orange
        "Steel":       [127, 127, 127],   # dark grey
    }

    legend_site_html_horizontal = """
    <style>
    .legend-horizontal {
        font-family: sans-serif;
        font-size: 14px;
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 10px;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
    }
    .legend-color {
        width: 15px;
        height: 15px;
        margin-right: 6px;
        flex-shrink: 0;
    }
    </style>
    <div class="legend-horizontal">
        <div class="legend-item"><div class="legend-color" style="background: rgb(102, 102, 102);"></div>Cement</div>
        <div class="legend-item"><div class="legend-color" style="background: rgb(31, 119, 180);"></div>Chemical</div>
        <div class="legend-item"><div class="legend-color" style="background: rgb(44, 160, 44);"></div>Fertilisers</div>
        <div class="legend-item"><div class="legend-color" style="background: rgb(148, 103, 189);"></div>Glass</div>
        <div class="legend-item"><div class="legend-color" style="background: rgb(255, 127, 14);"></div>Refineries</div>
        <div class="legend-item"><div class="legend-color" style="background: rgb(127, 127, 127);"></div>Steel</div>
    </div>
    """

    if color_choice == "Per cluster":
        gdf["color"] = gdf["cluster"].map(cluster_color_map)
    elif color_choice == "Per sector":
        gdf["color"] = gdf["sector_name"].map(sector_cmap)

    def generate_base64_icon_from_color_pil(rgb, size=128):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([(0, 0), (size - 1, size - 1)], fill=tuple(rgb) + (255,))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    gdf["icon_base64"] = gdf["color"].apply(
        generate_base64_icon_from_color_pil)
    gdf["icon_data"] = gdf["icon_base64"].apply(lambda b64: {
        "url": f"data:image/png;base64,{b64}",
        "width": 128,
        "height": 128,
        "anchorY": 128,
    })

    icon_layer = pdk.Layer(
        "IconLayer",
        id="site_icons",
        data=gdf,
        get_icon="icon_data",
        get_position='[lon, lat]',
        get_size="radius",
        size_scale=0.0007,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=gdf["lat"].mean(),
        longitude=gdf["lon"].mean(),
        zoom=5
    )

    chart = pdk.Deck(
        layers=[icon_layer],
        initial_view_state=view_state,
        tooltip={"text": "Cluster: {cluster}\nSite Name: {site_name}"},
        map_style=None
    )

    event = st.pydeck_chart(
        chart,
        selection_mode="single-object",
        on_select="rerun"
    )

    if color_choice == "Per sector":
        st.markdown(legend_site_html_horizontal, unsafe_allow_html=True)

    selected = event.selection
    if selected and "objects" in selected:
        selected = selected["objects"].get("site_icons", [])

    df = None
    if selected:
        df = pd.DataFrame([selected[0]])  # Only first selected object
    return df


def _edit_clustering(choice):
    if choice == "DBSCAN":
        st.markdown(
            """<small><i>DBSCAN clustering is based on the density of points. It requires two parameters: the minimum number of sites and the distance between sites (in km).</i></small>""",
            unsafe_allow_html=True
        )
        min_samples = st.slider(
            "Minimum number of sites", 1, 10, step=1, value=5)
        radius = st.slider("Distance between sites (km)",
                           1, 100, step=1, value=10)
        return min_samples, radius, None

    if choice == "KMEANS":
        st.markdown(
            """<small><i>KMeans clustering requires the number of clusters to be defined. It clusters the sites based on their location only.</i></small>""",
            unsafe_allow_html=True
        )
        n_cluster = st.slider("Number of clusters", 1, 200, step=1, value=100)
        return None, None, n_cluster

    if choice == "KMEANS (weighted)":
        st.markdown(
            """<small><i>Weighted KMeans clustering requires the number of clusters to be defined. It clusters the sites based on their location, weighted by their total energy demand.</i></small>""",
            unsafe_allow_html=True
        )
        n_cluster = st.slider("Number of clusters", 1, 200, step=1, value=100)
        return None, None, n_cluster


def _run_clustering(choice, gdf, min_samples, radius, n_cluster):

    if choice == "DBSCAN":
        gdf_clustered = _cluster_gdf_dbscan(gdf, min_samples, radius)

    if choice == "KMEANS":
        gdf_clustered = _cluster_gdf_kmeans(gdf, n_cluster)

    if choice == "KMEANS (weighted)":
        gdf_clustered = _cluster_gdf_kmeans_weight(gdf, n_cluster)

    if (gdf_clustered["cluster"] != -1).any():
        return gdf_clustered
    else:
        return gdf


def _cluster_gdf_dbscan(gdf, min_samples, radius):
    """
    Perform DBSCAN clustering on a GeoDataFrame using lat/lon.

    Parameters:
    gdf (GeoDataFrame): Input GeoDataFrame with Point geometries.
    min_samples (int): Minimum number of points to form a cluster.
    eps (float): Maximum distance between points in the same cluster (in degrees).

    Returns:
    GeoDataFrame: GeoDataFrame with an added 'cluster' column.
    """
    # Ensure geometry is in lat/lon
    gdf.loc[:, "lat"] = gdf.geometry.y
    gdf.loc[:, "long"] = gdf.geometry.x
    coords_rad = np.radians(gdf[["lat", "long"]])

    db = DBSCAN(
        eps=radius / 6371.0,  # Convert radius from km to radians
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree",
    ).fit(coords_rad)
    gdf['cluster'] = db.labels_

    return gdf


# Summarise clusters values and aggreagatge in centroid per cluster (exculde -1)
def _summarise_clusters_by_centroid(gdf_clustered):
    """
    Summarise clustered GeoDataFrame by computing the centroid of each cluster
    and summing all type_ener_feed columns per cluster.

    Parameters:
    gdf_clustered (GeoDataFrame): Clustered GeoDataFrame with 'cluster' column.

    Returns:
    GeoDataFrame: GeoDataFrame with one row per cluster, centroid location, and
                  sum of all type_ener_feed columns.
    """
    if 'cluster' not in gdf_clustered.columns:
        raise ValueError("GeoDataFrame must contain a 'cluster' column.")
    columns = [col for col in gdf_clustered.columns if any(
        col.startswith(f"{feed} ") for feed in type_ener_feed) or col == "total_energy"]

    def _cluster_centroid(cluster_df):
        """Compute centroid of a cluster."""
        if cluster_df.empty:
            return None
        points = MultiPoint(cluster_df.geometry.tolist())
        return [points.centroid.y, points.centroid.x]

    if (gdf_clustered["cluster"] != -1).any():
        cluster_centers = (
            gdf_clustered[gdf_clustered["cluster"] != -
                          1].groupby("cluster").apply(_cluster_centroid)
        )
    else:
        return gdf_clustered
    centroids_df = pd.DataFrame(
        cluster_centers.tolist(),
        columns=["Latitude", "Longitude"],
        index=cluster_centers.index,
    )

    gdf_clustered_center = gpd.GeoDataFrame(
        centroids_df,
        geometry=gpd.points_from_xy(
            centroids_df.Longitude, centroids_df.Latitude),
        crs="EPSG:4326",
    )

    # Group by cluster and sum energy columns
    summary = gdf_clustered.groupby(
        "cluster")[columns].sum().reset_index()

    # Compute geometry as centroid of cluster
    gdf_summary = summary.merge(gdf_clustered_center, on="cluster")

    gdf_summary = gpd.GeoDataFrame(
        gdf_summary, geometry='geometry', crs="EPSG:4326")

    return gdf_summary


# KMeans clustering for GeoDataFrame
def _cluster_gdf_kmeans(gdf, n_clusters=5):
    """
    Perform KMeans clustering on a GeoDataFrame using lat/lon.

    Parameters:
    gdf (GeoDataFrame): Input GeoDataFrame with Point geometries.
    n_clusters (int): The number of clusters to form.

    Returns:
    GeoDataFrame: GeoDataFrame with an added 'cluster' column.
    """
    # Ensure geometry is in lat/lon
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    coords = gdf[['lat', 'lon']].to_numpy()
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coords_scaled)
    gdf['cluster'] = kmeans.labels_

    return gdf


def _cluster_gdf_kmeans_weight(gdf, n_clusters=5):
    """
    Perform KMeans clustering on a GeoDataFrame using lat/lon and weighted by total_energy.

    Parameters:
    gdf (GeoDataFrame): Input GeoDataFrame with Point geometries and 'total_energy' column.
    n_clusters (int): The number of clusters to form.

    Returns:
    GeoDataFrame: GeoDataFrame with an added 'cluster' column.
    """
    # Ensure geometry is in lat/lon
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    coords = gdf[['lat', 'lon']].to_numpy()
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)

    weights = gdf['total_energy'].to_numpy()
    weights = gdf['total_energy']
    weights_normalised = weights / weights.mean()  # or weights / weights.max()
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(coords_scaled, sample_weight=weights_normalised)

    gdf['cluster'] = kmeans.labels_
    return gdf


def _layer_RES_generation():

    # Load the shapefile
    shapefile_path = "data/NUTS/NUTS_RG_20M_2021_4326/NUTS_RG_20M_2021_4326.shp"
    gdf = gpd.read_file(shapefile_path)

    # Filter for NUTS level 3 regions
    gdf = gdf[gdf["LEVL_CODE"] == 3]

    # Load the Excel file, skipping the first 10 rows
    nuts3_area_df = pd.read_excel(
        "data/NUTS/NUTS3_area.xlsx", sheet_name=2, skiprows=9)

    # Drop empty columns and the third column (index 2)
    nuts3_area_df = nuts3_area_df.dropna(axis=1, how="all")
    nuts3_area_df = nuts3_area_df.drop(nuts3_area_df.columns[2], axis=1)

    # Rename relevant columns
    nuts3_area_df.rename(
        columns={"GEO (Labels)": "NUTS_NAME", "Unnamed: 1": "Area(km2)"}, inplace=True
    )

    # Merge the GeoDataFrame with the area DataFrame
    gdf_NUTS3_area = pd.merge(
        gdf[["NUTS_ID", "NUTS_NAME", "geometry"]],
        nuts3_area_df[["NUTS_NAME", "Area(km2)"]],
        on="NUTS_NAME",
    )
    RES_prod_2023_solar = pd.read_excel(
        "data/Energy_production/Production_Solar_wind.xlsx", sheet_name="solar", skiprows=0
    )
    RES_prod_2023_onshore = pd.read_excel(
        "data/Energy_production/Production_Solar_wind.xlsx",
        sheet_name="windonshore",
        skiprows=0,
    )
    # Map wind and solar data
    gdf_NUTS3_area["wind (MWh/km2)"] = gdf_NUTS3_area["NUTS_ID"].map(
        RES_prod_2023_onshore.set_index("NUTS")["Value"]
    )

    gdf_NUTS3_area["solar (MWh/km2)"] = gdf_NUTS3_area["NUTS_ID"].map(
        RES_prod_2023_solar.set_index("NUTS")["Value"]
    )
    gdf_NUTS3_area = gdf_NUTS3_area.dropna(subset=["wind (MWh/km2)"])
    gdf_NUTS3_area["solar (MWh)"] = (
        gdf_NUTS3_area["Area(km2)"] * gdf_NUTS3_area["solar (MWh/km2)"]
    )
    gdf_NUTS3_area["wind (MWh)"] = (
        gdf_NUTS3_area["Area(km2)"] * gdf_NUTS3_area["wind (MWh/km2)"]
    )

    return gdf_NUTS3_area
