import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def view_page():
    st.title("Product selections")
    if "Pathway name" not in st.session_state or not st.session_state["Pathway name"]:
        st.info("No selections stored yet.")
        return
    # intial number sector
    sectors_all_list = []
    if len(list(
            st.session_state["Pathway name"].keys())) == 1:

        dict_path1 = st.session_state["Pathway name"][list(
            st.session_state["Pathway name"].keys())[0]]
        df_path1 = dict_path1[list(dict_path1.keys())[0]]
        sector_max_list = df_path1["sector_name"].unique().tolist()
        sectors_all_list = sector_max_list

    else:
        # Initialisation of all sectors
        sectors_all_list = ["Chemical", "Cement",
                            "Refineries", "Fertilisers", "Steel", "Glass"]

    # Select number of pathway to display
    pathway_names = list(st.session_state["Pathway name"].keys())
    max_display = min(len(pathway_names), 3)
    choices = list(range(1, max_display + 1))
    number_to_display = st.radio(
        "Number of paths to display", choices, horizontal=True, key=f'{choices}'
    )

    # Select one sector to display
    selected_sector = st.segmented_control(
        "Select a sector", sectors_all_list, default=sectors_all_list[0])

    cols = st.columns(number_to_display)

    column_pathway_pairs = []
    for col, name in zip(cols, pathway_names[:number_to_display]):
        with col:
            selected_pathway = st.selectbox(
                f"Choose a pathway", pathway_names, key=f"select_{name}", index=pathway_names.index(name)
            )
            column_pathway_pairs.append((col, selected_pathway))

    _display_pathway(column_pathway_pairs, selected_sector)


def _plot_configurations(df, selected_pathway, product, sector, col):

    if not df.empty:

        st.subheader
        st.subheader(f"{product}")

        # Sort configurations to maintain consistent order
        df_sorted = df.sort_values(by=["configuration_name", "fuel"])

        # Create a colour map for fuel types
        fuel_types = df_sorted["fuel"].unique()
        colours = px.colors.qualitative.Plotly
        colour_map = {fuel: colours[i % len(colours)]
                      for i, fuel in enumerate(fuel_types)}

        # Add a colour column for Plotly
        df_sorted["colour"] = df_sorted["fuel"].map(colour_map)

        # Create a bar per fuel with a single y-value (product) and stack them
        fig = px.bar(
            df_sorted,
            x="route_weight",
            y=[product]*len(df_sorted),
            color="fuel",
            color_discrete_map=colour_map,
            orientation="h",
            hover_data=["route_weight", "configuration_name"]
        )

        # add a horizontal line manually
        config_breaks = df_sorted["route_weight"].cumsum().values[:-1]
        for x_pos in config_breaks:
            fig.add_vline(x=x_pos, line_dash="dash", line_color="grey")

        fig.update_layout(
            barmode='stack',
            xaxis_title="Weight",
            yaxis_title="",
            showlegend=True,
            height=250,
            title=f"Configuration Weights for {selected_pathway} - {product}",
            margin=dict(t=30, b=30)
        )

        st.plotly_chart(fig, use_container_width=True,
                        key=f"plot_{selected_pathway} - {sector} - {product} - {col}")


def _display_pathway(column_pathway_pairs, sector):

    for col, selected_pathway in column_pathway_pairs:
        with col:
            dict_routes_selected = st.session_state["Pathway name"][selected_pathway]
            keys = dict_routes_selected.keys()
            keys_filtered = [k for k in keys if k.startswith(sector + "_")]
            for k in keys_filtered:
                product = k.split("_")[1]
                if len(product.split("-")) > 1:
                    product = "-".join(product.split("-")[1:])

                df = dict_routes_selected[k]

                _plot_configurations(df, selected_pathway,
                                     product, sector, col)
