# Streamlit interface and data tools
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json

from tool_modules.import_export_file import *
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.builder_functions import *

# Mapping short codes to readable product names
product_updates = {
    "cement": "Cement",
    "chemical-PE": "Polyethylene",
    "chemical-PEA": "Polyethylene acetate",
    "chemical-olefins": "Olefins",
    "fertiliser-ammonia": "Ammonia",
    "fertiliser-nitric-acid": "Nitric acid",
    "fertiliser-urea": "Urea",
    "glass-container": "Container glass",
    "glass-fibre": "Glass fibre",
    "glass-float": "Float glass",
    "refineries-light-liquid-fuel": "Light liquid fuel",
    "steel-secondary" : "Secondary steel", 
    "steel-primary" : "Primary steel"
}

# Mapping products to detailed descriptions
def_product = {
    "cement": (
        "Cement products include Portland Cement II (BV325R) and "
        "Limestone Calcined Clay Cement (LC3), based on the AIDRES report: "
        "https://op.europa.eu/en/publication-detail/-/publication/577d820d-5115-11ee-9220-01aa75ed71a1"
    ),
    "chemical-PE": (
        "Polyethylene (PE) products, derived from ethylene, "
        "commonly used in packaging, films, and molded items. "
        "Details based on the AIDRES report."
    ),
    "chemical-PEA": (
        "Polyethylene acetate (PEA) products, derived from polyethylene "
        "with acetate modifications, used in coatings, adhesives, "
        "and specialty plastics. Based on the AIDRES report."
    ),
    "chemical-olefins": (
        "Olefins (ethylene, propylene, and related derivatives), "
        "used as building blocks for plastics, chemicals, and fuels. "
        "Details from the AIDRES report."
    ),
    "fertiliser-ammonia": (
        "Ammonia-based fertiliser products, produced from nitrogen "
        "and hydrogen, widely used as feedstock for other fertilisers. "
        "Based on the AIDRES report."
    ),
    "fertiliser-nitric-acid": (
        "Nitric acid-based fertiliser products, typically used in the "
        "production of ammonium nitrate and related compounds. "
        "Details from the AIDRES report."
    ),
    "fertiliser-urea": (
        "Urea-based fertiliser products, the most widely used nitrogen fertiliser, "
        "produced from ammonia and carbon dioxide. Based on the AIDRES report."
    ),
    "glass-container": (
        "Container glass products, primarily bottles and jars used "
        "for packaging food, beverages, and other goods. "
        "Details from the AIDRES report."
    ),
    "glass-fibre": (
        "Glass fibre products, used in insulation, composites, and "
        "reinforcement materials. Based on the AIDRES report."
    ),
    "glass-float": (
        "Float glass products, manufactured by floating molten glass on a "
        "bed of molten metal, used in windows, facades, and mirrors. "
        "Details from the AIDRES report."
    ),
    "refineries-light-liquid-fuel": (
        "Light liquid fuel products, including gasoline and other "
        "refined fractions derived from crude oil. "
        "Based on the AIDRES report."
    ),
}

def select_page():

    # --- init session_state ---
    if "adding_sector" not in st.session_state:
        st.session_state.adding_sector = False
    if "sectors_list_new" not in st.session_state:
        st.session_state.sectors_list_new = []
    if "new_sector" not in st.session_state:
        st.session_state.new_sector = ""
    

    # Prechoice radio doc link

    if "pathway_configuration_prechoice" not in st.session_state:
        st.session_state["pathway_configuration_prechoice"] = 0

    pathway_configuration_prechoice = st.session_state.get(
        "pathway_configuration_prechoice", 0)

    st.subheader("Pathway Configuration")
    # creates two columns with a 4:1 width ratio
    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(
            "Select a ready-made path, upload another path or create your path")

        # Load and clean the per-ton configuration data
        perton_path = "data/perton_all.csv"
        perton_ALL = pd.read_csv(perton_path)


        perton_ALL = perton_ALL.groupby(
            "configuration_id").first().reset_index()

        perton_ALL = process_configuration_dataframe(perton_ALL)

        perton_ALL_no_mix = perton_ALL[~perton_ALL["configuration_name"].str.contains(
            "mix")]

        perton_ALL_no_mix["route_name"] = perton_ALL_no_mix["configuration_name"].replace(
            "route_name")
        
        # Replace product names using the mapping
        perton_ALL_no_mix["product_name"] = perton_ALL_no_mix["product_name"].replace(product_updates)
                

        # Columns to be shown in the route selection editor
        columns_to_show_selection = [
            "selected",
            "route_name",
            "horizon",
            "energy_feedstock",
            "technology_category",
            "hydrogen_source",
        ]

        selection = st.radio(
            "Choose an option",
            ["Ready-made path", "Upload a path", "Create a path"],
            horizontal=True, index=pathway_configuration_prechoice
        )
        aidres_mix_checked = selection == "Ready-made path"
        upload_mix_checked = selection == "Upload a path"
        create_mix_checked = selection == "Create a path"

        # --- EU-MIX AUTOMATED PATHWAY SELECTION ---
        if aidres_mix_checked:
            dict_routes_selected, selected_mix, pathway_name = preconfigure_path(
                perton_ALL_no_mix, columns_to_show_selection)

    # --- CUSTOM FROM-SCRATCH PATHWAY BUILDING ---
        if create_mix_checked:
            dict_routes_selected, pathway_name = create_path(
                perton_ALL_no_mix, columns_to_show_selection)
    # --- IMPORT PATHWAY FROM .txt FILE ---
        if upload_mix_checked:
            dict_routes_selected, pathway_name = upload_path(
                perton_ALL_no_mix, columns_to_show_selection)
        if any(not df.empty for df in dict_routes_selected.values()):
            # At least one DataFrame is not empty

            # Keep only the selected rows (where route_weight not 0)
            for key in dict_routes_selected.keys():
                dict_routes_selected[key] = dict_routes_selected[key][dict_routes_selected[key]
                                                                      ["route_weight"] != 0]
        st.markdown(
            "**Save the pathway before proceeding.**")
        with col2:
            st.text("Save the pathway")

            # --- PATHWAY NAMING AND SAVING ---
            pathway_name = st.text_input(
                "Enter a name for your pathway", value=pathway_name)

            if dict_routes_selected:

                if "Pathway name" not in st.session_state:
                    st.session_state["Pathway name"] = {}

                # Save button
                if st.button("Save pathway"):
                    
                    if pathway_name.strip() == "":
                        st.warning("Please enter a name for the pathway.")
                    elif pathway_name in st.session_state["Pathway name"]:
                        st.warning(
                            f"A pathway named '{pathway_name}' already exists.")
                    else:
                        st.session_state["Pathway name"][pathway_name] = dict_routes_selected
                        st.session_state.sectors_list_new = []
                        st.session_state.new_sector = ""
                        st.success(f"Pathway '{pathway_name}' saved.")
                # Download button (triggers logic only when clicked)
                if st.button("Download pathway"):
                    if pathway_name.strip() == "":
                        st.warning("Please enter a name for the pathway.")
                    else:
                        combined_df = pd.concat(
                            dict_routes_selected.values(), ignore_index=True)
                        exported_txt = export_to_txt(combined_df)
                        st.download_button(
                            label="Click here to download",
                            data=exported_txt,
                            file_name=f"ECM_Tool_{pathway_name}.txt",
                            mime="text/plain",
                            type="tertiary"
                        )

            else:
                st.text("Please upload or create a pathway before saving.")

                
