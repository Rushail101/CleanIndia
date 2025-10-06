import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import numpy as np
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
import json
import csv
from PIL import Image
import io
from supabase import create_client, Client
import base64
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def Clean_India():
    st.title("Clean India!")
    st.subheader("Share your civic issues with us and help us make India cleaner and better!")

    # Connect to Supabase (requires SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml)
    conn = st.connection("supabase", type=SupabaseConnection)

    # Fetch existing data (optional — can comment this out)
    try:
        rows = client.table("cleanindia").select("*").execute()
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    # ---- User Inputs ----
    Photo = st.file_uploader("Upload a picture of the area you want to get fixed.", type=['png', 'jpg', 'jpeg'])
    bytes_data = None
    if Photo is not None:
        bytes_data = Photo.getvalue()
        st.image(bytes_data, caption='Uploaded Image.', width=300)
        st.success("Image uploaded successfully!")

    state = st.selectbox("Select your state", [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
        "Ladakh", "Lakshadweep", "Puducherry"
    ])

    pincode = st.text_input("Area Pincode")
    issue = st.multiselect("Select the issue you want to report",options=[
        "Garbage Dumping", "Water Logging", "Road Damage", "Street Light Issue", "Pollution",
        "Public Toilet Issue", "Traffic Signal Issue", "Other"])

    # Optional location fetching
    latitude, longitude = None, None
    if st.checkbox("Get my location (Click on it twice if it doesn't work the first time)"):
        loc = get_geolocation()
        latitude, longitude = loc['coords']['latitude'], loc['coords']['longitude']
        st.write(f"Your coordinates are ({latitude}, {longitude})")
        st.map(pd.DataFrame({'lat': [latitude], 'lon': [longitude]}))

    # ---- Submit Button ----
    if st.button("Submit"):
        if not pincode or not issue:
            st.warning("Please fill all the required fields.")
            return

        try:
            # Convert image bytes to base64 (so it can be stored as text)
            image_base64 = base64.b64encode(bytes_data).decode("utf-8") if bytes_data else None

            data = {
                "state": state,
                "pincode": pincode,
                "issue": issue,
                "photo": image_base64,
                "latitude": latitude,
                "longitude": longitude
            }

            # Insert data into Supabase
            response = client.table("cleanindia").insert(data).execute()

            if hasattr(response, "data") and response.data:
                st.success("✅ Thank you for reporting the issue! Your report has been submitted successfully.")
            else:
                st.warning("⚠️ Data submission might have failed. Please check your Supabase configuration.")

        except Exception as e:
            st.error(f"Error submitting data: {e}")




import streamlit as st
import base64
from io import BytesIO
from PIL import Image

def All_Complaints():
    st.title("🧾 All Complaints")
    st.subheader("List of all issues reported by citizens")

    # Connect to Supabase
    conn = st.connection("supabase", type=SupabaseConnection)

    try:
        response = client.table("cleanindia").select("*").execute()
        rows = response.data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return

    if not rows:
        st.warning("No data found in the 'cleanindia' table.")
        return

    # Display each complaint in a card-like format
    for row in rows:
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([1, 2])

            # ---- Left: Show Photo if exists ----
            with col1:
                if row.get("photo"):
                    try:
                        img_bytes = base64.b64decode(row["photo"])
                        image = Image.open(BytesIO(img_bytes))
                        st.image(image, caption="Reported Area", use_container_width=True)
                    except Exception:
                        st.warning("Could not load image.")
                else:
                    st.info("No photo uploaded.")

            # ---- Right: Show Details ----
            with col2:
                st.markdown(f"### 🏙️ {row.get('state', 'Unknown State')}")
                st.markdown(f"**📍 Pincode:** {row.get('pincode', 'N/A')}")
                st.markdown(f"**📝 Issue:** {row.get('issue', 'N/A')}")
                st.markdown(f" Latitude: {row.get('latitude', 'N/A')}")
                st.markdown(f" Longitude: {row.get('longitude', 'N/A')}")
                if row.get("Latitude") and row.get("longitude"):
                    st.markdown(f"**📡 Location:** ({row['latitude']}, {row['longitude']})")

    st.markdown("---")
    st.success(f"✅ Total Complaints Displayed: {len(rows)}")


pg = st.navigation([Clean_India,All_Complaints], position="sidebar")
pg.run()


