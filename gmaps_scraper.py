import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_everything_definitively():
    """
    The definitive scraper. It handles CAPTCHA, clicks "More places",
    and loops through all pages using the confirmed ID "pnnext".
    """
    print("Setting up Selenium WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    url = f"https://www.google.com/search?q=restaurants+in+Silchar+Assam"
    driver.get(url)

    print("\nACTION REQUIRED: Please solve the CAPTCHA.")
    input("After you see the initial list, press Enter to continue...")

    wait = WebDriverWait(driver, 10)
    try:
        print("Looking for the 'More places' button...")
        more_places_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'More places')))
        more_places_button.click()
        print("Button clicked! Waiting for the full list...")
        time.sleep(5)
    except Exception:
        print("Could not find or click 'More places'.")

    restaurant_data = []
    scraped_names = set()
    page_number = 1

    while True:
        print(f"\n--- Scraping Page {page_number} ---")
        
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'uMdZh')))
            restaurant_containers = driver.find_elements(By.CLASS_NAME, 'uMdZh')
            print(f"Found {len(restaurant_containers)} results on this page.")

            for container in restaurant_containers:
                name = "Not found"
                try:
                    name = container.find_element(By.CLASS_NAME, 'OSrXXb').text
                    if name in scraped_names:
                        continue
                    scraped_names.add(name)
                except Exception: continue

                # ... (Parsing logic is the same) ...
                rating, reviews, address = "Not found", "Not found", "Not found"
                try: rating = container.find_element(By.CLASS_NAME, 'yi40Hd').text
                except Exception: pass
                try: reviews = container.find_element(By.CLASS_NAME, 'RDApEe').text
                except Exception: pass
                try:
                    details = container.find_element(By.CLASS_NAME, 'rllt__details').text.split('\n')
                    address = details[-1] if len(details) > 2 else details[0]
                except Exception: pass
                
                print(f"✔️ Parsed: {name}")
                restaurant_data.append({ "Name": name, "Rating": rating, "Reviews": reviews, "Address": address })
        except Exception as e:
            print(f"An error occurred while scraping page {page_number}: {e}")

        # --- FIND AND CLICK 'NEXT' USING THE CONFIRMED ID ---
        try:
            print("Looking for the 'Next' page button using its unique ID: 'pnnext'...")
            next_button = wait.until(EC.element_to_be_clickable((By.ID, 'pnnext')))
            
            # This little javascript trick can help ensure the button is clickable
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            
            next_button.click()
            page_number += 1
            print("SUCCESS: Navigating to the next page...")
            time.sleep(3) # Wait for next page to load
        except Exception:
            print("No more 'Next' button found. We've scraped all pages!")
            break

    print("\n" + "="*50)
    print("Closing browser...")
    driver.quit()

    if not restaurant_data: return None
    return pd.DataFrame(restaurant_data)

if __name__ == '__main__':
    restaurant_df = scrape_everything_definitively()
    if restaurant_df is not None:
        print("\n\n--- DEFINITIVE SCRAPING COMPLETE ---")
        print(f"Successfully scraped a total of {len(restaurant_df)} unique restaurants across all pages.")
        
        # Data cleaning
        restaurant_df['Reviews'] = restaurant_df['Reviews'].str.replace(r'[\(\)]', '', regex=True)
        restaurant_df['Reviews'] = pd.to_numeric(restaurant_df['Reviews'], errors='coerce').fillna(0).astype(int)
        restaurant_df['Rating'] = pd.to_numeric(restaurant_df['Rating'], errors='coerce')
        
        print("\n--- Final Cleaned Data (First 5 Rows) ---")
        print(restaurant_df.head())
        
        restaurant_df.to_csv('silchar_restaurants_ALL_DATA.csv', index=False)
        print("\nFull, clean, multi-page data saved to silchar_restaurants_ALL_DATA.csv")