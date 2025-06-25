import streamlit as st


def welcome():
    st.header("Welcome")
    st.markdown("""
### [ECM research group at Ghent University](https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm)

The Energy and Cluster Management (ECM) group at Ghent University focuses on sustainable energy systems, industrial symbiosis, and the optimisation of material and energy flows. The group conducts interdisciplinary research on energy efficiency, cluster-scale integration, and life cycle assessment, aiming to support the transition to a low-carbon economy.

### [AIDRES Project](https://op.europa.eu/en/publication-detail/-/publication/577d820d-5115-11ee-9220-01aa75ed71a1/language-en)

The AIDRES database supports the EU-27’s long-term goal of a fully integrated industrial strategy. It serves as a valuable resource for the European Commission and industry stakeholders, offering insights into the effectiveness, efficiency, and cost of potential innovation pathways to achieve carbon neutrality in key sectors—steel, chemical, cement, glass, fertiliser, and refinery—by 2050.
""")

    st.markdown("""
:arrow_backward: Start with the **Pathway** section in the sidebar. Save one or several pathways before proceeding.
""")
