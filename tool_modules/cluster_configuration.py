import streamlit as st
import pandas as pd
import numpy as np


dict_product_by_sector = {
    "Cement": ["cement"],
    "Chemical": [
        "chemical-PE",
        "chemical-PEA",
        "chemical-olefins"
    ],
    "Fertilisers": [
        "fertiliser-ammonia",
        "fertiliser-nitric-acid",
        "fertiliser-urea"
    ],
    "Glass": [
        "glass-container",
        "glass-fibre",
        "glass-float"
    ],
    "Refineries": [
        "refineries-light-liquid-fuel"
    ],
    "Steel": [
        "steel-primary",
        "steel-secondary"
    ]
}

sectors_list = [
    "Cement", "Chemical", "Fertilisers", "Glass", "Refineries", "Steel"
]


def cluster_configuration():
    choice = st.radio("Select an option", [
                      "Create a cluster", "Upload a cluster"], horizontal=True)

    df_cluster = pd.DataFrame()
    cluster_name = "Cluster 1"

    if choice == "Create a cluster":
        df_cluster = _cluster_product_selection()

    if choice == "Upload a cluster":
        df_cluster, cluster_name = upload_cluster()
    if not df_cluster.empty and df_cluster['site'].notnull().any():
        # Input cluster name first
        cluster_name = st.text_input(
            "Enter a name for your Cluster", value=cluster_name)

    if not df_cluster.empty and df_cluster['site'].notnull().any():

        with st.expander("Sites in the cluster", expanded=True):
            st.dataframe(df_cluster, hide_index=True, use_container_width=True)

        # Save button
        if "Cluster name" not in st.session_state:
            st.session_state["Cluster name"] = {}

        if st.button("Save Cluster"):
            if cluster_name.strip() == "":
                st.warning("Please enter a name for the cluster.")
            elif cluster_name in st.session_state["Cluster name"]:
                st.warning(
                    f"A cluster named '{cluster_name}' already exists.")
            else:
                st.session_state["Cluster name"][cluster_name] = df_cluster
                st.success(f"Cluster '{cluster_name}' saved.")

        # Download button (triggers logic only when clicked)
        if st.button("Download Cluster"):
            if cluster_name.strip() == "":
                st.warning("Please enter a name for the cluster.")
            else:
                combined_df = pd.concat([df_cluster], ignore_index=True)
                exported_txt = combined_df.to_csv(
                    index=False, sep=","
                )

                st.download_button(
                    label="Click here to download",
                    data=exported_txt,
                    file_name=f"ECM_Tool_{cluster_name}.txt",
                    mime="text/plain",
                    type="tertiary"
                )

        else:
            st.text("Please upload or create a cluster before saving.")


def _cluster_product_selection():
    # Dictionary to collect selected sites per sector-product
    dict_cluster_selected = {}

    sectors_list_all = ["Cement", "Chemical",
                        "Fertilisers", "Glass", "Refineries", "Steel"]
    sectors_list_plus_other = sectors_list_all + ["Other sectors"]

    selected_sectors = st.pills(
        "Sector(s)", sectors_list_plus_other, selection_mode="multi"
    )

    if not selected_sectors:
        st.warning("Please select at least 1 sector")
        return pd.DataFrame()

    tabs = st.tabs(selected_sectors)

    for i, sector in enumerate(selected_sectors):
        with tabs[i]:
            if sector == "Other sectors":
                other_products = []
                if st.session_state.get("Pathway name"):
                    for name, pathway in st.session_state["Pathway name"].items():
                        for sector_product in pathway.keys():
                            split_parts = sector_product.split("_")
                            if split_parts[0] == "Other sectors":
                                other_products.append(split_parts[-1])
                    all_products = other_products
                else:
                    all_products = []
            else:
                all_products = dict_product_by_sector[sector]

            for product in all_products:
                with st.expander(f"{product}", expanded=False):
                    df = _get_df_site_parameters(product)
                    df["product"] = product
                    df["sector"] = sector
                    dict_cluster_selected[f"{sector}_{product}"] = df

    if all(df.empty for df in dict_cluster_selected.values()):
        st.warning("Create at least one site in the cluster.")
        return pd.DataFrame()

    df_cluster = pd.concat(dict_cluster_selected.values())
    return df_cluster


