import streamlit as st
st.set_page_config(layout="wide")
logo = "images/logo_UGent_EN_RGB_2400_color.png"
logo_side = "images/logo_side_bar.png"
st.logo(logo_side, size="large",
        link="https://www.ugent.be/ea/emsme/en/research/research-ensy/energy-systems-clusters/ecm", icon_image=logo)
st.title("Acknowledgements")

st.markdown("""
We would like to express our sincere gratitude to all those who made this project possible.

**Special thanks to:**

- The **Directorate-General for Energy (DG ENER)** for coordinating and managing the AIDRES project.  
- **DG REGIO** and the **Industrial Advisory Board** for their valuable and constructive feedback throughout the process.  
- **Université de Nantes**, **Ghent University**, and the **Erasmus+ programme** for supporting the internship that contributed to this work.  
- **Prof. Ir. Greet Van Eetvelde**, for her dedicated supervision at Ghent University and the continued guidance and support from the **ECM research team**.  
- **Nienke Dhont** and **Thijs Duvillard** for their commitment to the development of the RES2Go platform, which supported the implementation of the project’s outcomes.
""")
