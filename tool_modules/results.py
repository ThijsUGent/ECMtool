import streamlit as st
import pandas as pd


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


def results_page():
    st.title("Pathway specific energy/feedstock")

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
        _pathway_perton(dict_routes_selected_1)

    with plot_col2:
        st.header(f"Results for {selected_pathway_name_2}")
        _pathway_perton(dict_routes_selected_2)


def _pathway_perton(dict_routes_selected):
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
                # Convert to DataFrame if needed
                if not isinstance(df_or_dict, pd.DataFrame):
                    df = pd.DataFrame(df_or_dict)
                else:
                    df = df_or_dict
                df_to_show = df[columns_perton_and_weight]
                st.text(f"{key.split('_')[1]}")
                st.dataframe(df_to_show)
                st.text("Per ton Weighted")
                df_weighted = _perton_product_weighted(df)
                st.dataframe(df_weighted[columns_perton])


def _perton_product_weighted(df):
    df = df.copy()  # avoid changing original dataframe

    # Check if product column exists, else fallback to something else or raise error
    if "product_name" not in df.columns:
        raise KeyError(
            "'product_name' column not found in dataframe. Required for grouping weighted values."
        )

    # Multiply each relevant column by route_weight for weighting
    for col in columns_perton:
        if col not in ["configuration_name", "route_weight"]:
            df[col] = df[col] * df["route_weight"]

    # Sum weighted values and total weights per product
    grouped = df.groupby("product_name").sum()

    # Calculate weighted averages by dividing summed weighted values by total weights
    for col in columns_perton:
        if col not in ["configuration_name", "route_weight"]:
            grouped[col] = grouped[col] / grouped["route_weight"]

    return grouped
