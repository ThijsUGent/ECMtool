# aidres_app.py
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)

st.markdown("""
**AIDRES** (Advancing Industrial Decarbonisation by Assessing the Future Use of Renewable Energies in Industrial Processes) is an EU-funded project supporting the decarbonisation of European industry through data-driven analysis, modelling and mapping.

---

## Overview

AIDRES develops and integrates:

- A detailed **database** of energy-intensive industrial sites across the EU-27, mapped at NUTS-3 level.
- **Techno-economic models** to simulate decarbonisation scenarios by 2030 and 2050 for key industrial sectors.
- A **geographical and resource-matching framework** to identify the optimal use of renewable energy in industry.
- A methodology for **industrial symbiosis**, exploring shared heat, energy, and carbon flows at cluster level.

---

## Project Objectives

- Assess how industrial demand for electricity, and energy feedstocks can shift to **renewable sources**.
- Develop pathways combining **electrification**, **green hydrogen**, **carbon capture**, and **process innovation**.
- Map and match **local renewable energy supply potential** with **industrial energy demand**.
- Support EU industrial and energy policy with spatially explicit data and techno-economic insights.

""")

st.markdown("""
---

## Project Partners

The AIDRES project is coordinated by **EnergyVille/VITO** and involves contributions from:

- KU Leuven  
- Ghent University  
- EPFL
- Energyville
- VUB
- Vito
- DECHEMA

---

## Access the Full Report

You can read the full AIDRES final report here:  
[AIDRES Report on EU Publications Portal](https://op.europa.eu/en/publication-detail/-/publication/577d820d-5115-11ee-9220-01aa75ed71a1/language-en)

For more details, also visit:  
[JRC – AIDRES Project Page](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EIGL-Data/AIDRES/)

---

## Citation

Girardin, L., Vallee, D., Correa Laguna, J. et al. (2023).  
*Advancing industrial decarbonisation by assessing the future use of renewable energies in industrial processes (AIDRES)*.  
European Commission – Joint Research Centre.

""")
