import streamlit as st
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.pathway_select import *
from tool_modules.pathway_view import *
from tool_modules.pathway_perton import *
from tool_modules.import_export_file import *
from tool_modules.maps import *
from tool_modules.cluster_results import *
from tool_modules.cluster_configuration import *
from tool_modules.emissions import *


def main():
    with st.sidebar:
        st.divider()
        st.markdown("**Choose a section**")

        # Show the radio widget with the current session_state as default
        tool_section = st.radio(
            "",
            ["Pathway",
                "Maps - European scale", "Cluster - microscale"],
            index=["-- Select a section --", "Pathway", "Maps - European scale", "Cluster - microscale"].index(
                st.session_state["tool_section"]
            ),
            key="tool_section",
        )

        if tool_section == "Pathway":
            pathway_subsection = st.sidebar.radio(
                "Select a page",
                [
                    "Pathway configuration",
                    "Production route consumption",
                    "CO2 Emissions",
                    "Pathway visualisation",
                ],
                key="pathway_sub",
            )
            if pathway_subsection == "Pathway configuration":
                select_page()
            elif pathway_subsection == "Production route consumption":
                perton_page()
            elif pathway_subsection == "CO2 Emissions":
                emissions_page()
            elif pathway_subsection == "Pathway visualisation":
                view_page()

        elif tool_section == "Maps - European scale":
            maps_subsection = st.sidebar.radio(
                "Select a page", ["Map per pathway"], key="maps_sub"
            )
            if maps_subsection == "Map per pathway":
                map_per_pathway()

        elif tool_section == "Cluster - microscale":
            cluster_subsection = st.sidebar.radio(
                "Select a page", ["Cluster configuration", "Cluster results"], key="cluster_sub"
            )
            if cluster_subsection == "Cluster configuration":
                cluster_configuration()
            elif cluster_subsection == "Cluster results":
                cluster_results()
