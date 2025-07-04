import streamlit as st

st.title("Contact Us")
st.markdown(
    "You can give us your feedback and recommendation about **RES2Go beta**.")

st.markdown(
    """
    <form action="https://formsubmit.co/duvillard.t@gmail.com" method="POST">
  <!-- disable captcha -->
  <input type="hidden" name="_captcha" value="false">

  <label for="name">Name</label>
  <input type="text" name="name" required>

  <label for="email">Email</label>
  <input type="email" name="email" required>

  <label for="message">Message</label>
  <textarea name="message" required></textarea>

  <button type="submit">Send</button>
</form>
    """,
    unsafe_allow_html=True
)
