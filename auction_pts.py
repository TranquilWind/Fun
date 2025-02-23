import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_points(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        
        response = requests.get(url, headers=headers)
        
        
        if response.status_code == 403:
            print("Access Denied: The website is blocking automated requests")
            return {}
            
        if response.status_code != 200:
            print(f"Failed to fetch data: Status code {response.status_code}")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        points_data = {}
        
        players = soup.find_all('tr')
        players = players[1:]  
        
        try:
            name = players[0].find('span', {'class': 'ds-text-tight-s ds-font-medium ds-text-raw-white hover:ds-underline hover:ds-decoration-raw-white ds-block ds-ml-2 ds-text-left ds-cursor-pointer'}).text.strip()
            points = players[0].find('td', {'class': 'ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-font-bold !ds-bg-ui-fill-standout ds-text-raw-white'}).text.strip()
        except:
            print("Error")
        
        for player in players:
            try:
                name = player.find('span', {'class': 'ds-text-tight-s ds-font-medium ds-text-typo hover:ds-text-typo-primary ds-block ds-ml-2 ds-text-left ds-cursor-pointer'}).text.strip()
                
                points = player.find('td', {'class': 'ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-font-bold'}).text.strip()
                points_data[name] = float(points)
            except:
                continue
            
        return points_data

    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {str(e)}")
        return {}

def update_csv(csv_file, new_points):

    df = pd.read_csv(csv_file)
    
    for index, row in df.iterrows():
        player_name = row['Name']  
        if player_name in new_points:
            df.at[index, 'Points'] = new_points[player_name]
    
    
    df.to_csv(csv_file, index=False)

def main():
    
    url = input("Enter the points list URL: ")
    csv_file = input("Enter the path to your CSV file: ")
    
    try:
        
        points_data = scrape_points(url)
        
        update_csv(csv_file, points_data)
        
        print("Points updated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
