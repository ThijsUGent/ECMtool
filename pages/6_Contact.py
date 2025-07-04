import streamlit as st

st.title("Contact Us")
st.markdown(
    "You can give us your feedback and recommendation about **RES2Go beta**.")

st.markdown(
    """
<form id="contactform" action="https://formsubmit.io/send/thijs.duvillard@ugent.be" method="POST">
    <input name="name" type="text" id="name">
    <input name="email" type="email" id="email">
    <textarea name="comment" id="comment" rows="3"></textarea>

    <input name="_formsubmit_id" type="text" style="display:none">

    <input value="Submit" type="submit">
</form>

    """,
    unsafe_allow_html=True
)
