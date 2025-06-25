import streamlit as st
from tool_modules.eu_mix_preconfiguration import *
from tool_modules.categorisation import *
from tool_modules.pathway_select import *
from tool_modules.pathway_view import *
from tool_modules.pathway_perton import *
from tool_modules.import_export_file import *
from tool_modules.maps import *
from tool_modules.cluster_results import *
from tool_modules.cluster_configuration import *
from tool_modules.emissions import *
from doc.doc_pathway import *

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)


st.header("Welcome")
st.markdown("""
    This tool starts from the AIDRES project, creating a variety of energy demand projections for industrial sites and clusters with a high level of product, process and location-based flexibilities and functionalities. Users can forecast energy pathways by modifying products and processes, creating clusters at micro to macro-level, and assess future demand of multiple energy vectors.   """)

st.markdown("""
    :arrow_down: Start to check tutorial in documentation section and use the tool :arrow_down:
    """)
st.page_link("pages/2_Documentation.py",
             label="Documentation", icon="📖", use_container_width=True)
st.page_link("pages/1_Tool.py", label="Tool",
             icon="⚙️", use_container_width=True)
