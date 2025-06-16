import streamlit as st
from tool_modules.cluster import *
import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import pandas as pd
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


def cluster_results():
    import streamlit as st

    # --- Check session state ---
    if "Cluster name" not in st.session_state or "Pathway name" not in st.session_state:
        st.warning("Please save at least one cluster and one pathway first.")
        return

    clusters_list = list(st.session_state["Cluster name"].keys())

    # --- Sector and energy/feedstock types ---
    sectors_all_list = ["Chemical", "Cement",
                        "Refineries", "Fertilisers", "Steel", "Glass"]

    type_ener_feed_gj = [item for item in type_ener_feed if "[gj/t]" in item]
    type_ener_feed_t = [item for item in type_ener_feed if "[t/t]" in item]

    type_ener_name = [" ".join(item.split("_")[:-1])
                      for item in type_ener_feed_gj]
    type_feed_name = [" ".join(item.split("_")[:-1])
                      for item in type_ener_feed_t]

    # --- Layout: fixed left column + dynamic right column(s) ---
    col_left, col_right = st.columns([1, 3])

    with col_left:
        unit = st.radio("Select unit", ["GJ", "t"], horizontal=True)

        selected_columns = []

        if unit == "GJ":
            with st.expander("Energy carriers"):
                select_all_energy = st.toggle(
                    "Select all", key="select_all_energy", value=True)
                default_ener = type_ener_name if select_all_energy else []

                selected_energy_labels = st.pills(
                    "Choose energy carriers",
                    type_ener_name,
                    default=default_ener,
                    label_visibility="visible",
                    selection_mode="multi",
                    key="energy_pills"
                )

                selected_columns = [
                    type_ener_feed_gj[type_ener_name.index(label)] for label in selected_energy_labels
                ]

        elif unit == "t":
            st.markdown("*Excluded electricity*")
            with st.expander("Feedstock"):
                select_all_feed = st.toggle(
                    "Select all", key="select_all_feed", value=True)
                default_feed = type_feed_name if select_all_feed else []

                selected_feed_labels = st.pills(
                    "Choose feedstock",
                    type_feed_name,
                    default=default_feed,
                    label_visibility="visible",
                    selection_mode="multi",
                    key="feed_pills"
                )

                selected_columns = [
                    type_ener_feed_t[type_feed_name.index(label)] for label in selected_feed_labels
                ]

        st.divider()
        st.markdown("**Edit utilisation rate per sector**  \n*Default: 100%*")
        with st.expander("Utilisation rate"):
            sector_utilization = _get_utilization_rates(sectors_all_list)

        st.divider()
        chart = st.radio("Select chart type", ["Sankey Diagram", "Treemap"])

        st.divider()
        # Select number of pathway to display
        pathway_names = list(st.session_state["Pathway name"].keys())
        max_display = min(len(pathway_names), 3)
        choices = list(range(1, max_display + 1))
        number_to_display = st.radio(
            "Number of paths to display", choices, horizontal=True, key=f'{choices}'
        )

    with col_right:
        if clusters_list:
            # Select one sector to display
            select_cluster = st.segmented_control(
                "Select a cluster", clusters_list, default=clusters_list[0])
        else:
            st.warning("No clusters available. Please save a cluster first.")
            return
        cols = st.columns(number_to_display)

        column_pathway_pairs = []
        for col, name in zip(cols, pathway_names[:number_to_display]):
            with col:
                selected_pathway = st.selectbox(
                    f"Choose a pathway", pathway_names, key=f"select_{name}", index=pathway_names.index(name)
                )
                column_pathway_pairs.append((col, selected_pathway))
        _display_cluster_pathway(column_pathway_pairs, select_cluster,
                                 selected_columns, unit, sector_utilization, chart)

        # Display the selected pathway


def _display_cluster_pathway(column_pathway_pairs, cluster, selected_columns, unit, sector_utilization, chart):

    for col, selected_pathway in column_pathway_pairs:
        with col:
            df_perton = _get_df_prod_x_perton_cluster(
                selected_pathway, sector_utilization, selected_columns, cluster)
            df_perton['unit'] = unit
            if chart == "Sankey Diagram":
                _sankey(df_perton, unit, cluster, selected_pathway, col)
            elif chart == "Treemap":
                _tree_map(df_perton, cluster, selected_pathway, col)


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


