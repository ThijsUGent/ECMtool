import streamlit as st
import pandas as pd

st.title("🔎 Session State Explorer")

if not st.session_state:
    st.info("Session state is currently empty.")
else:
    if "Pathway name" in st.session_state:
        st.subheader("Pathway within this session")

        # --- Remove pathway option ---
        pathways_list = list(st.session_state["Pathway name"].keys())
        if pathways_list:
            selected_pathway = st.selectbox(
                "Select a pathway to remove:", pathways_list
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