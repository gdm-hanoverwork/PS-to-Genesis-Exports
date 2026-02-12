#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-

"""Documentation Block -- TBD"""

__author__ = "Gregory Matyola"
__version__ = "2026.02.12"
__license__ = "MIT"

import configparser
import os
import sys
import requests
import pandas as pd
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# 1. Load Environment Variables
# This loads the variables from the .env file into the script securely.
load_dotenv()

# Retrieve variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTH_URL = os.getenv('AUTH_URL')
DATA_URL = os.getenv('DATA_URL')

def get_bearer_token(client_id, client_secret, auth_url):
    """
    Authenticates with the API using Client Credentials grant type
    to obtain a Bearer token.
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        # Some APIs require scope, e.g., 'scope': 'read_data'
    }
    
    try:
        # Note: Many OAuth providers (like Auth0, Okta) accept Basic Auth for the client_id/secret.
        # If your API requires them in the body, add them to the 'data' dictionary instead.
        response = requests.post(
            auth_url, 
            data=data, 
            headers=headers, 
            auth=HTTPBasicAuth(client_id, client_secret),
            timeout=10
        )
        
        # Check for HTTP errors (4xx or 5xx)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get('access_token')

    except requests.exceptions.RequestException as e:
        print(f"Error obtaining token: {e}")
        if 'response' in locals():
            ...
            # print(f"Server Response: {response.text}")
        sys.exit(1)

def fetch_api_data(data_url, token):
    """
    Fetches data from the secured API endpoint using the Bearer token.
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        "Accept": "application/json",
    }
    body = {
        'terms_start':'21',
        'terms_end':'36',
    }
    try:
        response = requests.post(data_url, headers=headers, json=body, timeout=10)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            for key, value in response.headers.items():
                print(f"{key}: {value}")
            response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

def save_to_excel(data, filename="api_data.xlsx"):
    """
    Parses the JSON data and saves it to an Excel file using Pandas.
    """
    try:
        # NORMALIZATION:
        # APIs often return data wrapped in keys like 'data', 'results', or 'items'.
        # You may need to inspect your API response and adjust the logic below.
        
        records = []
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # Try to find common list keys, or default to the whole dict
            if 'data' in data and isinstance(data['data'], list):
                records = data['data']
            elif 'results' in data and isinstance(data['results'], list):
                records = data['results']
            else:
                records = [data] # Wrap single object in list

        if not records:
            print("No records found to save.")
            return

        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Save to Excel
        df.to_excel(filename, index=False)
        print(f"Success! Data saved to {filename}")

    except Exception as e:
        print(f"Error saving to Excel: {e}")

def main():
    # Validation to ensure env vars exist
    if not all([CLIENT_ID, CLIENT_SECRET, AUTH_URL, DATA_URL]):
        print("Error: Missing environment variables. Please check your .env file.")
        sys.exit(1)

    print("1. Authenticating...")
    token = get_bearer_token(CLIENT_ID, CLIENT_SECRET, AUTH_URL)
    print("   Token received.")
    
    print("2. Fetching data...")
    config = configparser.ConfigParser(allow_unnamed_section=True)
    config.read(filenames='.env') # Your file

    print("   Configuration loaded.")
    print(f"   Sections in config: {config.sections()}")  # Print available sections for verification

    # Iterating over the 'categories' section
    if (len_categories:= len(categories:=config.sections())-1) > 0:  # Check if there are more than one sections (assuming 'CURRICULUM_EXPORT' is one of them)
        for number, cat in enumerate(categories,start=0):
            print(f"2.{number}/{len_categories} Fetching data for {cat}...")
            if cat == config.default_section:
                continue  # Skip unnamed section if it exists
            for key, val in config[cat].items():
                print(f"Installing {key} {val} for category {cat}...")
            if not isinstance(cat, str):
                print(f"Warning: Category '{type(cat)=}' is not a string. Skipping.")
                continue  # Skip if cat is not a string (just a safety check)
    else:
        api_data = fetch_api_data(DATA_URL, token)
        print("   Data received.")

        for key, value in api_data.items():
            if (key == 'record'):
                my_records=value
                for sub_value in value:
                    ...
                    # print(f"{str(sub_value)[:100]}...")  # Print first 100 chars of each sub-key's value for verification
            ...
            # print(f"   {key}: {str(value)}...")  # Print first 100 chars of each key's value for verification
        # print(f"   Sample data: {str(api_data)[:200]}...")  # Print first 200 chars of the response for verification
        my_records = api_data['record']

        print("3. Saving to Excel...")
        save_to_excel(data=my_records)

if __name__ == "__main__":
    main()
