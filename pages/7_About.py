import streamlit as st

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)


# Header and descriptions
st.header("About")
st.markdown(
    "This tool results from the **PIECE** project, developed by the **ECM research group** at ([Energy and cluster management (ECM) — Department of ElectroMechanical, Systems and Metal Engineering — Ghent University)](https://www.ugent.be/ea/emsme/en/research/ensy/energy-systems-clusters/ecm)).")

st.header("Beta version")
st.markdown("**RES2Go beta 2.0** – July 2025")

st.markdown(
    "[RES2Go beta](https://ugent-ecm-res2gobeta.streamlit.app/ECM)")
