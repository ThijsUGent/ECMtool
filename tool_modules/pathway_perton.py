import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import numpy as np


columns_perton_and_weight = [
    "configuration_name",
    "route_weight",
    "electricity_[mwh/t]",
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
    "plastic_mix_[t/t]",
    "totex_[eur/t]",
    "opex_var_[eur/t]",
    "co2_allowance_[eur/t]",
    "opex_cst_[eur/t]",
    "opex_[eur/t]",
    "capex_[eur/t]",
    "direct_emission_[tco2/t]",
    "total_emission_[tco2/t]",
    "direct_emission_reduction_[%]",
    "total_emission_reduction_[%]",
    "captured_co2_[tco2/t]",
]
columns_perton = [
    "configuration_name",
    "electricity_[mwh/t]",
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
    "plastic_mix_[t/t]",
    "totex_[eur/t]",
    "opex_var_[eur/t]",
    "co2_allowance_[eur/t]",
    "opex_cst_[eur/t]",
    "opex_[eur/t]",
    "capex_[eur/t]",
    "direct_emission_[tco2/t]",
    "total_emission_[tco2/t]",
    "direct_emission_reduction_[%]",
    "total_emission_reduction_[%]",
    "captured_co2_[tco2/t]",
]

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


def perton_page():
    st.title("Pathway specific energy/feedstock")

    if "Pathway name" not in st.session_state or not st.session_state["Pathway name"]:
        st.info("No selections stored yet.")
        return

    # intial number sector
    sectors_list = []
    if len(list(
            st.session_state["Pathway name"].keys())) == 1:

        dict_path1 = st.session_state["Pathway name"][list(
            st.session_state["Pathway name"].keys())[0]]
        df_path1 = dict_path1[list(dict_path1.keys())[0]]
        sector_max_list = df_path1["sector_name"].unique().tolist()
        sectors_list = sector_max_list

    else:
        # Initialisation of all sectors
        sectors_list = ["Chemical", "Cement",
                        "Refineries", "Fertilisers", "Steel", "Glass"]

    type_ener_feed_gj = [item for item in type_ener_feed if "[gj/t]" in item]
    type_ener_feed_t = [item for item in type_ener_feed if "[t/t]" in item]
    type_ener_feed_mwh = [item for item in type_ener_feed if "[mwh/t]" in item]

    # Labels only (without unit suffix)
    type_ener_name = ["_".join(item.split("_")[:-1])
                      for item in type_ener_feed_gj]
    type_feed_name = ["_".join(item.split("_")[:-1])
                      for item in type_ener_feed_t]

    pathway_names = list(st.session_state["Pathway name"].keys())

    col1, col2 = st.columns([1, 4])  # 3:1 ratio, left wide, right narrow

    with col1:
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

            selected_energy = [
                values_energy[options_energy.index(label)] for label in selected_energy_labels
            ]

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

            selected_feedstock = [
                values_feed[options_feed.index(label)] for label in selected_feed_labels
            ]

        type_of_perton = st.radio("Select which specific energy to show", [
            "Per route", "Weighted by sector"])

        if type_of_perton == "Per route":
            sector_selected = st.pills(
                "Select a sector", sectors_list, default=sectors_list[0])
            if not sector_selected:
                st.warning("Please select at least 1 sector.")
                selected_pathways = []
            selected_pathways = st.pills(
                "Select a pathway", pathway_names, selection_mode='multi', default=pathway_names[0])
            if len(selected_pathways) > 2:
                st.warning("Please select at most 2 pathways.")
                selected_pathways = selected_pathways[:2]
            if not selected_pathways:
                st.warning("Please select at least 1 pathways.")

        if type_of_perton == "Weighted by sector":
            selected_pathways = st.pills(
                "Select a pathway", pathway_names, selection_mode='multi', default=pathway_names[0])
            if len(selected_pathways) > 2:
                st.warning("Please select at most 2 pathways.")
                selected_pathways = selected_pathways[:2]
            if not selected_pathways:
                st.warning("Please select at least 1 pathways.")

    with col2:
        ener_or_feed = st.radio(
            "Select unit", ["Energy per ton (GJ/t)", "Tonne per tonne (t/t)"], horizontal=True
        )
        if type_of_perton == "Per route":
            st.subheader("Perton per route")
            _plot_per_route(selected_feedstock, selected_energy,
                            selected_pathways, sector_selected, ener_or_feed)
        if type_of_perton == "Weighted by sector":
            st.subheader("Perton by product")
            st.subheader("")
            _plot_per_pathway(selected_feedstock, selected_energy,
                              selected_pathways, sectors_list, ener_or_feed)


