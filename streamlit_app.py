
import streamlit as st
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables (for default API URL)
load_dotenv()
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Oura Data Dashboard", page_icon="💍", layout="wide")

st.title("💍 Oura Ring Data Dashboard")

# --- Sidebar ---
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)

# --- Authentication Section ---
st.header("1. Authentication")

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("Login with Oura"):
        # Open in new tab manually since Streamlit buttons are server-side
        st.markdown(f'<meta http-equiv="refresh" content="0;url={api_url}/auth/login" />', unsafe_allow_html=True)
        st.info("Redirecting to login...")

with col2:
    st.markdown(f"[Or click here to login]({api_url}/auth/login)")

token_input = st.text_input("Enter Access Token (copy from login callback):", type="password")

if "token" not in st.session_state:
    st.session_state.token = ""

if token_input:
    st.session_state.token = token_input
    st.success("Token saved!")

# --- Data Visualization ---

if not st.session_state.token:
    st.warning("Please enter your Access Token to view data.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.header("2. Your Data")

tab1, tab2, tab3, tab4 = st.tabs(["Personal Info", "Sleep", "Activity", "Readiness"])

# --- Personal Info Tab ---
with tab1:
    st.subheader("User Profile")
    if st.button("Fetch Profile"):
        try:
            res = requests.get(f"{api_url}/api/user", headers=headers)
            if res.status_code == 200:
                data = res.json()
                st.json(data)
                
                # Display key metrics
                if isinstance(data, dict):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Age", data.get("age", "N/A"))
                    c2.metric("Weight", f"{data.get('weight', 'N/A')} kg")
                    c3.metric("Height", f"{data.get('height', 'N/A')} m")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- Sleep Tab ---
with tab2:
    st.subheader("Sleep Data")
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Start Date", pd.to_datetime("2023-01-01"))
    end_date = c2.date_input("End Date", pd.to_datetime("2024-01-01"))
    
    if st.button("Fetch Sleep Data"):
        try:
            res = requests.get(
                f"{api_url}/api/sleep", 
                headers=headers, 
                params={"start_date": str(start_date), "end_date": str(end_date)}
            )
            if res.status_code == 200:
                data = res.json()
                if "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    st.write(f"Found {len(df)} records.")
                    
                    # Chart: Sleep Score
                    if "score" in df.columns:
                        st.line_chart(df.set_index("day")["score"], use_container_width=True)
                        st.caption("Daily Sleep Score")
                    
                    # Chart: Sleep Stages
                    # Extract stages if available (structure varies by API version, assuming simplified for now)
                    st.dataframe(df)
                else:
                    st.warning("No data found for this range.")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- Activity Tab ---
with tab3:
    st.subheader("Activity Data")
    if st.button("Fetch Activity Data"):
        try:
            res = requests.get(
                f"{api_url}/api/activity", 
                headers=headers, 
                params={"start_date": str(start_date), "end_date": str(end_date)}
            )
            if res.status_code == 200:
                data = res.json()
                if "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    
                    if "steps" in df.columns:
                        st.bar_chart(df.set_index("day")["steps"])
                        st.caption("Daily Steps")
                    
                    if "score" in df.columns:
                        st.line_chart(df.set_index("day")["score"])
                        st.caption("Activity Score")
                        
                    st.dataframe(df)
                else:
                    st.warning("No data found.")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- Readiness Tab ---
with tab4:
    st.subheader("Readiness Data")
    if st.button("Fetch Readiness Data"):
        try:
            res = requests.get(
                f"{api_url}/api/readiness", 
                headers=headers, 
                params={"start_date": str(start_date), "end_date": str(end_date)}
            )
            if res.status_code == 200:
                data = res.json()
                if "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    
                    if "score" in df.columns:
                        st.line_chart(df.set_index("day")["score"])
                        st.caption("Readiness Score")
                        
                    st.dataframe(df)
                else:
                    st.warning("No data found.")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")
