import streamlit as st
import psycopg2
from psycopg2 import sql
from datetime import datetime


# Connect to database

db_config = st.secrets["postgres"]


def insert_message(name, email, subject, message):
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, subject, message))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False


# -- UI
st.title("📬 Contact Us")
st.markdown("We'd love to hear your thoughts about **RES2Go beta**.")

with st.form("contact_form"):
    name = st.text_input("Name *")
    email = st.text_input("Email *")
    subject = st.text_input("Subject")
    message = st.text_area("Message *")
    submitted = st.form_submit_button("Send")

    if submitted:
        if name and email and message:
            success = insert_message(name, email, subject, message)
            if success:
                st.success(
                    "✅ Your message has been sent and stored in our database.")
        else:
            st.error("❌ Please fill in all required fields.")
