import streamlit as st
from pages.doc.doc_pathway import *


def Documentation():
    st.title("Documentation")

    tab_options = [
        "📘 Pathway",
        "🗺️ Maps - European scale",
        "🔬 Cluster - microscale",
        "📚 Glossary"
    ]

    tabs_choice = st.pills("Select section", tab_options)

    if tabs_choice == "📘 Pathway":
        st.header("Pathway")
        st.markdown("""This tool uses the AIDRES database to extract the energy need for each product through configurable pathways. Users can create and save multiple pathways that represent different industrial scenarios, serving as the basis for subsequent analyses.""")
        doc_pathway()

    elif tabs_choice == "🗺️ Maps - European scale":
        st.header("Maps - European scale")
        st.markdown("""The spatial data from AIDRES is visualised at the European scale to assess and compare the energy need across different regions. Sites are clustered based on geographical proximity and sector characteristics, helping to identify regional potentials for decarbonisation and clustering.""")

    elif tabs_choice == "🔬 Cluster - microscale":
        st.header("Cluster - microscale")
        st.markdown("""The microscale section allows full customisation of clusters. Users can define the annual production of multiple products within a cluster, download existing cluster configurations, or upload their own. The results can be compared visually using treemaps and sankey diagrams, supporting deeper insights into energy flows and interconnections.""")

    elif tabs_choice == "📚 Glossary":
        st.header("Glossary")
        st.markdown("""The glossary provides definitions and explanations of key terms and concepts used throughout the tool, ensuring users have a clear understanding of the terminology related to energy systems, industrial symbiosis, and the AIDRES database.""")
