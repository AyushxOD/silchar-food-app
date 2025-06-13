import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def final_mission_scrape():
    print("Initializing the Final Mission Scraper...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    # --- SETUP FOR SAVE-AS-YOU-GO ---
    output_filename = 'silchar_reviews_THE_FINAL_DATA.csv'
    if not os.path.exists(output_filename):
        pd.DataFrame(columns=['Name', 'Reviews_Text']).to_csv(output_filename, index=False)
        print(f"Output file created: {output_filename}.")
    else:
        print(f"Appending data to existing file: {output_filename}.")

    url = "https://www.google.com/search?q=restaurants+in+Silchar+Assam"
    driver.get(url)

    input("\n>>> ACTION: Please solve any CAPTCHA, then press Enter here to begin...")
    
    try:
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'More places'))).click()
        print(">>> 'More places' button engaged...")
        time.sleep(5)
    except TimeoutException:
        print(">>> Could not find 'More places' button.")

    page_number = 1

    # --- NEW, ROBUST PAGINATION LOOP ---
    while True:
        print(f"\n{'='*20} Starting Page {page_number} {'='*20}")
        
        try:
            # Wait for the results list to be ready on the current page
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'uMdZh')))
            num_results = len(driver.find_elements(By.CLASS_NAME, 'uMdZh'))
            print(f"Found {num_results} restaurants on this page.")

            # --- RESTAURANT LOOP (for the current page) ---
            for i in range(num_results):
                restaurant_info = {}
                name = "Unknown Target"
                print(f"\n--- Processing Restaurant {i+1}/{num_results} on this page ---")
                try:
                    # Re-find elements each time to prevent them from going stale
                    results_list = driver.find_elements(By.CLASS_NAME, 'uMdZh')
                    restaurant_to_click = results_list[i]
                    
                    # The script finds the name and clicks the restaurant FOR YOU
                    name = restaurant_to_click.find_element(By.CLASS_NAME, 'OSrXXb').text
                    restaurant_info['Name'] = name
                    print(f">>> Target Acquired: {name}. Opening details...")
                    restaurant_to_click.click()
                    
                    # Wait for the detail panel to update
                    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "h2.qrShPb").text == name)
                    
                    # --- PAUSE AND WAIT FOR YOU ---
                    input(f"--> YOUR TURN: For '{name}', please 1) Click 'Reviews' and 2) SCROLL the reviews. Then press Enter...")

                    # --- SCRIPT RESUMES TO READ AND SAVE ---
                    print("--> MY TURN: Reading all visible reviews...")
                    review_elements = driver.find_elements(By.CLASS_NAME, 'bwb7ce')
                    review_texts = [review.text for review in review_elements]
                    
                    restaurant_info['Reviews_Text'] = ' \n\n '.join(review_texts)
                    
                    # Save data for this one restaurant immediately
                    temp_df = pd.DataFrame([restaurant_info])
                    temp_df.to_csv(output_filename, mode='a', header=False, index=False)
                    print(f"  -> SUCCESS: Scraped and SAVED {len(review_texts)} reviews for {name}.")

                except Exception as e:
                    print(f"  -> A critical error occurred for {name}. Skipping. Error: {e}")
                    continue

            # --- AFTER PAGE IS DONE, GO TO NEXT ---
            print("\n>>> Page complete. Attempting to click 'Next'...")
            next_button = wait.until(EC.presence_of_element_located((By.ID, 'pnnext')))
            driver.execute_script("arguments[0].click();", next_button) # Use forceful click
            page_number += 1

        except TimeoutException:
            print(">>> No more 'Next' button found. All pages have been scraped.")
            break
        except Exception as e:
            print(f"A fatal error occurred on page {page_number}. Ending mission. Error: {e}")
            break

    driver.quit()
    print("\n\n--- MISSION ACCOMPLISHED ---")

if __name__ == '__main__':
    final_mission_scrape()