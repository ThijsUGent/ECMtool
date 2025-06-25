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

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)

# Session state doc link

if "tool_section_prechoice" not in st.session_state:
    st.session_state["tool_section_prechoice"] = 0

if "tool_subsection_prechoice" not in st.session_state:
    st.session_state["tool_subsection_prechoice"] = 0

tool_section_prechoice = st.session_state.get("tool_section_prechoice", 0)
tool_subsection_prechoice = st.session_state.get(
    "tool_subsection_prechoice", 0)


# Show the radio widget with the current session_state as default
tool_section = st.sidebar.radio(
    "",
    ["Pathway",
        "Maps - European scale", "Cluster - microscale"],

    key="tool_section", index=tool_section_prechoice
)

# PATHWAY

if tool_section == "Pathway":
    st.session_state[
        "tool_section_prechoice_doc"] = 0
    pathway_subsection = st.sidebar.radio(
        "Select a page",
        [
            "Pathway configuration",
            "Production route consumption",
            "CO2 Emissions",
            "Pathway visualisation",
        ], index=tool_subsection_prechoice,
        key="pathway_sub",
    )
    if pathway_subsection == "Pathway configuration":
        select_page()
        if st.button(label="📖 Documentation 📖"):
            st.session_state[
                "tool_subsection_prechoice"] = 0
            st.switch_page("pages/2_Documentation.py")
    elif pathway_subsection == "Production route consumption":
        perton_page()
        if st.button(label="📖 Documentation 📖"):
            st.session_state[
                "tool_subsection_prechoice"] = 1
            st.switch_page("pages/2_Documentation.py")
    elif pathway_subsection == "CO2 Emissions":
        emissions_page()
        if st.button(label="📖 Documentation 📖"):
            st.session_state[
                "tool_subsection_prechoice"] = 2
            st.switch_page("pages/2_Documentation.py")
    elif pathway_subsection == "Pathway visualisation":
        view_page()
        if st.button(label="📖 Documentation 📖"):
            st.session_state[
                "tool_subsection_prechoice"] = 3
            st.switch_page("pages/2_Documentation.py")

# MAPS

elif tool_section == "Maps - European scale":
    st.session_state[
        "tool_section_prechoice_doc"] = 1
    maps_subsection = st.sidebar.radio(
        "Select a page", ["Map per pathway"], key="maps_sub"
    )
    if maps_subsection == "Map per pathway":
        map_per_pathway()

# CLUSTER

elif tool_section == "Cluster - microscale":
    st.session_state[
        "tool_section_prechoice_doc"] = 2
    cluster_subsection = st.sidebar.radio(
        "Select a page", ["Cluster configuration", "Cluster results"], key="cluster_sub", index=tool_subsection_prechoice
    )
    if cluster_subsection == "Cluster configuration":
        cluster_configuration()
    elif cluster_subsection == "Cluster results":
        cluster_results()
