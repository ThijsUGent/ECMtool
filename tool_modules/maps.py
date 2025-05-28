from tool_modules.cluster import *
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import pydeck as pdk


def map_per_pathway():
    path = "data/production_site.csv"
    df = pd.read_csv(path)

    # Convert WKB hex to geometry
    df['geometry'] = df['geom'].apply(lambda x: wkb.loads(bytes.fromhex(x)))

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

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
                            selection_mode="multi-object")

    event.selection

    st.write(event.selection)


def map_per_utlisation_rate():
    st.write("Contruction")