def _tree_map(df: pd.DataFrame, cluster: str, pathway: str, column: str):
    """
    Create a treemap visualization of energy use breakdown.

    Parameters:
        df (pd.DataFrame): DataFrame containing energy use data.
        cluster (str): Name of the cluster.
        pathway (str): Name of the pathway.
        column (str): Column name used in the Streamlit key.
    """
    if df is not None and not df.empty:
        # Identify energy-related columns
        energy_cols = [col for col in df.columns if any(
            col.startswith(feed) for feed in type_ener_feed)]

        # Clean column names (remove suffix like "_input", "_output")
        rename_map = {}
        renamed_cols = []

        for col in energy_cols:
            if "_" in col:
                new_name = " ".join(col.split("_")[:-1])
            else:
                new_name = col
            rename_map[col] = new_name
            renamed_cols.append(new_name)

        df = df.rename(columns=rename_map)

        columns_plot = [col for col in df.columns if col in renamed_cols]

        # Sum all rows for the selected columns
        total_values = df[columns_plot].sum()

        # Create a new DataFrame with one row — the sums
        df_sum = pd.DataFrame([total_values], columns=columns_plot)

        if not columns_plot:
            st.warning("No matching energy columns found.")
            return

        # Determine if electricity is the only energy source
        elec = (columns_plot == ["electricity"])

        # Extract the relevant row
        row = df_sum.iloc[0]

        # Prepare long-form DataFrame for plotting
        df_long = pd.DataFrame({
            "energy_source": columns_plot,
            "value": [row[col] for col in columns_plot],
            "color_value": [color_map.get(col, "#cccccc") for col in columns_plot],
        })

        # Clean up label and assign unit
        df_long["label"] = df_long["energy_source"].str.replace(
            r"\[.*?\]$", "", regex=True).str.replace("_", " ")
        df_long["unit"] = row.get("unit", "")

        # Convert and calculate total energy
        total_energy = df_long["value"].sum()
        unit = df_long["unit"].iloc[0]
        total_energy, unit_real = _energy_convert(total_energy, unit, elec)
        # Plot treemap
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
            title_text=(
                f"Energy Use {cluster} <br>"
                f"<sub>Pathway: {pathway}</sub> <br>"
                f"Total energy per annum: {total_energy} {unit_real}"
            )
        )

        st.plotly_chart(fig, key=f"{cluster}_{pathway}_{column}")


def _sankey(df, unit, cluster, pathway, column):
    """
    Create a Sankey diagram to visualize energy flow from carriers to sectors.
    Parameters:
        df (pd.DataFrame): DataFrame containing energy flow data.
        unit (str): Unit of energy, either 'GJ' or 't'.
    """
    if df is not None:
        energy_cols = [col for col in df.columns if any(
            col.startswith(feed) for feed in type_ener_feed)]

        # Option 1: remove last underscore segment and join with space
        carrier_labels = [" ".join(col.split("_")[:-1]) for col in energy_cols]

        sector_labels = df['sector'].unique().tolist()

        labels = carrier_labels + sector_labels
        label_indices = {label: i for i, label in enumerate(labels)}

        sources, targets, values = [], [], []

        for _, row in df.iterrows():
            sector = row['sector']
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
                text=f"Energy Use {cluster} <br><sub>Pathway : {pathway}<sub> <br> Total energy per annum: {total_energy} {unit_real}"
            ),
            font=dict(color="black", size=12),
            hoverlabel=dict(font=dict(color="black"))
        )

        st.plotly_chart(fig, use_container_width=True,
                        key=f"{cluster}_{pathway}_{column}")


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


def _get_df_prod_x_perton_cluster(pathway, sector_utilization, selected_columns, cluster):
    perton = st.session_state["Pathway name"][pathway]
    df = st.session_state["Cluster name"][cluster]
    for sector, utilization_rate in sector_utilization.items():

        # Matching sector & utlisation rate
        matching = df["sector"] == sector
        df.loc[matching,
               "utilization_rate"] = utilization_rate

    # Condition : prod_rate if prod_cap extist, but not prod_rate
    prod_rate_cap_utli_condi = df["utilization_rate"] / \
        100 * df["production capacity (kt)"]

    condition = (
        df["production capacity (kt)"].notna() &
        df["utilization_rate"].notna())

    df["production rate (kt)"] = np.where(
        condition, prod_rate_cap_utli_condi, df["production capacity (kt)"])

    # Multiply per ton with matching product
    sectors_products = list(perton.keys())
    df_pathway_weighted = pd.DataFrame()
    columns = selected_columns

    for sector_product in sectors_products:
        product = sector_product.split("_")[-1]
        sector = sector_product.split("_")[0]
        df_path = pd.concat(perton.values(), ignore_index=True)

        df_filtered = df_path[df_path["product_name"] == product]
        if not df_filtered.empty:
            def weighted_avg(df, value_cols, weight_col):
                return pd.Series({
                    col: np.average(df[col], weights=df[weight_col]) for col in value_cols
                })

            df_filtered_weight = df_filtered.groupby("product_name").apply(
                weighted_avg, value_cols=columns, weight_col="route_weight"
            ).reset_index()

            df_filtered_weight["sector"] = sector  # retain sector info

            # Correct way to append data to the final DataFrame
            df_pathway_weighted = pd.concat(
                [df_pathway_weighted, df_filtered_weight], ignore_index=True)

        df_prod_x_perton = df.merge(
            df_pathway_weighted,
            how="left",
            left_on="product",
            right_on="product_name",
        )
        df_prod_x_perton.rename(columns={"sector_y": "sector"}, inplace=True)
        df_prod_x_perton.drop(columns=["sector_x"], inplace=True)

    for column in columns:
        df_prod_x_perton[column] = df_prod_x_perton[column] * \
            df_prod_x_perton["production rate (kt)"] * 1000  # prod rate kt

    df_prod_x_perton['total_energy'] = df_prod_x_perton[columns].sum(
        axis=1)

    for column in columns:
        df_prod_x_perton.rename(
            columns={column: f"{column} ton"}, inplace=True)
    df_prod_x_perton = df_prod_x_perton[df_prod_x_perton["sector"].notnull()]

    return df_prod_x_perton
