import streamlit as st


def doc_maps():
    if "tool_subsection_prechoice" not in st.session_state:
        st.session_state["tool_subsection_prechoice"] = 0

    tool_subsection_prechoice = st.session_state.get(
        "tool_subsection_prechoice", 0)

    subsection = st.radio("Subsection:", [
        "Mapping",
        "Clustering",
    ], index=tool_subsection_prechoice, horizontal=True)

    if subsection == "Mapping":

        with st.expander("Site view"):
            if st.button("Go to Mapping →"):
                st.video("video/maps/maps_mapping_views.mp4")
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("Utilisation rate editing"):
            if st.button("Go to Mapping →"):
                st.video("video/maps/maps_mapping_utilisation.mp4")
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("Energy carrier & sector selection"):
            if st.button("Go to Mapping →"):
                st.video("video/maps/maps_mapping_sectors.mp4")
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("Cluster export"):
            st.video("video/maps/maps_mapping_clusterexport.mp4")
            if st.button("Go to Mapping →"):
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")

    if subsection == "Clustering":

        with st.expander("Change cluster algorithm"):
            if st.button("Go to Mapping →"):
                st.video("video/maps/maps_clustering_change.mp4")
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("DBSCAN parameters"):
            if st.button("Go to Mapping →"):
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("KMEANS parameters"):
            if st.button("Go to Mapping →"):
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
        with st.expander("KMEANS weighted parameters"):
            if st.button("Go to Mapping →"):
                st.session_state["tool_subsection_prechoice"] = 1
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")
