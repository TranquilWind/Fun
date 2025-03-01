import os
import requests
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

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

def update_google_sheet(spreadsheet_id, sheet_name, new_points):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPES
        )
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return False

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found in the Google Sheet')
            return False
        header_row = values[0]
        name_col_idx = header_row.index('Name') if 'Name' in header_row else -1
        points_col_idx = header_row.index('Points') if 'Points' in header_row else -1
        
        if name_col_idx == -1 or points_col_idx == -1:
            print("Required columns 'Name' or 'Points' not found in the sheet")
            return False
            
        
        updates = []
        for i, row in enumerate(values[1:], start=2): 
            if len(row) > name_col_idx:
                player_name = row[name_col_idx]
                if player_name in new_points:
                    cell_range = f'{sheet_name}!{chr(65 + points_col_idx)}{i}'
                    updates.append({
                        'range': cell_range,
                        'values': [[new_points[player_name]]]
                    })
        
        if updates:
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body).execute()
            print(f"{result.get('totalUpdatedCells')} cells updated.")
            return True
        else:
            print("No matching players found to update.")
            return False
            
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False

def main():
    url = input("Points list URL: ")
    spreadsheet_id = input("Google Spreadsheet ID: ")
    sheet_name = "Sheet1"
    
    try:
        print("Scraping points data...")
        points_data = scrape_points(url)
        
        if points_data:
            print(f"Found points data for {len(points_data)} players")
            success = update_google_sheet(spreadsheet_id, sheet_name, points_data)
            
            if success:
                print("Points updated successfully!")
            else:
                print("Failed to update points.")
        else:
            print("No points data was retrieved.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
if __name__ == "__main__":
    main()