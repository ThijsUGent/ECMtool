import streamlit as st
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.pathway_select import *
from tool_modules.pathway_view import *
from tool_modules.pathway_perton import *
from tool_modules.import_export_file import *
from tool_modules.maps import *


def welcome():
    st.header("Welcome")
    st.markdown("""
            ### ECM Research Group at Ghent University

            The Energy and Cluster Management (ECM) group at Ghent University focuses on sustainable energy systems, industrial symbiosis, and the optimisation of material and energy flows. The group brings together interdisciplinary research on energy efficiency, cluster-scale integration, and life cycle assessment, aiming to support the transition to a low-carbon economy.

            ### AIDRES Project

            The AIDRES project, funded by the European Commission’s Directorate-General for Energy (DG ENER), aims to develop AI-powered digital tools to facilitate industrial decarbonisation. By identifying, evaluating, and optimising opportunities for resource and energy symbiosis within and between industrial clusters, AIDRES supports both industries and policymakers in accelerating the transition to a more circular and climate-neutral economy.
            """)

    if st.button("Start with a pathway"):
        st.session_state["start_button_pressed"] = True


def Documentation():
    st.header("Documention")


def ECM():
    st.header("ECM")


def About():
    st.header("About")
