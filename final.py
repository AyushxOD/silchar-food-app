import pandas as pd
import numpy as np
import streamlit as st
import os
import re
import spacy

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Silchar Foodie 🔥 Final Version",
    page_icon="🔥",
    layout="wide"
)

# --- NLP ENGINE & DATA LOADING (The most robust version) ---
@st.cache_resource
def load_spacy_model():
    """Loads the spaCy model once and caches it."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error("SpaCy language model not found. To enable AI features, please run this in your terminal: python -m spacy download en_core_web_sm")
        return None
nlp = load_spacy_model()

VIBE_DICTIONARY = {
    "✨ Great Ambience": ["ambience", "atmosphere", "decor", "interior", "view", "vibe"],
    "👍 Excellent Service": ["service", "staff", "owner", "friendly", "welcoming", "hospitable", "polite", "behavior"],
    "👥 Good for Groups": ["friends", "family", "group", "gathering", "party", "celebration"],
    "💑 Romantic Spot": ["date", "romantic", "couple", "cozy", "intimate"],
    "💸 Budget-Friendly": ["cheap", "affordable", "value", "price", "reasonable", "economic"],
    "🍗 Meat Lover's Choice": ["chicken", "mutton", "fish", "kebab", "non-veg", "tandoori"],
    "🍚 Biryani Hub": ["biryani", "briyani", "hyderabadi"],
    "☕ Cafe & Quick Bites": ["cafe", "coffee", "snacks", "bakery", "mocktail"],
    "🌿 Veggie Paradise": ["vegetarian", "veg", "vegan", "paneer", "thali", "plant-based", "pure veg", "shakahaar", "veg thali"],
    "🍹 Drinks & Mocktails": ["mocktail", "cocktail", "beverage", "drink", "refreshing"],
    "🍰 Desserts & Sweets": ["dessert", "sweet", "ice cream", "pastry", "cake", "pudding", "gulab jamun", "rasgulla"],
    "🌶️ Spicy & Flavorful": ["spicy", "flavorful", "tasty", "delicious", "mouthwatering", "zesty"],
    "🍽️ Diverse Cuisine": ["cuisine", "variety", "menu", "options", "international", "fusion"],
    "🌟 Hidden Gem": ["hidden gem", "secret", "underrated", "local favorite", "off the beaten path"],
    "🍕 Pizza & Fast Food": ["pizza", "burger", "fast food", "snacks", "quick bites", "fries"],
    "🍜 Noodles & Chinese": ["noodles", "chinese", "manchurian", "spring roll", "dimsum", "chowmein"],
    "🍛 Indian Classics": ["indian", "curry", "dal", "roti", "naan", "chapati", "paratha"],
    "🍣 Sushi & Japanese": ["sushi", "japanese", "ramen", "tempura", "sashimi"],

    "🎉 Party & Celebration": ["party", "celebration", "event", "birthday", "anniversary", "get-together"],
    "🌍 International Flavors": ["international", "global", "world cuisine", "fusion", "exotic"],
    "🍳 Breakfast & Brunch": ["breakfast", "brunch", "eggs", "pancakes", "waffles", "toast"],
    "🍔 Street Food Vibes": ["street food", "chaat", "pani puri", "bhel puri", "vada pav", "pav bhaji"],
    "🍖 Barbecue & Grill": ["barbecue", "grill", "tandoor", "smoked", "charcoal", "roasted"]
    
}

@st.cache_data
def analyze_restaurant(text):
    """Analyzes a single block of review text."""
    if not isinstance(text, str) or nlp is None or not text.strip(): 
        return [], "No review text to analyze."
    
    # Vibe Analysis with Confidence Threshold
    vibes_found = []
    text_lower = text.lower()
    for vibe, keywords in VIBE_DICTIONARY.items():
        mention_count = sum(text_lower.count(keyword) for keyword in keywords)
        if mention_count >= 3:
            vibes_found.append(vibe)
            
    # AI Extractive Summarization
    doc = nlp(text)
    sentence_scores = {}
    for sentence in doc.sents:
        if len(sentence.text.strip()) < 30 or "thank you" in sentence.text.lower():
            continue
        score = sum(1 for token in sentence if token.pos_ in ['NOUN', 'ADJ', 'VERB'] and not token.is_stop)
        if len(sentence) > 1:
            sentence_scores[sentence.text.strip()] = score / len(sentence)
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:2]
    summary = " ".join(top_sentences)
    
    return vibes_found, summary if summary else "Could not generate a highlight summary."

@st.cache_data
def load_and_process_data():
    """Loads, merges, and processes all data sources."""
    try:
        df_main = pd.read_csv('download.csv')
        df_reviews = pd.read_csv('downloadrev.csv')
    except FileNotFoundError: return None
    
    df_master = pd.merge(df_main, df_reviews[['Name', 'Reviews_Text']], on='Name', how='left')
    
    # Fix for FutureWarning and ensures column exists
    df_master['Reviews_Text'] = df_master['Reviews_Text'].fillna("")
    
    df_master.dropna(subset=['Rating', 'Reviews'], inplace=True)
    df_master['Reviews'] = df_master['Reviews'].astype(int)
    df_master['Gem_Score'] = df_master['Rating'] * np.log1p(df_master['Reviews'])
    
    # --- BUG FIX: Create all new columns on the main dataframe ---
    analysis_results = df_master['Reviews_Text'].apply(lambda text: analyze_restaurant(text))
    df_master['Vibes'] = [res[0] for res in analysis_results]
    df_master['AI_Summary'] = [res[1] for res in analysis_results]
    df_master['Has_AI_Analysis'] = df_master['Reviews_Text'].str.strip() != ""
    
    return df_master

# Reusable display function
def display_restaurant_details(data_row):
    tab1, tab2 = st.tabs(["✨ Overview", "🤖 AI Analysis"])
    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("⭐ Rating", f"{data_row['Rating']}/5")
        col2.metric("📝 Reviews", f"{int(data_row['Reviews']):,}")
        col3.metric("💎 Gem Score", f"{data_row['Gem_Score']:.2f}")
        if pd.notna(data_row['Address']): st.info(f"**Address:** {data_row['Address']}")
    with tab2:
        if data_row['Has_AI_Analysis']:
            st.markdown("**🤖 AI-Generated Summary:**")
            st.success(f"🗣️ *{data_row['AI_Summary']}*")
            st.markdown("---")
            if data_row['Vibes']:
                st.markdown("**Detected Vibes (Based on multiple mentions):**")
                keywords_html = "".join([f"<span style='background-color: #333; color: #eee; border-radius: 5px; padding: 5px 8px; margin: 3px; display: inline-block;'>{vibe}</span>" for vibe in data_row['Vibes']])
                st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.write("No detailed review text was collected for this restaurant.")

# --- MAIN APP LAYOUT ---
st.title('🔥 Silchar Foodie: The Definitive Edition')
df = load_and_process_data()

if df is None:
    st.error("Data files not found! Ensure 'silchar_restaurants_CLEAN_FINAL.csv' and 'gg_last.csv' are present.")
else:
    st.sidebar.title("Control Panel")
    app_mode = st.sidebar.radio("Choose App Mode", ('🏆 Top Suggestions', '🧾 Full Directory'))

    if app_mode == '🏆 Top Suggestions':
        st.sidebar.header("Find the Best Gems ✨")
        prioritize_ai = st.sidebar.checkbox("Prioritize results with AI Analysis 🔥", value=True)
        rating_filter = st.sidebar.slider('Minimum Rating', 1.0, 5.0, 3.5, 0.1)
        reviews_filter = st.sidebar.slider('Minimum Number of Reviews', 0, 1000, 10, 5)
        stops_filter = st.sidebar.number_input('Number of Suggestions to Show', 1, 20, 5)
        
        filtered_df = df[(df['Rating'] >= rating_filter) & (df['Reviews'] >= reviews_filter)]
        
        if prioritize_ai:
            final_suggestions = filtered_df.sort_values(by=['Has_AI_Analysis', 'Gem_Score'], ascending=[False, False]).head(stops_filter)
        else:
            final_suggestions = filtered_df.sort_values(by='Gem_Score', ascending=False).head(stops_filter)

        st.header(f"Our Top {len(final_suggestions)} AI-Analyzed Suggestions")
        st.divider()

        if final_suggestions.empty: st.warning("No restaurants match your criteria.")
        else:
            for i, (index, data) in enumerate(final_suggestions.iterrows()):
                title = f"#{i+1}: {data['Name']}"
                if data['Has_AI_Analysis']: title += " 🔥"
                st.subheader(title)
                display_restaurant_details(data)
    
    else: # Directory Mode
        st.sidebar.header("Search the Directory 🧾")
        search_query = st.sidebar.text_input("Search by Name or Address Keyword")
        if search_query:
            mask = df['Name'].str.contains(search_query, case=False) | df['Address'].str.contains(search_query, case=False, na=False)
            results = df[mask]
        else:
            results = df.sort_values('Name')
            
        st.header(f"Found {len(results)} Restaurants")
        st.divider()
        for index, row in results.iterrows():
            title = row['Name']
            if row['Has_AI_Analysis']: title += " 🔥"
            with st.expander(f"{title} (⭐ {row['Rating']})"):
                display_restaurant_details(row)