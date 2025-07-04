import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pandas as pd
import re

st.title("Contact Form")

st.markdown(
    """
    Please fill out the form below to send us a message.

    _🔒 All information you submit will remain confidential and will not be shared with third parties._
    """
)

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data
df = conn.read()

# Contact form
with st.form("message_form"):
    name = st.text_input("Your name")
    email = st.text_input("Your email")
    message = st.text_area("Your message")
    submitted = st.form_submit_button("Send")

    # Email format check
    email_valid = re.match(r"[^@]+@[^@]+\.[^@]+", email)

    if submitted:
        if name and email and message:
            if not email_valid:
                st.warning("⚠️ Please enter a valid email address.")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = pd.DataFrame(
                    [[timestamp, name, email, message]],
                    columns=["Timestamp", "Name", "Email", "Message"]
                )
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="messages", data=df)
                st.success("✅ Your message has been submitted!")
        else:
            st.warning("⚠️ Please fill in all fields.")
