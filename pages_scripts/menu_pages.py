import streamlit as st


def welcome():
    st.header("Welcome")
    st.markdown("""
### ECM Research Group at Ghent University

The Energy and Cluster Management (ECM) group at Ghent University focuses on sustainable energy systems, industrial symbiosis, and the optimisation of material and energy flows. The group conducts interdisciplinary research on energy efficiency, cluster-scale integration, and life cycle assessment, aiming to support the transition to a low-carbon economy.

### [AIDRES Project](https://op.europa.eu/en/publication-detail/-/publication/577d820d-5115-11ee-9220-01aa75ed71a1/language-en)

The AIDRES database supports the EU-27’s long-term goal of a fully integrated industrial strategy. It serves as a valuable resource for the European Commission and industry stakeholders, offering insights into the effectiveness, efficiency, and cost of potential innovation pathways to achieve carbon neutrality in key sectors—steel, chemical, cement, glass, fertiliser, and refinery—by 2050. 

The database includes the geographical distribution of annual production for these sectors at the EU NUTS-3 regional level. The IPCC Special Report on 1.5°C presents compelling evidence in favour of limiting global warming to below 2°C, with efforts to reach 1.5°C as outlined in the Paris Agreement under the UNFCCC. The report highlights the critical need for global CO₂ emissions neutrality by 2050, which is a cornerstone of the EU’s long-term climate strategy. This strategy outlines various pathways to enable the economic and societal transformations required to reach carbon neutrality within the EU by 2050.
""")

    st.markdown("""
:arrow_backward: Start with the **Pathway** section in the sidebar. Save one or several pathways before proceeding.
""")


def Documentation():
    st.header("Documentation")
    st.text("Under construction.")


def ECM():
    st.header("ECM")
    st.text("Under construction.")


def About():
    st.header("About")
    st.text("This tool is part of the PIECE project.")
