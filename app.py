import streamlit as st
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.pathway_select import *
from tool_modules.pathway_view import *
from tool_modules.results import *
from tool_modules.import_export_file import *

st.set_page_config(layout="wide")
st.logo("images/logo_UGent_EN_RGB_2400_color.png", size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm")


def main():
    st.sidebar.title("Navigation")

    # Pathway section
    with st.sidebar.expander("Pathway", expanded=True):
        pathway_subsection = st.radio(
            "Select a page",
            ["Pathway configuration", "Pathway visualisation", "Pathway perton"],
            key="pathway_sub",
        )

    # Cluster - microscale section
    with st.sidebar.expander("Cluster - microscale", expanded=False):
        cluster_subsection = st.radio(
            "Select a page", ["Cluster viewer", "Cluster analysis"], key="cluster_sub"
        )

    # Maps - European scale section
    with st.sidebar.expander("Maps - European scale", expanded=False):
        maps_subsection = st.radio(
            "Select a page", ["Emission map", "Energy flow map"], key="maps_sub"
        )

    # Page logic
    if pathway_subsection == "Pathway configuration":
        select_page()
    elif pathway_subsection == "Pathway visualisation":
        view_page()
    elif pathway_subsection == "Pathway perton":
        results_page()
    elif cluster_subsection == "Cluster viewer":
        st.text("Cluster viewer page under construction")
    elif cluster_subsection == "Cluster analysis":
        st.text("Cluster analysis page under construction")
    elif maps_subsection == "Emission map":
        st.text("Emission map page under construction")
    elif maps_subsection == "Energy flow map":
        st.text("Energy flow map page under construction")


if __name__ == "__main__":
    main()
