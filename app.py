import pandas as pd
import numpy as np
import streamlit as st
import os
import re
import spacy
import subprocess

# ==================================================================================================
# PAGE CONFIGURATION & STYLING (Your "WOW" Design)
# ==================================================================================================
st.set_page_config(
    page_title="Silchar Foodie 🔥 The Final Cut",
    page_icon="🔥",
    layout="wide"
)

# Your full CSS for the "Foodie Magazine" look.
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
            background-color: #F0F2F6;
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
            font-size: 3.5rem;
            color: white;
            font-weight: 700;
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        /* --- Sidebar Styling --- */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
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
# DEPLOYMENT-OPTIMIZED AI & DATA ENGINE
# ==================================================================================================

@st.cache_resource
def load_spacy_model():
    """Loads the spaCy model and downloads if it's not present."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        with st.spinner("AI Language model not found. Downloading for the first time... (this may take a minute)"):
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

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

# --- ON-DEMAND AI ANALYSIS FUNCTION ---
@st.cache_data # Caches the result for each unique restaurant's review text
def run_ai_analysis_on_demand(review_text):
    """The AI Engine. Runs only when needed on a single block of text."""
    if not isinstance(review_text, str) or nlp is None or not review_text.strip(): 
        return [], "No reviews available for AI analysis."

    text = re.sub(r'Local Guide·.+?photos|photos|review(s)?|\d+ (months|weeks|days|hours) ago|New|See translation \(English\)', '', review_text, flags=re.IGNORECASE)
    text = re.sub(r'[₹₹][0-9,]+–[0-9,]+', '', text)
    text = re.sub(r'\n', ' ', text).strip()
    
    text_lower = text.lower()
    vibes_found = [vibe for vibe, keywords in VIBE_DICTIONARY.items() if sum(text_lower.count(kw) for kw in keywords) >= 2]
            
    doc = nlp(text)
    sentence_scores = {}
    for sentence in doc.sents:
        if len(sentence.text.strip()) < 30 or "thank you" in sentence.text.lower(): continue
        score = sum(1 for token in sentence if token.pos_ in ['NOUN', 'ADJ', 'VERB'] and not token.is_stop)
        if len(sentence) > 1: sentence_scores[sentence.text.strip()] = score / len(sentence)
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:2]
    summary = " ".join(top_sentences)
    
    return vibes_found, summary if summary else "Could not generate a highlight summary."

# --- LEAN DATA LOADING FUNCTION ---
@st.cache_data
def load_base_master_data():
    """Loads and merges data WITHOUT running the heavy AI pipeline on startup."""
    try:
        df_main = pd.read_csv('download.csv')
        df_reviews = pd.read_csv('downloadrev.csv')
    except FileNotFoundError: return None
    
    df_master = pd.merge(df_main, df_reviews[['Name', 'Reviews_Text']], on='Name', how='left')
    df_master['Reviews_Text'] = df_master['Reviews_Text'].fillna("")
    
    df_master['Rating'] = pd.to_numeric(df_master['Rating'], errors='coerce')
    df_master['Reviews'] = pd.to_numeric(df_master['Reviews'], errors='coerce')
    df_master.dropna(subset=['Rating', 'Reviews'], inplace=True)
    df_master['Reviews'] = df_master['Reviews'].astype(int)
    
    df_master['Gem_Score'] = df_master['Rating'] * np.log1p(df_master['Reviews'])
    df_master['Hype_Score'] = df_master['Reviews'] / df_master['Reviews_Text'].str.count('year ago').clip(lower=1)
    df_master['Has_AI_Analysis'] = df_master['Reviews_Text'].str.strip() != ""
    
    return df_master

# ==================================================================================================
# UI COMPONENTS
# ==================================================================================================

def display_restaurant_card(data_row, rank=None):
    """Renders a card, now with on-demand AI analysis inside."""
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
            if data_row['Has_AI_Analysis']:
                # Run the AI engine only when this tab is viewed
                with st.spinner("Running AI Analysis..."):
                    vibes, summary = run_ai_analysis_on_demand(data_row['Reviews_Text'])
                
                st.markdown(f'<div class="summary-box"><p><i class="bi bi-robot"></i> &nbsp;{summary}</p></div>', unsafe_allow_html=True)
                if vibes:
                    st.markdown("**Detected Vibes:**")
                    vibe_html = "".join([f"<span class='vibe-tag'>{vibe}</span>" for vibe in vibes])
                    st.markdown(vibe_html, unsafe_allow_html=True)
            else:
                st.info("No detailed review text was collected for this restaurant.")

        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================================================================
# APP PAGES
# ==================================================================================================

def show_home_dashboard(df):
    st.subheader("Project Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Restaurants Analyzed", f"{len(df)}")
    col2.metric("With AI Review Data", f"{df['Has_AI_Analysis'].sum()} 🔥")
    col3.metric("Average Rating", f"{df['Rating'].mean():.2f} ⭐")
    st.subheader("🏆 Top 10 Restaurants (by Gem Score)")
    st.dataframe(
        df[['Name', 'Rating', 'Reviews', 'Gem_Score']].sort_values('Gem_Score', ascending=False).head(10),
        use_container_width=True,
        column_config={"Gem_Score": st.column_config.ProgressColumn("Gem Score",format="%.2f",min_value=float(df['Gem_Score'].min()),max_value=float(df['Gem_Score'].max()))}
    )

def show_foodie_awards(df):
    st.subheader("🏆 The 2025 Silchar Foodie Awards")
    st.info("Award winners are determined by running AI analysis on restaurants with review data.")
    
    # Run analysis just for the restaurants with reviews to determine winners
    ai_df = df[df['Has_AI_Analysis']].copy()
    if not ai_df.empty:
        award_data = ai_df['Reviews_Text'].apply(run_ai_analysis_on_demand)
        ai_df['Vibes'] = [res[0] for res in award_data]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 👍 Best Service")
            service_df = ai_df[ai_df['Vibes'].apply(lambda v: "👍 Excellent Service" in v)]
            if not service_df.empty: st.success(f"**Winner:** {service_df.sort_values('Rating', ascending=False).iloc[0]['Name']}")
            else: st.warning("Not enough data.")
        with col2:
            st.markdown("#### ✨ Best Ambience")
            ambience_df = ai_df[ai_df['Vibes'].apply(lambda v: "✨ Great Ambience" in v)]
            if not ambience_df.empty: st.success(f"**Winner:** {ambience_df.sort_values('Rating', ascending=False).iloc[0]['Name']}")
            else: st.warning("Not enough data.")

def show_restaurant_explorer(df):
    st.subheader("🧾 Full Restaurant Directory")
    search_query = st.text_input("Search by Name or Address Keyword")
    results = df
    if search_query:
        mask = df['Name'].str.contains(search_query, case=False) | df['Address'].str.contains(search_query, case=False, na=False)
        results = df[mask]
    st.info(f"Showing {len(results)} of {len(df)} total restaurants.")
    for index, row in results.iterrows():
        display_restaurant_card(row)

def show_head_to_head_comparer(df):
    st.subheader("🆚 Head-to-Head Comparison")
    restaurant_list = df['Name'].sort_values().tolist()
    col1, col2 = st.columns(2)
    r1 = col1.selectbox("Choose Restaurant 1", restaurant_list, index=0)
    r2 = col2.selectbox("Choose Restaurant 2", restaurant_list, index=1)
    if r1 and r2 and r1 != r2:
        st.divider()
        data1 = df[df['Name'] == r1].iloc[0]
        data2 = df[df['Name'] == r2].iloc[0]
        with col1: display_restaurant_card(data1)
        with col2: display_restaurant_card(data2)

def show_about_page():
    st.subheader("ℹ️ About This Project")
    # ... (Your about text here) ...

# ==================================================================================================
# MAIN APP EXECUTION
# ==================================================================================================
st.markdown('<div class="header"><h1>Silchar Foodie</h1></div>', unsafe_allow_html=True)
df = load_base_master_data()

if df is None:
    st.error("Data files not found! Ensure 'download.csv' and 'downloadrev.csv' are present.")
else:
    st.sidebar.title("Navigation")
    app_page = st.sidebar.radio("Go to", ('🏠 Home', '🏆 The Foodie Awards', '🗺️ Restaurant Explorer', '🆚 Head-to-Head Compare', 'ℹ️ About'))
    
    if app_page == '🏠 Home': show_home_dashboard(df)
    elif app_page == '🏆 The Foodie Awards': show_foodie_awards(df)
    elif app_page == '🗺️ Restaurant Explorer': show_restaurant_explorer(df)
    elif app_page == '🆚 Head-to-Head Compare': show_head_to_head_comparer(df)
    elif app_page == 'ℹ️ About': show_about_page()