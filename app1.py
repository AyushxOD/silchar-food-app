import pandas as pd
import numpy as np
import streamlit as st
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Silchar Foodie",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA LOADING & FEATURE ENGINEERING ---
@st.cache_data # Cache the data for better performance
def load_data():
    file_path = 'download.csv'
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    df.dropna(subset=['Name', 'Rating', 'Reviews'], inplace=True)
    
    # --- Calculate the "Gem Score" ---
    # This score balances high ratings with the number of reviews
    # The log ensures that a 5-star from 50 reviews is more of a "gem" than a 4.6 from 2000 reviews
    df['Gem_Score'] = df['Rating'] * np.log1p(df['Reviews'])
    
    return df

df = load_data()

# --- STYLING (Optional, but makes it look better) ---
st.markdown("""
    <style>
    .stMetric {
        border: 1px solid #2e2e2e;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .stSubheader {
        border-bottom: 2px solid #2e2e2e;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title('🏆 Silchar Foodie')
st.markdown("Your ultimate guide to discovering the best and most unique restaurants in Silchar, powered by data.")
st.divider()

# --- SIDEBAR / CONTROL PANEL ---
st.sidebar.title("Control Panel")
app_mode = st.sidebar.radio(
    "Choose Your Mode",
    ('🏆 Top Suggestions', '-  All Restaurants (Directory)')
)

if df is None:
    st.error("FATAL ERROR: The data file 'silchar_restaurants_CLEAN_FINAL.csv' was not found! Please run the final scraper first.")
else:
    if app_mode == '🏆 Top Suggestions':
        # --- TOP SUGGESTIONS MODE ---
        st.sidebar.header("Find the Best Gems ✨")
        
        rating_filter = st.sidebar.slider('Minimum Rating', 1.0, 5.0, 4.0, 0.1)
        reviews_filter = st.sidebar.slider('Minimum Number of Reviews', 0, 500, 20, 5)
        stops_filter = st.sidebar.number_input('Number of Suggestions to Show', 1, 20, 5)
        
        # --- Filtering Logic ---
        filtered_df = df[(df['Rating'] >= rating_filter) & (df['Reviews'] >= reviews_filter)]
        # Sort by the Gem Score to find the top suggestions
        top_suggestions = filtered_df.sort_values(by='Gem_Score', ascending=False).head(stops_filter)

        st.header(f"Our Top {len(top_suggestions)} Suggestions For You")

        if top_suggestions.empty:
            st.warning("No restaurants match your criteria. Try loosening the filters!")
        else:
            for i, row in enumerate(top_suggestions.iterrows()):
                index, data = row
                st.subheader(f"#{i+1}: {data['Name']}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("⭐ Rating", f"{data['Rating']}/5")
                col2.metric("📝 Reviews", f"{int(data['Reviews']):,}")
                col3.metric("💎 Gem Score", f"{data['Gem_Score']:.2f}")
                
                if pd.notna(data['Address']):
                    st.info(f"**Address:** {data['Address']}")
                st.divider()

    elif app_mode == '-  All Restaurants (Directory)':
        # --- DIRECTORY MODE ---
        st.sidebar.header("Search the Directory 🧾")
        search_query = st.sidebar.text_input("Search by Name or Address Keyword")

        # --- Filtering Logic ---
        if search_query:
            mask = df['Name'].str.contains(search_query, case=False) | \
                   df['Address'].str.contains(search_query, case=False, na=False)
            search_results = df[mask]
        else:
            search_results = df.sort_values(by='Name') # Show all, sorted alphabetically

        st.header(f"Found {len(search_results)} Restaurants")
        
        for index, row in search_results.iterrows():
            with st.container():
                st.subheader(row['Name'])
                if pd.notna(row['Address']):
                    st.write(f"**Address:** {row['Address']}")
                col1, col2 = st.columns(2)
                col1.metric("⭐ Rating", f"{row['Rating']:.1f}/5" if pd.notna(row['Rating']) else "N/A")
                col2.metric("📝 Reviews", f"{int(row['Reviews']):,}" if pd.notna(row['Reviews']) else "N/A")
                st.divider()