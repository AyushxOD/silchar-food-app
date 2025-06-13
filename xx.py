import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def scrape_with_scrolling_panel():
    print("Setting up Selenium for the Final Polished Scrape...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10) # A 10 second wait should be sufficient

    url = "https://www.google.com/search?q=restaurants+in+Silchar+Assam"
    driver.get(url)

    input("\nACTION REQUIRED: Please solve any CAPTCHA, then press Enter here to begin...")
    
    try:
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'More places'))).click()
        print("Clicked 'More places' button. Waiting for the main list...")
        time.sleep(5)
    except TimeoutException:
        print("Could not find 'More places' button, proceeding with what is visible.")

    all_restaurant_data = []
    page_number = 1

    # --- PAGINATION LOOP ---
    while True:
        print(f"\n{'='*20} Scraping Page {page_number} {'='*20}")
        
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'uMdZh')))
        num_results_on_page = len(driver.find_elements(By.CLASS_NAME, 'uMdZh'))
        print(f"Found {num_results_on_page} restaurants on this page.")

        # --- RESTAURANT LOOP ---
        for i in range(num_results_on_page):
            restaurant_info = {}
            try:
                results_list = driver.find_elements(By.CLASS_NAME, 'uMdZh')
                if i >= len(results_list): continue
                
                restaurant_to_click = results_list[i]
                
                name = restaurant_to_click.find_element(By.CLASS_NAME, 'OSrXXb').text
                restaurant_info['Name'] = name
                print(f"\nProcessing {i+1}/{num_results_on_page}: {name}")

                restaurant_to_click.click()
                
                # --- NEW: SCROLL THE RIGHT-HAND DETAIL PANEL ---
                try:
                    # This panel often has a specific role or class. We'll use a common one.
                    # This JavaScript command scrolls the specific panel, not the whole page.
                    pane_selector = "div[role='main']"
                    pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pane_selector)))
                    # Scroll down a few times to trigger any lazy-loaded content
                    for _ in range(3):
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
                        time.sleep(0.5)
                    print("  -> Scrolled detail panel.")
                except Exception as e:
                    print(f"  -> Could not scroll detail panel. Info may be incomplete. Error: {e}")

                # --- Scrape All Details ---
                details = {}
                # Address
                try: details['Address'] = driver.find_element(By.CLASS_NAME, 'LrzXr').text
                except: details['Address'] = "Not found"
                # Phone
                try: details['Phone'] = driver.find_element(By.CSS_SELECTOR, 'span[data-tooltip*="phone"]').text
                except: details['Phone'] = "Not found"
                # Price
                try: details['Price'] = driver.find_element(By.XPATH, "//span[contains(text(), '₹')]").text
                except: details['Price'] = "Not found"
                # Services
                try:
                    services_container = driver.find_element(By.CLASS_NAME, 'i2sC4e')
                    options = [opt.text for opt in services_container.find_elements(By.CLASS_NAME, 'E0DTEd') if opt.text]
                    details['Services'] = ', '.join(options)
                except: details['Services'] = "Not found"
                # Rating and Reviews from detail panel for accuracy
                try:
                    rating_string = driver.find_element(By.CSS_SELECTOR, 'span.Aq14Cf').text
                    details['Rating'] = rating_string
                except: details['Rating'] = "Not found"

                print(f"  -> Details scraped: {details}")
                restaurant_info.update(details)
                all_restaurant_data.append(restaurant_info)
                
            except Exception as e:
                print(f"  -> An error occurred for item {i+1} ({name}). Skipping. Error: {e}")
                continue

        # --- Go to the next page ---
        try:
            print("\nPage complete. Looking for the 'Next' page button...")
            next_button = wait.until(EC.element_to_be_clickable((By.ID, 'pnnext')))
            next_button.click()
            page_number += 1
        except TimeoutException:
            print("All pages have been scraped.")
            break

    driver.quit()
    return pd.DataFrame(all_restaurant_data)

if __name__ == '__main__':
    final_df = scrape_with_scrolling_panel()
    if not final_df.empty:
        print("\n\n--- FINAL SCRAPING COMPLETE ---")
        print(f"Successfully scraped details for {len(final_df)} restaurants.")
        print(final_df.head())
        final_df.to_csv('silchar_restaurants_FINAL_RICH_DETAILS.csv', index=False)
        print("\nAll detailed data saved to silchar_restaurants_FINAL_RICH_DETAILS.csv")