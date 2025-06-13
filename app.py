import pandas as pd
import numpy as np
import streamlit as st
import os
import re
import spacy
from collections import Counter
import subprocess

# ==================================================================================================
# PAGE CONFIGURATION & STYLING (The "WOW" Design)
# ==================================================================================================
st.set_page_config(
    page_title="Silchar Foodie 🔥 The Final Cut",
    page_icon="🔥",
    layout="wide"
)

# This is a significant block of CSS to achieve the professional "Food Magazine" look.
st.markdown("""
    <style>
        /* --- Font Imports --- */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap');
        @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");

        /* --- Main App Theme --- */
        html, body, [class*="st-"] {
            font-family: 'Lato', sans-serif;
        }
        .stApp {
            background-color: #0000;
        }

        /* --- Custom Header --- */
        .header {
            background-image: linear-gradient(to right, #d31027, #ea384d);
            
            padding: 2.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .header h1 {
            font-family: 'Playfair Display', serif;
            backgrouund-color: rgba(255, 255, 255, 0.1);
            font-size: 3.5rem;
            color: white;
            font-weight: 700;
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        /* --- Sidebar Styling --- */
        [data-testid="stSidebar"] {
            background-color: #darkgray;
            color: #333;
            font-family: 'Lato', sans-serif;
            border-right: 1px solid #E0E0E0;
        }
        .st-emotion-cache-1629p8f h1 {
             font-family: 'Playfair Display', serif;
             font-size: 1.8rem;
             color: #1E1E1E;
        }

        /* --- Restaurant Card Design --- */
        .restaurant-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #EAEAEA;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: all 0.3s ease-in-out;
        }
        .restaurant-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            border-left: 5px solid #d31027;
        }

        /* --- Vibe Tags --- */
        .vibe-tag {
            background-color: #f0f2f6;
            color: #333;
            border-radius: 15px;
            padding: 6px 14px;
            margin: 4px;
            display: inline-block;
            font-size: 0.9rem;
            font-weight: 700;
        }
        
        /* --- AI Summary Box --- */
        .summary-box {
            background-color: #FFFBEA;
            border-left: 4px solid #F59E0B;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            font-style: italic;
            color: #57534E;
        }

    </style>
""", unsafe_allow_html=True)


# ==================================================================================================
# AI & DATA ENGINE (The "FIRE" Brains)
# ==================================================================================================

# --- NLP Model Loading ---
@st.cache_resource
def load_spacy_model():
    """
    Loads the spaCy model. If not found, it triggers a download for the
    Streamlit Cloud environment.
    """
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.warning("AI Language model not found. Downloading for the first time... (this may take a minute)")
        # Run the download command
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")
nlp = load_spacy_model()

# --- Vibe Dictionary ---
VIBE_DICTIONARY = {
    "✨ Great Ambience": ["ambience", "atmosphere", "decor", "interior", "view", "vibe"],
    "👍 Excellent Service": ["service", "staff", "owner", "friendly", "welcoming", "hospitable", "polite", "behavior"],
    "👥 Good for Groups": ["friends", "family", "group", "gathering", "party", "celebration"],
    "💑 Romantic Spot": ["date", "romantic", "couple", "cozy", "intimate"],
    "💸 Budget-Friendly": ["cheap", "affordable", "value", "price", "reasonable", "economic"],
    "🍗 Meat Lover's Choice": ["chicken", "mutton", "fish", "kebab", "non-veg", "tandoori"],
    "🍚 Biryani Hub": ["biryani", "briyani", "hyderabadi"],
    "☕ Cafe & Quick Bites": ["cafe", "coffee", "snacks", "bakery", "mocktail"]
}

@st.cache_data
def analyze_restaurant_data(row):
    """The final AI engine: performs deep cleaning, vibe analysis, and summarization."""
    text = row['Reviews_Text']
    if not isinstance(text, str) or nlp is None or not text.strip(): 
        return [], "No reviews available for AI analysis."

    # 1. Deep Cleaning
    text = re.sub(r'Local Guide·.+?photos|photos|review(s)?|\d+ (months|weeks|days|hours) ago|New|See translation \(English\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[₹₹][0-9,]+–[0-9,]+', '', text)
    text = re.sub(r'\n', ' ', text).strip()
    
    # 2. Vibe Analysis with Confidence Threshold
    text_lower = text.lower()
    vibes_found = [vibe for vibe, keywords in VIBE_DICTIONARY.items() if sum(text_lower.count(kw) for kw in keywords) >= 2]
            
    # 3. AI Extractive Summarization
    doc = nlp(text)
    sentence_scores = {}
    for sentence in doc.sents:
        if len(sentence.text.strip()) < 30 or "thank you" in sentence.text.lower() or "your feedback" in sentence.text.lower():
            continue
        score = sum(1 for token in sentence if token.pos_ in ['NOUN', 'ADJ', 'VERB'] and not token.is_stop)
        if len(sentence) > 1:
            sentence_scores[sentence.text.strip()] = score / len(sentence)
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:2]
    summary = " ".join(top_sentences)
    
    return vibes_found, summary if summary else "Could not generate a highlight summary from available reviews."

