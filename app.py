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


from pages_scripts.menu_pages import *

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)


def main():
    # initilisation
    buttons = False
    st.session_state["start_button_pressed"] = False

    if "main_section" not in st.session_state:
        st.session_state["main_section"] = "-- Select a section --"

    if st.sidebar.button("Welcome", type="tertiary"):
        st.session_state["main_section"] = "-- Select a section --"
        buttons = True
        welcome()

        # Other sections
    if st.sidebar.button("Documentation", type="tertiary"):
        st.session_state["main_section"] = "-- Select a section --"
        buttons = True
        Documentation()
    if st.sidebar.button("ECM", type="tertiary"):
        st.session_state["main_section"] = "-- Select a section --"
        buttons = True
        ECM()
    if st.sidebar.button("About", type="tertiary"):
        st.session_state["main_section"] = "-- Select a section --"
        buttons = True
        About()

    st.sidebar.divider()
    st.sidebar.subheader("Tool")

    # Static label above the radio
    st.sidebar.markdown("**Choose a section**")

    # Use a placeholder and conditional rendering for better default behaviour
    main_options = ["-- Select a section --", "Pathway", "Maps - European scale",
                    "Cluster - microscale"]

    # Determine the current main section selection

    main_section = st.sidebar.radio(
        "", main_options, key="main_section", index=main_options.index(st.session_state["main_section"]), label_visibility="collapsed"
    )

    if main_section == "-- Select a section --":
        if not buttons:
            welcome()

    if main_section == "Pathway":
        pathway_subsection = st.sidebar.radio(
            "Select a page",
            ["Pathway configuration", "Production route consumption", "CO2 Emissions", "Pathway visualisation"
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

    elif main_section == "Maps - European scale":
        maps_subsection = st.sidebar.radio(
            "Select a page", ["Map per pathway"], key="maps_sub"
        )
        if maps_subsection == "Map per pathway":
            map_per_pathway()
        # elif maps_subsection == "Map per utilisation rate":
        #     map_per_utlisation_rate()

    elif main_section == "Cluster - microscale":
        cluster_subsection = st.sidebar.radio(
            "Select a page", ["Cluster configuration", "Cluster results"], key="cluster_sub"
        )
        if cluster_subsection == "Cluster configuration":
            cluster_configuration()
        elif cluster_subsection == "Cluster results":
            cluster_results()
        # elif cluster_subsection == "Production by cluster":
        #     cluster_production()


if __name__ == "__main__":
    main()
