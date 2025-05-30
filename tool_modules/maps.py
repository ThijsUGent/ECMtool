from tool_modules.cluster import *
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import pydeck as pdk
import numpy as np

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


def _get_utilization_rates(sectors):
    sector_utilization_defaut = {
        "Fertilisers": 63,
        "Steel": 80,
        "Cement": 100,
        # onethird (from aidres)% from 2022 to 2050 ,  # and 0.58 for assumed utilization rate
        "Refineries": 20,
        "Chemical": 75,  # cf cefec advanced competitiveness report page 41
        "Glass": 100,
    }
    sector_utilization = {}
    for sector in sectors:
        st.text("Ulization rate (%)")
        value = st.slider(f"{sector}", 0, 100,
                          value=sector_utilization_defaut[sector])
        sector_utilization[sector] = value
    return sector_utilization


def _get_gdf_prod_x_perton(df, pathway, sector_utilization):
    perton = st.session_state["Pathway name"][pathway]

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
    prod_rate_cap_utli_condi = gdf_production_site["utilization_rate"]/100 * \
        gdf_production_site["prod_cap"]

    condition = (gdf_production_site["prod_rate"].isna() &
                 gdf_production_site["prod_cap"].notna() &
                 gdf_production_site["utilization_rate"].notna())

    gdf_production_site["prod_rate"] = np.where(
        condition, prod_rate_cap_utli_condi, gdf_production_site["prod_rate"])

    # Multiply per ton with matching product
    sectors_products = list(perton.keys())
    df_pathway_weighted = []
    columns = type_ener_feed
    for sector_product in sectors_products:
        product = sector_product.split("_")[-1]
        sec = sector_product.split("_")[0]
        dfs_dict_path = st.session_state["Pathway name"][pathway]
        df_path = pd.concat(dfs_dict_path.values(), ignore_index=True)
        df_filtered = df_path[df_path["sector_name"] == sec]
        if not df_filtered.empty:
            def weighted_avg(df, value_cols, weight_col):
                return pd.Series({
                    col: np.average(df[col], weights=df[weight_col]) for col in value_cols
                })

            df_filtered_weight = df_filtered.groupby("product_name").apply(
                weighted_avg, value_cols=columns, weight_col="route_weight"
            ).reset_index()
            df_filtered_weight["sector_name"] = sec  # retain sector info
            df_pathway_weighted.append(df_filtered_weight)
    df_pathway_weighted = pd.concat(df_pathway_weighted, ignore_index=True)

    gdf_prod_x_perton = gdf_production_site.merge(
        df_pathway_weighted,
        how="left",
        left_on="wp1_model_product_name",
        right_on="product_name",
    )

    for column in columns:
        gdf_prod_x_perton[column] = gdf_prod_x_perton[column] * \
            gdf_prod_x_perton["prod_rate"]
        gdf_prod_x_perton.rename(
            columns={column: f"{column} ton"}, inplace=True)
    st.write(gdf_prod_x_perton)
    return gdf_prod_x_perton


def map_per_pathway():
    path = "data/production_site.csv"
    df = pd.read_csv(path)

    df = df[df["wp1_model_product_name"] != "not included in blue-print model"]

    if "Pathway name" not in st.session_state or not st.session_state["Pathway name"]:
        st.info("No selections stored yet.")
        return

    pathways_names = list(
        st.session_state["Pathway name"].keys())

    # intial number sector
    sectors_all_list = []
    if len(pathways_names) == 1:

        dict_path1 = st.session_state["Pathway name"][list(
            st.session_state["Pathway name"].keys())[0]]
        df_path1 = dict_path1[list(dict_path1.keys())[0]]
        sector_max_list = df_path1["sector_name"].unique().tolist()
        sectors_all_list = sector_max_list

    else:
        # Initialisation of all sectors
        sectors_all_list = ["Chemical", "Cement",
                            "Refineries", "Fertilisers", "Steel", "Glass"]

    sector_utilization = _get_utilization_rates(sectors_all_list)

    for pathway in pathways_names:
        st.write(pathway)
        gdf_prod_x_perton = _get_gdf_prod_x_perton(
            df, pathway, sector_utilization)

    # Convert to GeoDataFrame
    gdf = gdf_prod_x_perton

    # Extract latitude and longitude
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    # Create the PyDeck layer
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=gdf,
        id="sites",
        get_position='[lon, lat]',
        get_radius=1e4,
        pickable=True,
    )

    # Set the initial view state
    view_state = pdk.ViewState(
        latitude=gdf['lat'].mean(),
        longitude=gdf['lon'].mean(),
        zoom=3,
        pitch=0,
    )

    # Render the interactive map with tooltips and capture selected data
    chart = pdk.Deck(
        layers=[point_layer],
        initial_view_state=view_state,
        tooltip={"text": "Sector: {aidres_sector_name}"},
        map_style=None,
    )
    event = st.pydeck_chart(chart, on_select="rerun",
                            selection_mode="single-object")

    event.selection

    st.write(event.selection)


def map_per_utlisation_rate():
    st.write("Contruction")
