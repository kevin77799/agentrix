# In agentrix/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
try:
    from pandas import json_normalize
except ImportError:
    from pandas.io.json import json_normalize
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="AgentriX Admin Dashboard",
    page_icon="🌾",
    layout="wide"
)

# --- Database Connection ---
@st.cache_resource
def get_mongo_connection():
    """Establishes a connection to MongoDB."""
    # Try multiple methods to get MongoDB URI
    mongodb_uri = None
    
    # Method 1: Try Streamlit secrets
    try:
        mongodb_uri = st.secrets["mongo"]["MONGODB_URI"]
    except (KeyError, FileNotFoundError):
        pass
    
    # Method 2: Try environment variable
    if not mongodb_uri:
        mongodb_uri = os.getenv('MONGODB_URI')
    
    # Method 3: Try direct from secrets (alternative format)
    if not mongodb_uri:
        try:
            mongodb_uri = st.secrets["MONGODB_URI"]
        except (KeyError, FileNotFoundError):
            pass
    
    # Method 4: Default (will fail, but gives clear error)
    if not mongodb_uri:
        st.error("""
        ⚠️ **MongoDB Connection Not Configured**
        
        Please add your MongoDB connection string to Streamlit Cloud:
        1. Go to your app settings
        2. Click on "Secrets" 
        3. Add this content:
        ```
        MONGODB_URI = "mongodb+srv://kevinsjais_db_user:KBHSF2w9XULSB5H5@agentrix-cluster.7pjtvbc.mongodb.net/"
        ```
        """)
        st.stop()
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        db = client['agentrix_db']
        return db.advisories
    except Exception as e:
        st.error(f"❌ **Database Connection Failed**: {str(e)}")
        st.info("Please check your MongoDB Atlas connection string and network settings.")
        st.stop()

advisory_collection = get_mongo_connection()

# --- Load and Process Data ---
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_data():
    """Loads data from the advisory collection and processes it into a DataFrame."""
    try:
        # Try to get any data (not just status="complete" since we may not have that field)
        data = list(advisory_collection.find().limit(100))  # Limit to prevent memory issues
        
        if not data:
            return pd.DataFrame()

        # Normalize the nested JSON structure
        df = json_normalize(data, sep='_')
        
        # FIX: Convert the MongoDB '_id' column to a string to prevent Arrow errors
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)
        
        # --- Data Cleaning and Feature Engineering ---
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Check if any GPS column exists before processing it
        gps_columns = [col for col in df.columns if 'gps' in col.lower()]
        if gps_columns:
            gps_col = gps_columns[0]  # Use first GPS column found
            def parse_gps(gps_str):
                try:
                    lat, lon = map(float, str(gps_str).split(','))
                    return lat, lon
                except (ValueError, AttributeError):
                    return None, None
                
            df[['latitude', 'longitude']] = df[gps_col].apply(
                lambda x: pd.Series(parse_gps(x))
            )
        else:
            # If no GPS column exists, create empty ones to prevent errors later
            df['latitude'] = None
            df['longitude'] = None
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

df = load_data()

# --- Dashboard UI ---
st.title("🌾 AgentriX Admin Dashboard")
st.markdown("Track trends, disease outbreaks, and farmer activity in real-time.")

if df.empty:
    st.warning("No advisory data found in the database. Please use the main application to generate some data.")
else:
    # --- Key Metrics ---
    total_advisories = len(df)
    
    # Check if disease column exists before counting
    if 'results_disease_prediction_disease' in df.columns:
        disease_detections = int(df['results_disease_prediction_disease'].notna().sum())
    else:
        disease_detections = 0
        
    unique_locations = df.dropna(subset=['latitude', 'longitude']).shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Advisories Generated", f"{total_advisories}")
    col2.metric("Total Disease Detections", f"{disease_detections}")
    col3.metric("Requests with GPS Location", f"{unique_locations}")
    
    st.markdown("---")

    # --- Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Recommended Crops")
        if 'results_recommended_crop' in df.columns:
            crop_counts = df['results_recommended_crop'].value_counts().reset_index()
            crop_counts.columns = ['Crop', 'Count']
            fig_crops = px.bar(
                crop_counts, 
                x='Crop', 
                y='Count', 
                title="Frequency of Recommended Crops",
                color='Crop'
            )
            st.plotly_chart(fig_crops, use_container_width=True)
        else:
            st.info("No crop recommendation data available.")

    with col2:
        st.subheader("Most Common Diseases")
        if 'results_disease_prediction_disease' in df.columns and not df['results_disease_prediction_disease'].isna().all():
            disease_df = df.dropna(subset=['results_disease_prediction_disease'])
            disease_counts = disease_df['results_disease_prediction_disease'].value_counts().reset_index()
            disease_counts.columns = ['Disease', 'Count']
            fig_diseases = px.bar(
                disease_counts.head(10), # Show top 10
                x='Disease', 
                y='Count', 
                title="Frequency of Detected Diseases",
                color='Disease'
            )
            st.plotly_chart(fig_diseases, use_container_width=True)
        else:
            st.info("No disease detections have been recorded yet.")
            
    # --- Map Visualization ---
    st.subheader("Map of Advisory Requests")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        map_df = df.dropna(subset=['latitude', 'longitude'])
        if not map_df.empty:
            st.map(map_df[['latitude', 'longitude']])
        else:
            st.info("No requests with valid GPS coordinates to display.")
    else:
        st.info("No GPS data available to display on map.")

    # --- Raw Data View ---
    st.subheader("Raw Advisory Data")
    st.dataframe(df)