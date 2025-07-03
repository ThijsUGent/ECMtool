import streamlit as st

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)


# Header and descriptions
st.header("About")
st.markdown("This tool is part of the **PIECE** project. Developed by the **ECM research group** at Ghent University (UGent).")

st.header("Versions")
st.markdown("**RES2Go 2.0** – 3 July 2025")
