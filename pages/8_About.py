import streamlit as st

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)

st.markdown(
    """
## About

This tool results from the **PIECE** project, developed by the **ECM research group** at [Energy and Cluster Management (ECM) — Department of ElectroMechanical, Systems and Metal Engineering — Ghent University](https://www.ugent.be/ea/emsme/en/research/ensy/energy-systems-clusters/ecm).

---

### Beta version  

**RES2Go beta 2.0** – July 2025  

[RES2Go beta](https://ugent-ecm-res2gobeta.streamlit.app/ECM)

---

### License  

RES2Go License – Free to Use, No Modification

Copyright (c) 2025 Ghent University, ECM Research Group

---

### Citation  

T. Duvillard, N. Dhont, G. Van Eetvelde\*, *RES2Go tool*, University of Ghent, 2025.  

\* Contact: [ecm@ugent.be](mailto:ecm@ugent.be)
"""
)