def _plot_per_pathway(selected_feedstock, selected_energy, selected_pathways, sector, ener_or_feed):
    if selected_pathways and sector:
        if ener_or_feed == "Energy per ton (GJ/t)":
            selected_ener_feed = selected_energy
        if ener_or_feed == "Tonne per tonne (t/t)":
            selected_ener_feed = selected_feedstock

        nbr_of_columns = len(selected_pathways)
        if nbr_of_columns > 1:
            cols = st.columns(nbr_of_columns)
            for i, pathway in enumerate(selected_pathways[:nbr_of_columns]):
                with cols[i]:
                    st.write(f"**{pathway}**")
                    _diplay_chart_per_pathway(
                        selected_ener_feed, pathway, sector, ener_or_feed)

        else:
            pathway = selected_pathways[0]
            _diplay_chart_per_pathway(
                selected_ener_feed, pathway, sector, ener_or_feed)


def _diplay_chart_per_pathway(
        selected_ener_feed, pathway, sector, ener_or_feed):

    columns = selected_ener_feed

    df_pathway_weighted = []

    for sec in sector:
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

   # st.write(df_pathway_weighted)

    # Melt the dataframe to long format for stacked bar chart
    df_melted = df_pathway_weighted.melt(
        id_vars=["product_name"],
        value_vars=columns,
        var_name="type",
        value_name="value"
    )

    df_combined = df_melted[df_melted["value"] != 0]

    # Filter color map (keys are still the full type, so legend colors may not match exactly)
    color_map_combined = {
        k: v for k, v in color_map.items() if k in df_combined["type"].unique()}

    # Plot combined
    fig_combined = px.bar(
        df_combined,
        x="value",
        y="product_name",
        color="type",
        color_discrete_map=color_map_combined,
        orientation="h",
        title=f"{ener_or_feed} for {pathway} per product",
        labels={"value": f"{ener_or_feed}",
                "product_name": "product_name", "type": "Type"}
    )

    st.plotly_chart(fig_combined, use_container_width=True,
                    key=f"plot_combined_{pathway}")


def _diplay_chart_per_route(selected_ener_feed, pathway, sector, ener_or_feed):

    columns = selected_ener_feed
    dfs_dict_path = st.session_state["Pathway name"][pathway]
    df_path = pd.concat(dfs_dict_path.values(), ignore_index=True)
    df_filtered = df_path[df_path["sector_name"] == sector]

    if df_filtered.empty:
        st.warning(f"No data available for sector: {sector}")
        return

    st.write(f"**{pathway} - {sector}**")

    product_names = df_filtered["product_name"].unique()

    for product_name in product_names:
        df_product = df_filtered[df_filtered["product_name"] == product_name]

        if df_product.empty:
            continue

        # Melt the dataframe to long format for stacked bar chart
        df_melted = df_product.melt(
            id_vars=["configuration_name"],
            value_vars=columns,
            var_name="type",
            value_name="value"
        )

        df_combined = df_melted

        df_combined = df_combined[df_combined["value"] != 0]

        # Filter color map (keys are still the full type, so legend colors may not match exactly)
        color_map_combined = {
            k: v for k, v in color_map.items() if k in df_combined["type"].unique()}

        # Plot combined
        fig_combined = px.bar(
            df_combined,
            x="value",
            y="configuration_name",
            color="type",
            color_discrete_map=color_map_combined,
            orientation="h",
            title=f"{ener_or_feed} for {product_name} - {pathway} ",
            labels={"value": f"{ener_or_feed})",
                    "configuration_name": "Configuration", "type": "Type"}
        )

        st.plotly_chart(fig_combined, use_container_width=True,
                        key=f"plot_combined_{pathway}-{sector}-{product_name}")


def _plot_per_route(selected_feedstock, selected_energy, selected_pathways, sector, ener_or_feed):
    if selected_pathways and sector:
        if selected_pathways:
            if ener_or_feed == "Energy per ton (GJ/t)":
                selected_ener_feed = selected_energy
            if ener_or_feed == "Tonne per tonne (t/t)":
                selected_ener_feed = selected_feedstock

        nbr_of_columns = len(selected_pathways)
        if nbr_of_columns > 1:
            cols = st.columns(nbr_of_columns)
            for i, pathway in enumerate(selected_pathways[:nbr_of_columns]):
                with cols[i]:
                    st.write(f"**{pathway}**")
                    _diplay_chart_per_route(
                        selected_ener_feed, pathway, sector, ener_or_feed)

        else:
            pathway = selected_pathways[0]
            _diplay_chart_per_route(
                selected_ener_feed, pathway, sector, ener_or_feed)