@st.cache_data
def load_and_process_master_data():
    """Loads, merges, cleans, and analyzes all data sources."""
    try:
        df_main = pd.read_csv('download.csv')
        df_reviews = pd.read_csv('downloadrev.csv')
    except FileNotFoundError: return None
    
    df_master = pd.merge(df_main, df_reviews[['Name', 'Reviews_Text']], on='Name', how='left')
    df_master['Reviews_Text'] = df_master['Reviews_Text'].fillna("")
    # --- THIS IS THE FIX ---
    # Convert 'Rating' to a number, coercing any errors
    df_master['Rating'] = pd.to_numeric(df_master['Rating'], errors='coerce')
    # Convert 'Reviews' to a number
    df_master['Reviews'] = pd.to_numeric(df_master['Reviews'], errors='coerce')

    # Now, drop any rows where the conversion might have failed
    df_master.dropna(subset=['Rating', 'Reviews'], inplace=True)
    df_master['Reviews'] = df_master['Reviews'].astype(int)
    # --- END OF FIX ---
    # --- Feature Engineering: Gem Score & Hype Score ---
    df_master['Gem_Score'] = df_master['Rating'] * np.log1p(df_master['Reviews'])
    # Hype Score is higher for places with more recent reviews (a simple heuristic)
    df_master['Hype_Score'] = df_master['Reviews'] / df_master['Reviews_Text'].str.count('year ago').clip(lower=1)
    
    df_master['Has_AI_Analysis'] = df_master['Reviews_Text'].str.strip() != ""
    
    # Apply the full AI pipeline
    analysis_results = df_master.apply(analyze_restaurant_data, axis=1)
    df_master['Vibes'] = [res[0] for res in analysis_results]
    df_master['AI_Summary'] = [res[1] for res in analysis_results]
    
    return df_master

# ==================================================================================================
# UI COMPONENTS (Reusable parts of the app)
# ==================================================================================================