def _get_df_site_parameters(product):
    # --- Define the template DataFrame ---
    df_template = pd.DataFrame({
        'site': pd.Series(dtype='str'),
        'production capacity (kt)': pd.Series(dtype='float64'),
    })

    # --- Let the user edit the DataFrame with column config ---
    edited_df = st.data_editor(
        df_template,
        num_rows="dynamic",
        hide_index=True,  # hides the index column
        use_container_width=True,
        key=f"site_parameters_{product}",
        column_order=['site', 'production capacity (kt)'],
        column_config={
            "site": st.column_config.TextColumn(
                "site",
                help="Enter the site name"
            ),
            "production capacity (kt)": st.column_config.NumberColumn(
                "production capacity (kt)",
                help="Enter production capacity in kt",
                min_value=0.0,
                format="%.2f"
            ),
        }
    )

    return edited_df


def upload_cluster():
    sectors_list_all = ["Cement", "Chemical",
                        "Fertilisers", "Glass", "Refineries", "Steel"]
    sectors_list_plus_other = sectors_list_all + ["Other sectors"]

    # Initialization
    df_cluster = pd.DataFrame()
    modified = False
    st.text("Drag & drop .txt cluster file")
    uploaded_file = st.file_uploader(
        "Upload your cluster file here", type=["txt"]
    )
    cluster_name = "Upload file"
    if uploaded_file:
        import re
        cluster_name = uploaded_file.name.split(".")[0]
        match = re.search(r"ECM_Tool_(.+)_cluster$", cluster_name)
        if match:
            cluster_name = match.group(1)
        # Read the uploaded file directly into a DataFrame
        df = pd.read_csv(uploaded_file, sep=",")
        # Try to infer sector and product columns, or fallback to template
        if set(['sector', 'product']).issubset(df.columns):
            tabs = st.tabs(sectors_list_plus_other)
            for i, sector in enumerate(sectors_list_plus_other):
                with tabs[i]:
                    if sector == "Other sectors":
                        other_products = []
                        for product in df[df["sector"] == sector]["product"].unique():
                            other_products.append(product)
                        all_products = other_products
                        if st.session_state.get("Pathway name"):
                            all_possible_products = set()
                            for name, pathway in st.session_state["Pathway name"].items():
                                for sector_product in pathway.keys():
                                    split_parts = sector_product.split("_")
                                    if split_parts[0] == "Other sectors":
                                        all_possible_products.add(
                                            split_parts[-1])
                        rest_all_products = list(
                            set(all_possible_products) - set(all_products))
                        if rest_all_products:
                            product_selected = st.multiselect(
                                "Select a product included in pathways", rest_all_products
                            )
                            if product_selected and product_selected not in all_products:
                                all_products.extend(product_selected)

                    else:
                        all_products = dict_product_by_sector[sector]
                    for product in all_products:
                        with st.expander(f"{sector} - {product}", expanded=False):
                            df_product = df[(df['sector'] == sector) & (
                                df['product'] == product)].copy()
                            if not df_product.empty:
                                df_product = df_product
                            else:
                                df_product = pd.DataFrame({
                                    'site': pd.Series(dtype='str'),
                                    'production capacity (kt)': pd.Series(dtype='float64'),
                                })

                            # --- Let the user edit the DataFrame with column config ---
                            edited_df = st.data_editor(
                                df_product,
                                num_rows="dynamic",
                                hide_index=True,
                                use_container_width=True,
                                key=f"site_parameters_{product}",
                                column_order=[
                                    'site', 'production capacity (kt)'],
                                column_config={
                                    "site": st.column_config.TextColumn(
                                        "site",
                                        help="Enter the site name"
                                    ),
                                    "production capacity (kt)": st.column_config.NumberColumn(
                                        "production capacity (kt)",
                                        help="Enter production capacity in kt",
                                        min_value=0.0,
                                        format="%.2f"
                                    ),
                                }
                            )

                            if not edited_df.empty:
                                edited_df['product'] = product
                                edited_df['sector'] = sector
                            df_cluster = pd.concat(
                                [df_cluster, edited_df], ignore_index=True)
                            if not df_product.equals(edited_df):
                                modified = True
        else:
            st.warning(
                "Uploaded file not in the good format")
            return pd.DataFrame(), cluster_name

    else:
        st.warning("Please upload a cluster file.")
        return pd.DataFrame(), cluster_name

    if modified:
        cluster_name += " modified"
    return df_cluster, cluster_name
