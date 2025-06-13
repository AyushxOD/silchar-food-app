# 🔥 Silchar Foodie: The AI Vibe Analyst

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![spaCy](https://img.shields.io/badge/spaCy-3.7-09A3D5?style=for-the-badge&logo=spacy)](https://spacy.io/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)

An advanced, AI-powered web application built from scratch to analyze and summarize customer reviews for restaurants in Silchar, Assam, revealing their true "vibe."

**[➡️ View the Live Demo Here](https://YOUR_STREAMLIT_APP_URL_HERE)** *(<- Replace with your actual app URL after deploying!)*

---

## 🌟 Key Features

This isn't just another restaurant directory. This application uses a multi-layered AI pipeline to provide deep insights that go far beyond a simple star rating.

* **Dual-Mode Interface:** Seamlessly switch between a "🏆 **Top Suggestions**" mode to discover the best gems and a "🧾 **Full Directory**" mode to search and explore all restaurants.
* **The AI Vibe Engine:** Analyzes thousands of words from customer reviews to tag restaurants with specific, meaningful "vibes" like `✨ Great Ambience`, `👥 Good for Groups`, or `🍚 Biryani Hub`.
* **AI-Generated Summaries:** For restaurants with detailed reviews, the AI reads everything and generates a concise, 2-sentence summary that captures the essence of customer feedback.
* **The Gem Score:** A custom-built algorithm that balances a restaurant's rating with its number of reviews to find true hidden gems, not just the most popular places.
* **Advanced Filtering:** A powerful control panel allows users to filter by rating, number of reviews, and combine multiple "vibe" tags to find the perfect spot for any occasion.
* **Professional "Foodie Magazine" UI:** A custom-designed, fully responsive interface built with injected CSS for a premium user experience.

## 🚀 The Journey: From a "DAAAAMN UNIQUE" Idea to a Deployed AI App

This project was an end-to-end data science marathon. The goal was to create a genuinely unique and powerful tool using real-world, messy data.

### Phase 1: The Data Heist (Advanced Web Scraping)

The first, and most significant, challenge was that no clean dataset for this problem existed. I had to create it from scratch by building a sophisticated, automated scraper using **Python** and **Selenium**.

This process was a brutal gauntlet that required overcoming multiple layers of modern web defenses:

* **The Dynamic Content Wall:** The target website was a Single-Page Application (SPA) where content loads dynamically with JavaScript. The scraper had to be taught to wait intelligently for elements to appear.
* **The CAPTCHA Boss Battle:** The scraper was frequently challenged by "I'm not a robot" tests. I engineered a **"Human-in-the-Loop" (Co-Pilot)** solution, where the script would pause and allow me to solve the CAPTCHA, after which the automation would seamlessly resume.
* **The Gauntlet of Stubborn Elements:** Throughout the process, the scraper faced buttons and panels that were "unclickable" by standard automation. I had to escalate my techniques, finally deploying **advanced `ActionChains` and direct JavaScript clicks** to simulate human mouse movements and force interactions.
* **The Pagination Labyrinth:** The scraper had to be taught to not only loop through items on a page but also correctly find the "Next" button and navigate through dozens of pages without losing its place or getting stuck in a loop—a major bug that I had to meticulously debug and fix.
* **The "Click & Scrape" Pivot:** The final challenge was scraping the review text itself. The solution was a complex interactive workflow where the scraper clicks an item, I click the "Reviews" tab and scroll, and then the scraper takes over to read and save the data. This collaborative approach was key to securing the final dataset.

### Phase 2: The AI Brain (The NLP Pipeline)

With the data secured, I built a multi-stage NLP pipeline to act as the application's brain:

1.  **Deep Cleaning:** I used regular expressions (`re`) to surgically remove all noise from the scraped review text—timestamps, "Local Guide" tags, owner responses, etc.—to ensure the analysis was based purely on customer feedback.
2.  **Lemmatization with spaCy:** I used the industry-standard `spaCy` library to process the text, consolidating words like "tasty" and "taste" into their root form ("taste") to understand the core concepts.
3.  **The Vibe Engine:** I engineered a "Vibe Dictionary" and an algorithm that tags restaurants with vibes (like `💑 Romantic Spot`) only when there is a **strong pattern** (i.e., multiple mentions), not just a single keyword.
4.  **AI Summarizer:** The crown jewel of the project. I built an extractive summarizer that scores every sentence in the reviews based on its keyword density and importance, then selects the top 2-3 sentences to create a concise, AI-generated summary.

### Phase 3: The Grand Finale (UI/UX & Deployment)

The final step was to build a beautiful and functional front-end with **Streamlit**. I injected a large block of custom **CSS** to create a professional "Foodie Magazine" theme with custom fonts, colors, icons, and a responsive card-based layout. The final application, with all its features and modes, was then successfully deployed to the **Streamlit Community Cloud**.

## 🛠️ How to Run Locally

To run this project on your own machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    The project requires a few powerful libraries. Make sure you have your datasets (`silchar_restaurants_CLEAN_FINAL.csv` and `gg_last.csv`) in the folder.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The `requirements.txt` file should contain `streamlit`, `pandas`, `numpy`, `scikit-learn`, and `spacy`)*

4.  **Download the AI language model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

---

This project was an incredible challenge and a demonstration of a full, end-to-end data science workflow. Thank you for checking it out.
