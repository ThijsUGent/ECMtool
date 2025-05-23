import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from sklearn.cluster import DBSCAN
import numpy as np
import folium
from geopy.distance import geodesic


def site_to_gdf(path):
    """
    Convert site data from a CSV or Excel file into a GeoDataFrame.
    Uses Latitude/Longitude if available, otherwise converts WKT geometry.

    Parameters:
        path (str): Path to the CSV or Excel file containing site data.

    Returns:
        gdf_sites (GeoDataFrame): GeoDataFrame of sites with geometry.
    """
    if path.endswith(".csv"):
        df_sites = pd.read_csv(path)
    elif path.endswith(".xlsx"):
        df_sites = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")

    if "Latitude" in df_sites.columns and "Longitude" in df_sites.columns:
        # Drop rows with missing latitude or longitude
        df_sites.dropna(subset=["Latitude", "Longitude"], inplace=True)

        # Convert Latitude/Longitude to geometry
        gdf_sites = gpd.GeoDataFrame(
            df_sites,
            geometry=gpd.points_from_xy(df_sites.Longitude, df_sites.Latitude),
            crs="EPSG:4326",
        )

    elif "site_lat" in df_sites.columns and "site_long" in df_sites.columns:
        # Drop rows with missing latitude or longitude
        df_sites.dropna(subset=["site_lat", "site_long"], inplace=True)

        # Convert Latitude/Longitude to geometry
        gdf_sites = gpd.GeoDataFrame(
            df_sites,
            geometry=gpd.points_from_xy(df_sites.site_long, df_sites.site_lat),
            crs="EPSG:4326",
        )
    elif "geometry" in df_sites.columns:
        # Drop rows with missing geometrys
        df_sites.dropna(subset=["geometry"], inplace=True)

        # Convert WKT to geometry
        gdf_sites = gpd.GeoDataFrame(
            df_sites,
            geometry=gpd.GeoSeries.from_wkt(df_sites["geometry"]),
            crs="EPSG:4326",
        )

    elif "geom" in df_sites.columns:
        # Drop rows with missing geometrys
        df_sites.dropna(subset=["geom"], inplace=True)

        # Convert WKT to geometry
        gdf_sites = gpd.GeoDataFrame(
            df_sites,
            geometry=gpd.GeoSeries.from_wkt(df_sites["geom"]),
            crs="EPSG:4326",
        )
    else:
        raise ValueError(
            "The file must contain either 'Latitude' and 'Longitude' columns or a 'geometry' column."
        )

    return gdf_sites


