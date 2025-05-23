import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def view_page():
    st.title("Product selections")

    if "Pathway name" not in st.session_state or not st.session_state["Pathway name"]:
        st.info("No selections stored yet.")
        return

    pathway_names = list(st.session_state["Pathway name"].keys())

    # Create two columns side by side for pathway selection
    col1, col2 = st.columns(2)

    with col1:
        selected_pathway_name_1 = st.selectbox(
            "Choose pathway 1", pathway_names, key="pathway1"
        )

    with col2:
        selected_pathway_name_2 = st.selectbox(
            "Choose pathway 2", pathway_names, key="pathway2"
        )

    dict_routes_selected_1 = st.session_state["Pathway name"][selected_pathway_name_1]
    dict_routes_selected_2 = st.session_state["Pathway name"][selected_pathway_name_2]

    # Create two columns side by side for plotting
    plot_col1, plot_col2 = st.columns(2)

    with plot_col1:
        st.header(f"Results for {selected_pathway_name_1}")
        _display_pathway(dict_routes_selected_1, selected_pathway_name_1)

    with plot_col2:
        st.header(f"Results for {selected_pathway_name_2}")
        _display_pathway(dict_routes_selected_2, selected_pathway_name_2)


def _display_pathway(dict_routes_selected, pathway_names):
    # make a list with the sectors
    sectors_list = []
    for key in dict_routes_selected:
        first_part = key.split("_")[0]  # splits by underscore and takes first part
        sectors_list.append(first_part)

    # Gather by sector
    for sector in set(sectors_list):  # unique sector names
        with st.expander(f"Products in sector: {sector}"):
            # find all keys in dict_routes_selected starting with this sector
            products = {
                k: v
                for k, v in dict_routes_selected.items()
                if k.startswith(sector + "_")
            }
            for key, df_or_dict in products.items():
                # Assuming df_or_dict is a DataFrame or dict with columns "configuration_name" and "route_weight"
                # If dict, convert to DataFrame
                if not isinstance(df_or_dict, pd.DataFrame):
                    df = pd.DataFrame(df_or_dict)
                else:
                    df = df_or_dict

                fig = px.bar(
                    df,
                    x="configuration_name",
                    y="route_weight",
                    title=key,
                    labels={
                        "configuration_name": "Configuration",
                        "route_weight": "Weight",
                    },
                    barmode="stack",
                )

            st.plotly_chart(fig, key=f"{pathway_names}_{key}")
