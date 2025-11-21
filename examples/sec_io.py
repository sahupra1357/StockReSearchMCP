import requests
import json
import pandas as pd

# 1. Configuration
API_KEY = "YOUR_API_KEY" # Replace with your actual API key
SECTOR = "Energy"       # The sector you want to query

# The endpoint structure for listing all companies by sector
BASE_URL = "https://api.sec-api.io/mapping/sector/"
API_URL = f"{BASE_URL}{SECTOR}"
API_KEY='fd2761a841ae234af92fed84aa2758aaa85c5a9affc054e749510b0c3d38d67c'
# 2. API Request
try:
    # Send GET request with the API key as a query parameter
    response = requests.get(API_URL, params={'token': API_KEY})
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    # 3. Process the JSON Response
    companies = response.json()

    print(f"✅ Successfully retrieved {len(companies)} companies in the {SECTOR} sector.")
    print("-" * 40)

    # 4. Display Results (Using Pandas for clear table formatting)
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(companies)

    # Filter and display key columns for the first few companies
    display_df = df[['ticker', 'name', 'industry', 'exchange', 'isDelisted']].head(5)

    print(f"Top 5 Companies in the {SECTOR} Sector:")
    print(display_df.to_markdown(index=False))

except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred during the API request: {e}")
    # Handle specific errors like 401 Unauthorized or 404 Not Found