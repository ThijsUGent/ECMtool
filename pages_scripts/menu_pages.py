import streamlit as st


def welcome():
    st.header("Welcome")
    st.markdown("""
### [ECM research group at Ghent University](https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm)

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
    st.header(
        "[ECM](https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm)")
    st.markdown("""The Energy & Cluster Management group is matured from the synergy between environment and entrepreneurship, between study and implementation of industrial symbiosis, performed since 1998.

 Research topics focus on concerted energy & resource management at business parks, on industrial sites or in cross-sectorial clusters. It concerns characteristic interdisciplinary research, combining engineering & modelling skills with economic analyses, spatial planning, policy settings and social responsibility.

The main line of research is on advancing the ECM LESTS (Legal, Economic, Spatial, Technical and Social) survey for assessing park management intensity into a toolbox for driving energy symbiosis and circular economy principles in and across process industries. Typical ECM projects focus on energy efficiency, resource optimisation, site integration, waste (heat) recovery, regional clustering, etc.""")
    st.subheader(
        "[PIECE project](https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm/piece)")
    st.markdown("""**Overview**""")

    st.markdown("""PIECE is a direct ECM collaboration with EU DG ENER on the potential for energy clustering and flexibility to support the low-carbon transition in industry, framed by a master’s thesis project in an Erasmus exchange with the University of Nantes in France. In a first step the low-carbon energy potential across Europe is evaluated using public databases such as ENSPRESO and ExtremOS, as well as the industrial demand based on AIDRES scenarios and input from the project's industry advisory board. Both supply and demand are integrated in a cluster-based approach, which serves as basis to map the potential in Europe and target the most relevant regions through case studies. The selected industrial hubs are assessed for challenges and opportunities to adopt low-carbon energy in a competitive cluster environment. The project results in support for industrial stakeholders and policymakers to advance towards a net-zero European industrial tissue.""")

    st.markdown("""**Objective**""")

    st.markdown("""The main objective of this master’s thesis project is to investigate how to reduce emissions in energy-intensive industry by clustering energy demand and providing low-carbon energy solutions while advancing industrial competitiveness in Europe.""")


def About():
    st.header("About")
    st.text("This tool is part of the PIECE project.")
