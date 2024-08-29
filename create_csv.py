import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Load credentials from environment variables
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# URL for Reliance company's Profit & Loss page
login_url = "https://www.screener.in/login/"
reliance_url = "https://www.screener.in/company/RELIANCE/consolidated/"

# Use requests to log in to Screener.in
session = requests.Session()
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract CSRF token
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
if csrf_token:
    csrf_token = csrf_token['value']
else:
    print("CSRF token not found!")
    exit()

# Prepare login data with the extracted CSRF token
login_data = {
    "username": email,
    "password": password,
    "csrfmiddlewaretoken": csrf_token
}

# Post the login data to the form
login_response = session.post(login_url, data=login_data, headers={"Referer": login_url})

# Check if login was successful
if login_response.url == "https://www.screener.in/dash/":
    print("Login successful!")

    # Fetch the page content
    page_response = session.get(reliance_url)
    page_soup = BeautifulSoup(page_response.text, 'html.parser')

    # Find the "Profit & Loss" section
    profit_loss_section = page_soup.find('h2', string="Profit & Loss")
    
    if profit_loss_section:
        table = profit_loss_section.find_next('table')
        
        if table:
            # Extract table headers (Years)
            years = [header.get_text(strip=True) for header in table.find_all('th')]
            print(f"Years: {years}")
            
            # Extract table rows (Sales, Expenses, etc.)
            categories = []
            data = []
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    # The first column is the category (Sales, Expenses, etc.)
                    category = columns[0].get_text(strip=True)
                    categories.append(category)
                    
                    # The remaining columns are data (numbers corresponding to the years)
                    row_data = [column.get_text(strip=True) for column in columns[1:]]
                    data.append(row_data)
                    
            # Convert the list of categories and data to a DataFrame
            df = pd.DataFrame(data, index=categories, columns=years[1:])  # Skip the first "Parameters" header
            
            # Transpose the DataFrame so that years become rows and categories become columns
            df_transposed = df.transpose().reset_index()
            df_transposed.rename(columns={'index': 'Year'}, inplace=True)
            
            # Save the transposed DataFrame to CSV
            csv_file_path = 'profit_loss_data/profit_loss_data.csv'
            df_transposed.to_csv(csv_file_path, index=False)
            print(f"Data saved to {csv_file_path}")
            
            # Print the transposed DataFrame
            print(df_transposed)
        else:
            print("Table not found in Profit & Loss section!")
    else:
        print("Profit & Loss section not found!")
else:
    print("Login failed!")
# new comment for testing