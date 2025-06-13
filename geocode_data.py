import pandas as pd
from geopy.geocoders import Nominatim
import time
from tqdm import tqdm # A progress bar library

print("Starting the geocoding process. This will take a few minutes...")

# Initialize the Nominatim geocoder
# The user_agent can be any name you choose for your app.
geolocator = Nominatim(user_agent="silchar_food_tour_app")

# Load your master dataset
df = pd.read_csv('silchar_restaurants_ALL_DATA.csv')

# Prepare lists to store the new data
latitudes = []
longitudes = []

# Use tqdm to create a nice progress bar in your terminal
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Geocoding Restaurants"):
    # Create a detailed query for better accuracy
    query = f"{row['Name']}, Silchar, Assam, India"
    
    try:
        # Geocode the address
        location = geolocator.geocode(query, timeout=10)
        
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
            # print(f"SUCCESS: Found coordinates for {row['Name']}")
        else:
            latitudes.append(None)
            longitudes.append(None)
            # print(f"WARNING: Could not find coordinates for {row['Name']}")
            
    except Exception as e:
        # Handle potential errors like network issues
        print(f"ERROR: An error occurred for {row['Name']}. Error: {e}")
        latitudes.append(None)
        longitudes.append(None)
    
    # --- IMPORTANT: Rate limit to respect Nominatim's usage policy (1 request/sec) ---
    time.sleep(1.1)

# Add the new columns to the DataFrame
df['latitude'] = latitudes
df['longitude'] = longitudes

# Save the new, enriched DataFrame to a new file
output_filename = 'silchar_restaurants_geocoded.csv'
df.to_csv(output_filename, index=False)

print(f"\nGeocoding complete! Enriched data saved to '{output_filename}'")
print(f"Check the file to see how many locations were successfully found.")