def display_restaurant_card(data_row, rank=None):
    """Renders a single restaurant's info in a beautiful card format."""
    with st.container():
        st.markdown('<div class="restaurant-card">', unsafe_allow_html=True)
        
        title = f"#{rank}: {data_row['Name']}" if rank else data_row['Name']
        if data_row['Has_AI_Analysis']: title += " 🔥"
        st.subheader(title)
        
        tab1, tab2 = st.tabs(["✨ Overview", "🤖 AI Analysis"])
        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("⭐ Rating", f"{data_row['Rating']}/5")
            col2.metric("📝 Reviews", f"{int(data_row['Reviews']):,}")
            col3.metric("💎 Gem Score", f"{data_row['Gem_Score']:.2f}")
            if pd.notna(data_row['Address']):
                st.markdown(f'<div class="address-box"><p><i class="bi bi-geo-alt-fill"></i> &nbsp;{data_row["Address"]}</p></div>', unsafe_allow_html=True)
        with tab2:
            st.markdown(f'<div class="summary-box"><p><i class="bi bi-robot"></i> &nbsp;{data_row["AI_Summary"]}</p></div>', unsafe_allow_html=True)
            if data_row['Vibes']:
                st.markdown("**Detected Vibes:**")
                vibe_html = "".join([f"<span class='vibe-tag'>{vibe}</span>" for vibe in data_row['Vibes']])
                st.markdown(vibe_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================================================================
# APP PAGES (The main logic for each view)
# ==================================================================================================

def show_home_dashboard(df):
    """Displays the main dashboard with summary stats."""
    st.subheader("Project Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Restaurants Analyzed", f"{len(df)}")
    col2.metric("Restaurants with AI Vibe Analysis", f"{df['Has_AI_Analysis'].sum()} 🔥")
    col3.metric("Average Rating", f"{df['Rating'].mean():.2f} ⭐")
    
    st.subheader("🏆 Top 10 Restaurants (by Gem Score)")
    # --- THIS IS THE FIX ---
    # We now sort by 'Gem_Score' and also display it for transparency.
    st.dataframe(
        df[['Name', 'Rating', 'Reviews', 'Gem_Score']].sort_values('Gem_Score', ascending=False).head(10),
        column_config={
            "Gem_Score": st.column_config.ProgressColumn(
                "Gem Score (Higher is Better)",
                format="%.2f",
                min_value=float(df['Gem_Score'].min()),
                max_value=float(df['Gem_Score'].max()),
            ),
        }
    )
def show_foodie_awards(df):
    """Displays winners in different categories."""
    st.subheader("🏆 The 2025 Silchar Foodie Awards")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 💎 Top Gem Score")
        top_gem = df.loc[df['Gem_Score'].idxmax()]
        st.success(f"**Winner:** {top_gem['Name']} (Score: {top_gem['Gem_Score']:.2f})")
        
        st.markdown("#### 👍 Best Service")
        service_df = df[df['Vibes'].apply(lambda v: "👍 Excellent Service" in v)]
        if not service_df.empty:
            st.success(f"**Winner:** {service_df.iloc[0]['Name']}")
        else:
            st.warning("Not enough data for this category.")

    with col2:
        st.markdown("#### ✨ Best Ambience")
        ambience_df = df[df['Vibes'].apply(lambda v: "✨ Great Ambience" in v)]
        if not ambience_df.empty:
            st.success(f"**Winner:** {ambience_df.iloc[0]['Name']}")
        else:
            st.warning("Not enough data for this category.")

        st.markdown("#### 💸 Best Value")
        value_df = df[df['Vibes'].apply(lambda v: "💸 Budget-Friendly" in v)]
        if not value_df.empty:
            st.success(f"**Winner:** {value_df.iloc[0]['Name']}")
        else:
            st.warning("Not enough data for this category.")

def show_restaurant_explorer(df):
    """The full, searchable directory."""
    st.subheader("🧾 Full Restaurant Directory")
    
    search_query = st.text_input("Search by Name or Address Keyword")
    if search_query:
        mask = df['Name'].str.contains(search_query, case=False) | df['Address'].str.contains(search_query, case=False, na=False)
        results = df[mask]
    else:
        results = df.sort_values('Name')
        
    st.info(f"Showing {len(results)} of {len(df)} total restaurants.")
    
    for index, row in results.iterrows():
        display_restaurant_card(row)

def show_head_to_head_comparer(df):
    """A new feature to compare two restaurants."""
    st.subheader("🆚 Head-to-Head Comparison")
    
    restaurant_list = df['Name'].sort_values().tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        r1 = st.selectbox("Choose Restaurant 1", restaurant_list, index=0)
    with col2:
        r2 = st.selectbox("Choose Restaurant 2", restaurant_list, index=1)
        
    if r1 and r2:
        st.divider()
        data1 = df[df['Name'] == r1].iloc[0]
        data2 = df[df['Name'] == r2].iloc[0]
        
        with col1:
            display_restaurant_card(data1)
        with col2:
            display_restaurant_card(data2)
            
def show_about_page():
    """An 'About' page explaining the project."""
    st.subheader("ℹ️ About This Project")
    st.markdown("""
    This application is the result of an intensive, end-to-end data science project. It was built to demonstrate the maximum possible potential from a custom-collected dataset.
    
    **Key Technologies Used:**
    - **Data Collection:** A custom-built Python scraper using **Selenium** to navigate dynamic web pages, handle CAPTCHAs, click buttons, and extract text data.
    - **Data Processing:** The **Pandas** library was used to clean, merge, and structure the scraped data.
    - **AI & NLP:** The **spaCy** library powers the advanced natural language processing. The AI engine performs:
        - **Deep Text Cleaning** to remove noise.
        - **Vibe Analysis** using a data-driven dictionary with a confidence threshold.
        - **AI Summarization** using an extractive technique based on sentence scoring.
    - **Web Application:** Built with **Streamlit**, featuring a multi-page design, custom CSS for a professional look, and multiple interactive components.
    
    This project was a true collaboration, evolving through many stages of debugging and feature enhancement.
    """)

# ==================================================================================================
# MAIN APP EXECUTION
# ==================================================================================================

# --- Header ---
st.markdown('<div class="header"><h1>Silchar Foodie</h1></div>', unsafe_allow_html=True)
df = load_and_process_master_data()

if df is None:
    st.error("Data files not found! Ensure 'silchar_restaurants_CLEAN_FINAL.csv' and 'gg_last.csv' are present.")
else:
    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    app_page = st.sidebar.radio(
        "Go to",
        ('🏠 Home', '🏆 The Foodie Awards', '🗺️ Restaurant Explorer', '🆚 Head-to-Head Compare', 'ℹ️ About')
    )
    
    # --- Page Routing ---
    if app_page == '🏠 Home':
        show_home_dashboard(df)
    elif app_page == '🏆 The Foodie Awards':
        show_foodie_awards(df)
    elif app_page == '🗺️ Restaurant Explorer':
        show_restaurant_explorer(df)
    elif app_page == '🆚 Head-to-Head Compare':
        show_head_to_head_comparer(df)
    elif app_page == 'ℹ️ About':
        show_about_page()