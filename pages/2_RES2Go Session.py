import streamlit as st
import pandas as pd

st.title("🔎 Session State Explorer")

if not st.session_state:
    st.info("Session state is currently empty.")
else:
    col1, col2 = st.columns([1, 1])  # Pathway left, Cluster right

    # ================= PATHWAY (col1) =================
    with col1:
        if "Pathway name" in st.session_state:
            st.subheader("📂 Pathway")

            pathways_list = list(st.session_state["Pathway name"].keys())

            # --- Remove pathway option ---
            if pathways_list:
                selected_pathway = st.selectbox(
                    "Select a pathway to remove:", pathways_list, key="remove_pathway"
                )
                if st.button("🗑️ Remove selected pathway"):
                    del st.session_state["Pathway name"][selected_pathway]
                    st.success(f"Pathway **{selected_pathway}** removed from session.")
                    st.rerun()

            pathways_list = list(st.session_state["Pathway name"].keys())

            if pathways_list:  # Only create tabs if the list is non-empty
                tab_list = st.tabs(pathways_list)

                for i, pathway in enumerate(pathways_list):
                    with tab_list[i]:
                        st.markdown(f"### Pathway: **{pathway}**")

                        # Collect sector → product mapping from session_state
                        sector_map = {}
                        for sector_product, df in st.session_state["Pathway name"][pathway].items():
                            parts = sector_product.split("_")
                            if len(parts) < 2:
                                continue
                            sector, product = parts[0], "_".join(parts[1:])
                            if not df.empty:
                                sector_map.setdefault(sector, []).append((product, df))

                        # Display each sector with its products
                        for sector, products in sector_map.items():
                            with st.expander(f"Sector: {sector}"):
                                for product, df in products:
                                    st.write(f"**Product:** {product}")
                                    st.dataframe(df)
            else:
                st.info("No pathways available to display.")

    # ================= CLUSTER (col2) =================
    with col2:
        if "Cluster name" in st.session_state:
            st.subheader("📍 Cluster")

            cluster_list = list(st.session_state["Cluster name"].keys())

            # --- Remove cluster option ---
            if cluster_list:
                selected_cluster = st.selectbox(
                    "Select a cluster to remove:", cluster_list, key="remove_cluster"
                )
                if st.button("🗑️ Remove selected cluster"):
                    del st.session_state["Cluster name"][selected_cluster]
                    st.success(f"Cluster **{selected_cluster}** removed from session.")
                    st.rerun()

            cluster_list = list(st.session_state["Cluster name"].keys())

            if cluster_list:  # Only create tabs if the list is non-empty
                tab_list = st.tabs(cluster_list)

                for i, cluster in enumerate(cluster_list):
                    with tab_list[i]:
                        st.markdown(f"### Cluster: **{cluster}**")
                        st.write(st.session_state["Cluster name"][cluster])
            else:
                st.info("No clusters available to display.")