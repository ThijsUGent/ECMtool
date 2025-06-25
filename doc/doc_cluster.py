import streamlit as st


def doc_cluster():
    if "tool_subsection_prechoice" not in st.session_state:
        st.session_state["tool_subsection_prechoice"] = 0

    tool_subsection_prechoice = st.session_state.get(
        "tool_subsection_prechoice", 0)

    subsection = st.radio("Subsection:", [
        "Cluster configuration",
        "Cluster results",
    ], index=tool_subsection_prechoice, horizontal=True)

    if subsection == "Cluster configuration":
        with st.expander("Create a cluster"):
            st.video("video/cluster/cluster_create.mp4",
                     subtitles="video/cluster/cluster_create.vtt")
            if st.button("Go to Pre-made pathway →"):
                st.session_state["tool_subsection_prechoice"] = 2
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")

        with st.expander("Upload a cluster"):
            st.video("video/pathway/upload_create.mp4",
                     subtitles="video/pathway/upload_create.vtt", end_time="1m47s")
            if st.button("Go to Create a pathway →"):
                st.session_state["tool_subsection_prechoice"] = 2
                st.session_state["pathway_configuration_prechoice"] = 0
                st.switch_page("pages/1_Tool.py")

    if subsection == "Cluster results":

        with st.expander("Visualise results"):
            st.video("video/cluster/cluster_view.mp4",
                     subtitles="video/cluster/cluster_view.vtt")
            if st.button("Go to Pre-made pathway →"):
                st.session_state["tool_subsection_prechoice"] = 2
                st.session_state["pathway_configuration_prechoice"] = 1
                st.switch_page("pages/1_Tool.py")
