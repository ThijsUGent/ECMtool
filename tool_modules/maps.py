import base64
from io import BytesIO
from tool_modules.cluster import *
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import pydeck as pdk
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import pandas as pd
from io import BytesIO
import base64
import os
import math
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

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
        st.text('________')
        st.text('Edit utilisation rate per sector')
        st.markdown(""" *Default value 100 %* """)
        with st.expander("Utilisation rate"):
            sector_utilization = _get_utilization_rates(sectors_all_list)
        dict_gdf = {}
        for pathway in pathways_names:
            gdf_prod_x_perton = _get_gdf_prod_x_perton(
                df, pathway, sector_utilization, selected_columns)
            # Convert to GeoDataFrame
            dict_gdf[pathway] = gdf_prod_x_perton
        st.text('________')
        choice = st.radio("Cluster method", ["DBSCAN", "KMEANS"])
        min_samples, radius, n_cluster = _edit_clustering(choice)
        dict_gdf_clustered = {}
        for pathway in pathways_names:
            gdf_clustered = _run_clustering(
                choice, dict_gdf[pathway], min_samples, radius, n_cluster)
            dict_gdf_clustered[pathway] = gdf_clustered
        st.text('________')
        map_choice = st.radio("Mapping view", ["cluster centroid", "site"])
    with col2:

        pathway = st.radio("Select a pathway", pathways_names, horizontal=True)

        sectors_included = dict_gdf_clustered[pathway]["aidres_sector_name"].unique(
        ).tolist()
        sector_seleted = st.segmented_control("Sector(s) included within the pathway:",
                                              sectors_included, selection_mode="multi", default=sectors_included)
        st.markdown("""*Click on a cluster to see details*""")

        # Selected sectors
        dict_gdf_clustered[pathway].copy()
        dict_gdf_clustered[pathway] = dict_gdf_clustered[pathway][dict_gdf_clustered[pathway]
                                                                  ["aidres_sector_name"].isin(sector_seleted)]

        if map_choice == "cluster centroid":
            gdf_clustered_centroid = _summarise_clusters_by_centroid(
                dict_gdf_clustered[pathway])
            selected = _mapping_chart_per_ener_feed_cluster(
                gdf_clustered_centroid, color_map, unit)
        if map_choice == "site":
            selected = _mapping_chart_per_ener_feed_sites(
                dict_gdf_clustered[pathway])
        df_selected = _clean_seleted_to_df(selected)

        if df_selected is not None:
            chart = st.radio("Select an option ", ["Treemap",
                             "Sankey Diagram"])
            df_filtered_cluster = _site_within_cluster(
                df_selected, pathway, dict_gdf_clustered)
            if chart == "Treemap":
                _tree_map(df_selected)
            elif chart == "Sankey Diagram":
                _sankey(df_filtered_cluster, unit)
            with st.expander("Show sites within the cluster"):
                if df_filtered_cluster is not None:
                    df_filtered_cluster_show = df_filtered_cluster[[
                        "site_name", "aidres_sector_name", "product_name", "prod_cap", "prod_rate", "utilization_rate", "total_energy"]]
                    st.write(df_filtered_cluster_show)


def _clean_seleted_to_df(selected):
    df = None
    if selected and "objects" in selected:
        cluster_objs = selected["objects"].get("cluster", [])
        if cluster_objs:
            selected_obj = cluster_objs[0]  # First selected item

            # Optionally convert to DataFrame
            import pandas as pd
            df = pd.DataFrame([selected_obj])
    return df


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
    if unit != "GJ":
        return round(value), unit

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
        )

        fig.update_layout(
            title_text=f"Energy Use Breakdown<br><sub>Total energy per annum: {total_energy} {unit_real}</sub>")
        fig.update_traces(marker_colors=df_long["color_value"].tolist())

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
    prod_rate_cap_utli_condi = gdf_production_site["utilization_rate"] / \
        100 * gdf_production_site["prod_cap"]

    condition = (gdf_production_site["prod_rate"].isna() &
                 gdf_production_site["prod_cap"].notna() &
                 gdf_production_site["utilization_rate"].notna())

    gdf_production_site["prod_rate"] = np.where(
        condition, prod_rate_cap_utli_condi, gdf_production_site["prod_rate"])

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