def site_to_cluster(gdf_sites, min_samples, radius):
    """
    Perform DBSCAN clustering on geographic sites and compute cluster centroids.
    Handles both Latitude/Longitude and WKT geometry.

    Parameters:
        gdf_sites (GeoDataFrame): GeoDataFrame containing site locations.
        min_samples (int): Minimum points to form a cluster.
        radius (float): Maximum distance (km) to be considered in the same cluster.

    Returns:
        tuple:
            - gdf_sites (GeoDataFrame): Sites with assigned cluster labels.
            - gdf_cluster (GeoDataFrame): Cluster centroids with aggregated emissions.
    """
    gdf_sites = gdf_sites.copy()  # ensure we're not modifying a view

    if "Latitude" in gdf_sites.columns and "Longitude" in gdf_sites.columns:
        coords_rad = np.radians(gdf_sites[["Latitude", "Longitude"]])
    else:
        gdf_sites.loc[:, "Latitude"] = gdf_sites.geometry.y
        gdf_sites.loc[:, "Longitude"] = gdf_sites.geometry.x
        coords_rad = np.radians(gdf_sites[["Latitude", "Longitude"]])

    db = DBSCAN(
        eps=radius / 6371.0,  # Convert radius from km to radians
        min_samples=min_samples,
        metric="haversine",
        algorithm="ball_tree",
    ).fit(coords_rad)
    gdf_sites.loc[:, "cluster"] = db.labels_

    def cluster_centroid(cluster_df):
        """Compute centroid of a cluster."""
        if cluster_df.empty:
            return None
        points = MultiPoint(cluster_df.geometry.tolist())
        return [points.centroid.y, points.centroid.x]

    cluster_centers = (
        gdf_sites[gdf_sites["cluster"] != -1].groupby("cluster").apply(cluster_centroid)
    )
    centroids_df = pd.DataFrame(
        cluster_centers.tolist(),
        columns=["Latitude", "Longitude"],
        index=cluster_centers.index,
    )

    gdf_cluster = gpd.GeoDataFrame(
        centroids_df,
        geometry=gpd.points_from_xy(centroids_df.Longitude, centroids_df.Latitude),
        crs="EPSG:4326",
    )

    gdf_cluster.loc[:, "Number of sites"] = gdf_cluster.index.map(
        lambda index: (gdf_sites["cluster"] == index).sum()
    )

    if "Emissions 2022 (Mt)" in gdf_sites.columns:
        gdf_cluster.loc[:, "Total Emissions 2022 (Mt)"] = gdf_cluster.index.map(
            lambda index: gdf_sites.loc[
                gdf_sites["cluster"] == index, "Emissions 2022 (Mt)"
            ].sum()
        )
    if "Emissions 2023 (Mt)" in gdf_sites.columns:
        gdf_cluster.loc[:, "Total Emissions 2023 (Mt)"] = gdf_cluster.index.map(
            lambda index: gdf_sites.loc[
                gdf_sites["cluster"] == index, "Emissions 2023 (Mt)"
            ].sum()
        )
    if (
        "Emissions 2022 (Mt)" in gdf_sites.columns
        and "Emissions 2023 (Mt)" in gdf_sites.columns
    ):
        gdf_cluster.loc[:, "Average Emissions (Mt)"] = gdf_cluster[
            ["Total Emissions 2022 (Mt)", "Total Emissions 2023 (Mt)"]
        ].mean(axis=1)

    if "elec_mwh" in gdf_sites.columns:
        gdf_cluster.loc[:, "elec_mwh (total)"] = gdf_cluster.index.map(
            lambda index: gdf_sites.loc[gdf_sites["cluster"] == index, "elec_mwh"].sum()
        )
    if "Elec (MWh)" in gdf_sites.columns:
        gdf_cluster.loc[:, "elec TWh (total)"] = gdf_cluster.index.map(
            lambda index: gdf_sites.loc[
                gdf_sites["cluster"] == index, "Elec (MWh)"
            ].sum()
            * 1e-6
        )

    def average_distance_to_centroid(cluster_df, centroid):
        """Calculate the average distance from sites to the cluster centroid."""
        distances = cluster_df.geometry.apply(
            lambda point: geodesic(
                (point.y, point.x), (centroid.iloc[0], centroid.iloc[1])
            ).kilometers
        )
        return distances.mean()

    avg_distances = []
    for cluster_id, centroid in centroids_df.iterrows():
        cluster_sites = gdf_sites[gdf_sites["cluster"] == cluster_id]
        avg_distance = average_distance_to_centroid(cluster_sites, centroid)
        avg_distances.append(avg_distance)

    gdf_cluster.loc[:, "Average Distance centroid/site(km)"] = avg_distances

    if "NACE name" in gdf_sites.columns:
        gdf_cluster.loc[:, "Number of sectors"] = gdf_sites.groupby("cluster")[
            "NACE name"
        ].nunique()

    gdf_sites.drop(columns=["Latitude", "Longitude"], inplace=True, errors="ignore")
    gdf_cluster.drop(columns=["Latitude", "Longitude"], inplace=True, errors="ignore")

    return gdf_sites, gdf_cluster


def get_cluster_data(cluster_index_list, gdf_sites, gdf_cluster):
    """
    Select multiple clusters and their sites, returning a visualization map.

    Parameters:
        cluster_index_list (list of int): List of cluster indices.
        gdf_sites (GeoDataFrame): Site data with cluster labels.
        gdf_cluster (GeoDataFrame): Cluster centroid data.

    Returns:
        dict: Dictionary containing selected clusters, sites, and an interactive map.
    """
    if not isinstance(cluster_index_list, list):
        raise TypeError("cluster_index_list must be a list of integers.")

    selected_clusters = gdf_cluster.loc[cluster_index_list]
    selected_sites = gdf_sites[gdf_sites["cluster"].isin(cluster_index_list)]

    m = folium.Map(zoom_start=6)
    for _, row in selected_clusters.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"Cluster {row.name}: {row['Number of sites']} sites, Avg Emissions: {row['Average Emissions (Mt)']} Mt",
            icon=folium.Icon(color="red"),
        ).add_to(m)
    for _, row in selected_sites.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=2,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=row.get("name", "Unknown Site"),
        ).add_to(m)

    return {
        "gdf_cluster_selected": selected_clusters,
        "gdf_sites_cluster": selected_sites,
        "map": m,
    }
