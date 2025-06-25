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


from pages.menu_pages import *

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)


if __name__ == "__main__":
    main()
