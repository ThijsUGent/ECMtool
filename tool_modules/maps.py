from tool_modules.cluster import *
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import pydeck as pdk
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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

color_map = {
    "electricity_[mwh/t]": "#fff7bc",  # yellow pastel
    "electricity_[gj/t]": "#ffeda0",   # yellow pastel
    "alternative_fuel_mixture_[gj/t]": "#fdd49e",  # light orange
    "alternative_fuel_mixture_[t/t]": "#d7301f",   # dark red
    "biomass_[gj/t]": "#c7e9c0",       # light green
    "biomass_[t/t]": "#238b45",        # dark green
    "biomass_waste_[gj/t]": "#a1d99b",  # green pastel
    "biomass_waste_[t/t]": "#006d2c",  # deep green
    "coal_[gj/t]": "#cccccc",          # light grey
    "coal_[t/t]": "#000000",           # black
    "coke_[gj/t]": "#bdbdbd",          # grey
    "coke_[t/t]": "#636363",           # dark grey
    "crude_oil_[gj/t]": "#fdae6b",     # orange pastel
    "crude_oil_[t/t]": "#e6550d",      # burnt orange
    "hydrogen_[gj/t]": "#b7d7f4",      # light blue
    "hydrogen_[t/t]": "#3484d4",       # deep blue
    "methanol_[gj/t]": "#fdd0a2",      # soft orange
    "methanol_[t/t]": "#d94801",       # dark orange
    "ammonia_[gj/t]": "#d9f0a3",       # lime pastel
    "ammonia_[t/t]": "#78c679",        # dark lime
    "naphtha_[gj/t]": "#fcbba1",       # peach
    "naphtha_[t/t]": "#cb181d",        # dark red
    "natural_gas_[gj/t]": "#89a0d0",   # light blue
    "natural_gas_[t/t]": "#074c88",    # medium blue
    "plastic_mix_[gj/t]": "#e5e5e5",   # very light grey
    "plastic_mix_[t/t]": "#737373"     # medium grey
}


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
    type_ener_name = ["_".join(item.split("_")[:-1])
                      for item in type_ener_feed_gj]
    type_feed_name = ["_".join(item.split("_")[:-1])
                      for item in type_ener_feed_t]

    col1, col2 = st.columns([1, 4])  # 3:1 ratio, left wide, right narrow

    with col1:
        ener_or_feed = st.radio(
            "Select unit", ["Energy per ton (GJ/t)", "Tonne per tonne (t/t)"], horizontal=True
        )
        if ener_or_feed == "Energy per ton (GJ/t)":
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

        elif ener_or_feed == "Tonne per tonne (t/t)":
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

        st.text('Edit utilisation rate per sector')

        with st.expander("Utilisation rate"):
            sector_utilization = _get_utilization_rates(sectors_all_list)
        dict_gdf = {}
        for pathway in pathways_names:
            gdf_prod_x_perton = _get_gdf_prod_x_perton(
                df, pathway, sector_utilization, selected_columns)
            # Convert to GeoDataFrame
            dict_gdf[pathway] = gdf_prod_x_perton

        choice = st.radio("Cluster method", ["DBSCAN", "KMEANS"])
        min_samples, radius, n_cluster = _edit_clustering(choice)
        dict_gdf_clustered = {}
        for pathway in pathways_names:
            gdf_clustered = _run_clustering(
                choice, dict_gdf[pathway], min_samples, radius, n_cluster)
            dict_gdf_clustered[pathway] = gdf_clustered

        map_choice = st.radio("Mapping view", ["cluster", "site"])
    with col2:
        pathway = st.radio("Select a pathway", pathways_names, horizontal=True)
        if map_choice == "cluster":
            gdf_clustered_centroid = _summarise_clusters_by_centroid(
                dict_gdf_clustered[pathway])
            selected = _mapping_chart_per_ener_feed_cluster(
                gdf_clustered_centroid)
        if map_choice == "site":
            selected = _mapping_chart_per_ener_feed_sites(
                dict_gdf_clustered[pathway])

        st.write(selected)


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


def _get_gdf_prod_x_perton(df, pathway, sector_utilization, selected_columns):
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
    columns = selected_columns
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
    return gdf_prod_x_perton


def _mapping_chart_per_ener_feed_cluster(gdf):
    def _get_radius(gdf):
        gdf.sum

    # Extract latitude and longitude
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    unique_clusters = gdf["cluster"].unique()
    cmap = plt.get_cmap("tab20", len(unique_clusters))
    cluster_color_map = {}
    for i, cluster in enumerate(unique_clusters):
        if cluster == -1:
            cluster_color_map[cluster] = [0, 0, 0]  # black
        else:
            rgb = [int(255 * c) for c in cmap(i % cmap.N)[:3]]
            cluster_color_map[cluster] = rgb

    gdf["color"] = gdf["cluster"].map(cluster_color_map)
    colormap = "color"
    get_radius = _get_radius(gdf)
    # Create the PyDeck layer
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=gdf,
        id="sites",
        get_position='[lon, lat]',
        get_radius=1e4,
        pickable=True,
        get_fill_color=colormap
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

    selected = event.selection

    return selected


def _mapping_chart_per_ener_feed_sites(gdf):
    # Extract latitude and longitude
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    unique_clusters = gdf["cluster"].unique()
    cmap = plt.get_cmap("tab20", len(unique_clusters))
    cluster_color_map = {}
    for i, cluster in enumerate(unique_clusters):
        if cluster == -1:
            cluster_color_map[cluster] = [0, 0, 0]  # black
        else:
            rgb = [int(255 * c) for c in cmap(i % cmap.N)[:3]]
            cluster_color_map[cluster] = rgb

    gdf["color"] = gdf["cluster"].map(cluster_color_map)
    colormap = "color"

    # Create the PyDeck layer
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=gdf,
        id="sites",
        get_position='[lon, lat]',
        get_radius=1e4,
        pickable=True,
        get_fill_color=colormap,
        pitch=0,
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

    selected = event.selection

    return selected


def _edit_clustering(choice):
    if choice == "DBSCAN":
        min_samples = st.slider("Min samples", 1, 10, value=5)
        radius = st.slider("Distance", 1, 100, step=10, value=10)
        return min_samples, radius, None

    if choice == "KMEANS":
        n_cluster = st.slider("Nbr of cluster", 10, 200, step=10, value=100)
        return None, None, n_cluster


def _run_clustering(choice, gdf, min_samples, radius, n_cluster):
    if choice == "DBSCAN":
        gdf_clustered = _cluster_gdf_dbscan(gdf, min_samples, radius)

    if choice == "KMEANS":
        gdf_clustered = _cluster_gdf_kmeans(gdf, n_cluster)

    return gdf_clustered


def map_per_utlisation_rate():
    st.write("Contruction")


# DBSCAN clustering for GeoDataFrame
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
        col.startswith(f"{feed} ") for feed in type_ener_feed)]

    def _cluster_centroid(cluster_df):
        """Compute centroid of a cluster."""
        if cluster_df.empty:
            return None
        points = MultiPoint(cluster_df.geometry.tolist())
        return [points.centroid.y, points.centroid.x]

    cluster_centers = (
        gdf_clustered[gdf_clustered["cluster"] != -
                      1].groupby("cluster").apply(_cluster_centroid)
    )
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
