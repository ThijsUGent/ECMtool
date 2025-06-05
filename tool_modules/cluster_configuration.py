import streamlit as st


def cluster_configuration():
    choice = st.radio("Select an option", [
                      "Create a cluster", "Upload a cluster"])

    if choice == "Create a cluster":
        st.text("Under construction")
    if choice == "Upload a cluster":
        st.text("Under construction")
