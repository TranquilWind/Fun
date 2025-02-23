import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import math

class Player:
    def __init__(self, name, squad, role):
        self.name = name
        self.squad = squad 
        self.role = role
        self.base_price = 0  
        
    def set_base_price(self, price):
        self.base_price = price
        
    def __str__(self):
        return f"{self.name} ({self.role}) - {self.squad} - Base Price: {self.base_price}"


class PlayerDatabase:
    def __init__(self):
        self.players = {}
    
    def add_player(self, name, squad, role):
        if not name:
            raise ValueError("Player name cannot be empty")
        if name in self.players:
            print(f"Note: Player '{name}' already exists in database")
            return
        self.players[name] = Player(name, squad, role)
        print(f"Added player '{name}' to database")
        
    def get_player(self, name):
        player = self.players.get(name)
        if not player:
            print(f"Warning: Player '{name}' not found in database")
        return player
    
    def set_base_price(self, name, price):
        player = self.get_player(name)
        if player:
            try:
                player.set_base_price(price)
                return True
            except Exception as e:
                print(f"Error setting base price for {name}: {e}")
                return False
        return False
    
    def __str__(self):
        return f"PlayerDatabase ({len(self.players)} players): {list(self.players.keys())}"


player_db = PlayerDatabase()

def scrape_webpage(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links_with_class = soup.find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
        print("\nLinks with specified class:")
        squad_links = {}
        for link in links_with_class:
            if "Squad" in link.get_text():
                print(f"Text: {link.get_text(strip=True)}")
                print(f"URL: {link.get('href')}")
                squad_links[link.get_text(strip=True)] = link.get('href')
                print("-" * 50)

        each_squad(headers, squad_links)
        
        return {
            'title': soup.title.string if soup.title else 'No title found',
            'text': soup.get_text(),
            'links': [link.get('href') for link in soup.find_all('a')],
        }
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

def each_squad(headers, squad_links):
    player_links = {}       
    base_url = "https://www.espncricinfo.com"
    for squad_name, path in squad_links.items():
        full_url = base_url + path
        print(f"\nProcessing {squad_name} at {full_url}")
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.find_all('div', class_='ds-border-line odd:ds-border-r ds-border-b')
        for i in block:
            player_name = i.find('a', class_='ds-inline-flex ds-items-start ds-leading-none').get_text()
            player_role = i.find('p', class_='ds-text-tight-s ds-font-regular ds-mb-2 ds-mt-1').get_text()
            player_link = i.find('a', class_='ds-inline-flex ds-items-start ds-leading-none').get('href')
            player_links[player_name] = player_link
            player_db.add_player(player_name, squad_name, player_role)

            print(player_name)
            print("-" * 50)
    base_price_calc(headers, player_links)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'player_database_{timestamp}.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Squad', 'Name', 'Role', 'Base Price'])  # Header row
        
        for name, player in player_db.players.items():
            writer.writerow([
                player.squad[0:-6],
                player.name,
                player.role, 
                player.base_price
            ])

    print(f"Player database exported to: {csv_filename}")


    
def base_price_calc(headers, player_links):
    print("Current players in database:", player_db)
    base_url = "https://www.espncricinfo.com"
    
    for player_name, path in player_links.items():
        player = player_db.get_player(player_name)
        if not player:
            print(f"Warning: Player {player_name} not found in database")
            continue
            
        try:
            full_url = base_url + path
            print(f"\nProcessing {player_name} at {full_url}")
            response = requests.get(full_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = soup.find_all('div', class_='ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line ds-mb-4')
            t20_stats = None
            
            for detail in details:
                if "T20 Stats" in detail.get_text():
                    t20_stats = detail
                    break

            if t20_stats:
                testing = t20_stats.find_all('tr')
                ipl_details = None
                ipl_details_list = []
                for row in testing:
                    if 'IPL' in row.get_text():
                        ipl_details = row
                        print(f"Found IPL details for {player_name}")
                        ipl_details_list.append(ipl_details)
                if len(ipl_details_list) > 0:
                    if '/' in ipl_details_list[0].get_text():
                        bowling = ipl_details_list[0]
                        batting = ipl_details_list[1]
                    elif '/' in ipl_details_list[1].get_text():
                        bowling = ipl_details_list[1]
                        batting = ipl_details_list[0]
                    elif '-' in ipl_details_list[0].get_text():
                        bowling = ipl_details_list[0]
                        batting = ipl_details_list[1]
                    else:
                        bowling = ipl_details_list[1]
                        batting = ipl_details_list[0]
                    batting_score = int(calc_bat(batting))
                    bowling_score = int(calc_bowl(bowling))
                    print(f"Batting score: {batting_score}")
                    print(f"Bowling score: {bowling_score}")
                    player_db.set_base_price(player_name, max(batting_score, bowling_score, 1))
                else:
                    print(f"No IPL stats found for {player_name}")
                    player_db.set_base_price(player_name, 1)

            else:
                print(f"No T20 stats found for {player_name}")
                player_db.set_base_price(player_name, 1)
        
                
        except requests.RequestException as e:
            print(f"Error fetching data for {player_name}: {e}")
        except Exception as e:
            print(f"Error processing {player_name}: {e}")

def calc_bat(batting):
    if '-' in batting.get_text():
        return 0
    if batting.find_all('td')[5].get_text() == '0':
        return 0
    if float(batting.find_all('td')[7].get_text())<15 or float(batting.find_all('td')[5].get_text())<200:
        return 0
    return round(((float(batting.find_all('td')[5].get_text())*0.01) + (float(batting.find_all('td')[7].get_text())*2) +  (float(batting.find_all('td')[9].get_text())*0.5)) / 100, 0)
def calc_bowl(bowling):
    if '-' in bowling.get_text():
        return 0
    if bowling.find_all('td')[6].get_text() == '0':
        return 0
    if float(bowling.find_all('td')[6].get_text())<20 or float(bowling.find_all('td')[9].get_text())>40:
        return 0
    return round(((float(bowling.find_all('td')[6].get_text())*0.5) + (60 - float(bowling.find_all('td')[9].get_text()))*2 +  (20-float(bowling.find_all('td')[10].get_text()))*5) / 100, 0)


if __name__ == "__main__":
    url = "https://www.espncricinfo.com/series/ipl-2025-1449924/squads"  
    result = scrape_webpage(url)
    
    if result:
        print(f"Title: {result['title']}")
        print(f"Number of links found: {len(result['links'])}")