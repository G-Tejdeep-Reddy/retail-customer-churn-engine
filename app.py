import streamlit as st
import pandas as pd
from scripts.db_loader import load_customer_segments

# Page configuration
st.set_page_config(page_title="Retail Churn & RFM Dashboard", layout="wide", page_icon="🛍️")

st.title("🛍️ Retail Customer Churn & RFM Segmentation Engine")
st.markdown("Interactive control tower analyzing customer lifetime value, retention risk, and RFM segments.")

# Load data using your Python function
@st.cache_data
def get_data():
    return load_customer_segments()

df = get_data()

# --- SIDE-BY-SIDE FILTERS ---
st.sidebar.header("🔍 Dashboard Filters")

# Country Filter
countries = ["All"] + sorted(df['country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Filter by Country", countries)

# Segment Filter
segments = ["All"] + sorted(df['customer_segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Filter by Customer Segment", segments)

# Apply Filters
filtered_df = df.copy()
if selected_country != "All":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]
if selected_segment != "All":
    filtered_df = filtered_df[filtered_df['customer_segment'] == selected_segment]

# --- QUICK METRICS ROW (Reflects filtered data) ---
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(filtered_df):,}")
col2.metric("Total Revenue", f"${filtered_df['monetary_value'].sum():,.2f}")
col3.metric("Avg Recency (Days)", f"{filtered_df['recency_days'].mean():.1f}" if not filtered_df.empty else "0")
col4.metric("Avg Frequency", f"{filtered_df['frequency'].mean():.1f}" if not filtered_df.empty else "0")

st.divider()

# --- DATA TABLE & BREAKDOWN ---
st.subheader(f"Customer Records ({len(filtered_df):,})")
st.dataframe(filtered_df, width='stretch')