def _mapping_chart_per_ener_feed_cluster(gdf, color_map, unit):
    # --- Data Preparation ---
    type_ener_feed = list(color_map.keys())
    energy_cols = [col for col in gdf.columns if "[" in col]
    rename_map = {col: " ".join(col.split("_")[:-1]) for col in energy_cols}
    gdf = gdf.rename(columns=rename_map)

    energy_cols = [col for col in gdf.columns if any(
        col.startswith(feed.split("_")[0]) for feed in type_ener_feed)]

    if (gdf[energy_cols].sum(axis=1) == 0).all():
        return st.error("Select feedstock(s) or energy carrier(s)")
    if energy_cols == ["electricity"]:
        elec = True
    else:
        elec = False

    gdf["total_energy"] = gdf[energy_cols].sum(axis=1)
    gdf = gdf[gdf["total_energy"] > 0].copy()
    gdf["unit"] = unit
    gdf["total_energy_rounded"] = gdf["total_energy"].round().astype(int)
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y
    gdf["radius"] = _get_radius(gdf)

    # --- Pie Chart SVG as Icon ---
    def generate_pie_svg_base64(row):
        values = row[energy_cols]
        segments = [(col, val)
                    for col, val in zip(energy_cols, values) if val > 0]
        if not segments:
            return ""

        total = sum(val for _, val in segments)
        start_angle = 0
        cx, cy, r = 50, 50, 50
        paths = []

        if len(segments) == 1:
            # Draw full circle
            col, _ = segments[0]
            colour = color_map.get(col, "#000000")
            paths.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{colour}" />')
        else:
            total = sum(val for _, val in segments)
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

    def polar_to_cartesian(cx, cy, r, angle_deg):
        angle_rad = math.radians(angle_deg)
        return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

    gdf["icon_url"] = gdf.apply(generate_pie_svg_base64, axis=1)

    # --- Icon Layer ---
    icon_data = gdf[["lon", "lat", "icon_url", "total_energy",
                     "total_energy_rounded", "unit", "radius"]].copy()

    icon_data["icon"] = icon_data.apply(lambda row: {
        "url": row["icon_url"],
        "width": 100,
        "height": 100,
        "anchorY": 50
    }, axis=1)

    icon_layer = pdk.Layer(
        "IconLayer",
        id='pie_chart',
        data=icon_data,
        get_icon="icon",
        get_size="radius",
        size_scale=0.002,
        get_position=["lon", "lat"],
        pickable=False
    )

    # --- Pie Tooltip HTML ---
    def generate_pie_legend(row):
        values = row[energy_cols]
        segments = [(col, val)
                    for col, val in zip(energy_cols, values) if val > 0]
        if not segments:
            return ""

        total = sum(val for _, val in segments)
        gradient_parts = []
        legend_rows = []
        start = 0

        for col, val in segments:
            pct = val / total * 100
            end = start + pct
            colour = color_map.get(col, "#000000")
            gradient_parts.append(f"{colour} {start:.1f}% {end:.1f}%")
            legend_rows.append(f"""
                <div style="display: flex; align-items: center; margin-bottom: 2px;">
                    <div style="width: 12px; height: 12px; background-color: {colour}; margin-right: 6px; border-radius: 2px;"></div>
                    <span style="font-size: 11px; color: white;">{col}</span>
                </div>
            """)
            start = end

        legend_html = "".join(legend_rows)
        return f"""
        <div style="display: flex; flex-direction: row; gap: 10px; align-items: flex-start;">
            <div style="width: 80px; height: 80px; border-radius: 50%; flex-shrink: 0;"></div>
            <div style="display: flex; flex-direction: column;">{legend_html}</div>
        </div>
        """

    gdf["pie_html"] = gdf.apply(generate_pie_legend, axis=1)

    def build_total_html(row):
        total_formatted, unit_formatted = _energy_convert(
            row['total_energy_rounded'], row['unit'], elec)
        return f"{total_formatted} {unit_formatted}"

    # Apply the function to your GeoDataFrame
    gdf['total_html'] = gdf.apply(build_total_html, axis=1)

    # --- Point Layer (Selectable) ---
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=gdf,
        id="cluster",
        get_position="[lon, lat]",
        get_radius=5000,
        pickable=True,
        auto_highlight=False,
        opacity=0.001
    )

    # --- Deck Setup ---
    view_state = pdk.ViewState(
        latitude=gdf["lat"].mean(),
        longitude=gdf["lon"].mean(),
        zoom=5,
        pitch=0.1
    )

    # First, define a function that will return the formatted HTML string per row

    tooltip = {
        "html": "<b>Total energy:</b> {total_html} <b> {pie_html}",
        "style": {
            "backgroundColor": "rgba(0,0,0,0.7)",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px",
            "borderRadius": "5px"
        }
    }

    deck = pdk.Deck(
        layers=[icon_layer, point_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=None
    )

    event = st.pydeck_chart(
        deck, selection_mode="single-object",  on_select="rerun",)
    return event.selection


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
        get_radius=0.4e4,
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
        tooltip={"text": "Cluster: {cluster} \n Site Name: {site_name}"},
        map_style=None,
    )
    event = st.pydeck_chart(chart, on_select="rerun",
                            selection_mode="single-object")

    selected = event.selection

    return selected


def _edit_clustering(choice):
    if choice == "DBSCAN":
        min_samples = st.slider("Min samples", 1, 10, step=1, value=5)
        radius = st.slider("Distance", 1, 100, step=1, value=10)
        return min_samples, radius, None

    if choice == "KMEANS":
        n_cluster = st.slider("Number of clusters", 1, 200, step=1, value=100)
        return None, None, n_cluster


def _run_clustering(choice, gdf, min_samples, radius, n_cluster):

    if choice == "DBSCAN":
        gdf_clustered = _cluster_gdf_dbscan(gdf, min_samples, radius)

    if choice == "KMEANS":
        gdf_clustered = _cluster_gdf_kmeans(gdf, n_cluster)

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
