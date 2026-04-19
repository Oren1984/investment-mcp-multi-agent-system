import os
import streamlit as st

APP_TITLE = "Streamlit UI Skeleton"
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
)

st.title(APP_TITLE)
st.write("This is the base entry point for the Streamlit UI skeleton.")
st.write(f"Backend base URL: {BACKEND_BASE_URL}")