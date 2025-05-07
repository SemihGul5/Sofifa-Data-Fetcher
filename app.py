from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import time
import html

app = Flask(__name__)
champions_league_teams = [
    "PSV", "Aston Villa", "AS Monaco", "Dinamo Zagreb", "Lille OSC", "RB Leipzig", "Bologna", "Atlético Madrid",
    "Sparta Praha", "SL Benfica", "BSC Young Boys", "Liverpool", "Sporting CP", "VfB Stuttgart", "Atalanta", "Bayer 04 Leverkusen",
    "Feyenoord", "Girona FC", "Inter", "FC Barcelona", "Paris Saint-Germain", "Borussia Dortmund", "SK Sturm Graz",
    "Shakhtar Donetsk", "AC Milan", "FC Bayern München", "Juventus", "Manchester City", "Club Brugge KV", "Celtic", "FC Red Bull Salzburg",
    "Arsenal", "Real Madrid", "Stade Brestois 29"
]

europa_league_teams = [
    "FK Bodø/Glimt", "FC Porto", "Roma", "Olympique Lyonnais", "Galatasaray SK", "Beşiktaş JK", "Union Saint-Gilloise", "Fenerbahçe SK",
    "Real Sociedad", "Qarabağ FK", "FCSB", "Ferencvárosi Torna Club", "RSC Anderlecht", "OGC Nice", "FC Twente", "TSG 1899 Hoffenheim", "AZ Alkmaar",
    "Malmö FF", "Rangers", "Ajax", "PAOK", "Eintracht Frankfurt", "Midtjylland", "Lazio", "Olympiakos Piraeus",
    "IF Elfsborg", "Manchester United", "SK Slavia Praha", "Viktoria Plzeň", "Dynamo Kyiv", "Athletic Club", "Sporting Clube de Braga",
    "Tottenham Hotspur"
]

conference_league_teams = [
    "Shamrock Rovers", "Djurgårdens IF", "1. FC Heidenheim 1846", "Cercle Brugge KSV", "FC St.Gallen 1879", "HJK Helsinki", "KAA Gent", "Legia Warszawa",
    "SK Rapid", "LASK Linz", "Real Betis Balompié", "Medipol Başakşehir FK", "Fiorentina", "Chelsea", "Jagiellonia Białystok",
    "FC Lugano", "Vitória SC", "APOEL FC", "Molde FK", "Hearts", "Panathinaikos FC", "FC København"
]

def calculate_stars(overall):
    if overall >= 83:
        return 5
    elif 79 <= overall <= 82:
        return 4.5
    elif 75 <= overall <= 78:
        return 4
    elif 71 <= overall <= 74:
        return 3.5
    elif 69 <= overall <= 70:
        return 3
    elif 67 <= overall <= 68:
        return 2.5
    elif 65 <= overall <= 66:
        return 2
    elif 63 <= overall <= 64:
        return 1.5
    elif 60 <= overall <= 62:
        return 1
    else:
        return 0.5


def fetch_leagues():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = "https://sofifa.com/leagues"
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    leagues_data = []

    league_links = soup.find_all('a', href=True)
    for link in league_links:
        href = link['href']
        match = re.match(r'/league/(\d+)', href)
        if match:
            league_id = match.group(1)
            league_name = link.get_text(strip=True)
            league_name = html.unescape(league_name)
            row = link.find_parent('tr')

            # Lig logosunu içeren <img> tagini bulalım
            logo_img = row.find('img', class_='team')
            if logo_img and 'data-src' in logo_img.attrs:
                
                logo_url = logo_img['data-src'].replace('60.png', '180.png')
            else:
                logo_url = 'N/A'

            # Ülke bayrağı ve ismini bulma
            flag_img = row.find('img', {'class': 'flag'})
            if flag_img and 'data-src' in flag_img.attrs:
                
                flag_url = flag_img['data-src'].replace('.png', '@3x.png')
                country_name = flag_img['title'] if 'title' in flag_img.attrs else 'Unknown'
            else:
                flag_url = 'N/A'
                country_name = 'Unknown'

            
            leagues_data.append({
                'league_id': league_id,
                'league_name': league_name,
                'country': country_name,
                'logo_url': logo_url, 
                'flag_url': flag_url  
            })

    driver.quit()

    
    with open('leagues_data.json', 'w', encoding='utf-8') as f:
        json.dump(leagues_data, f, ensure_ascii=False, indent=4)
    
    return leagues_data


from selenium.webdriver.chrome.options import Options


def fetch_players_data(offset=0):
    options = Options()
    options.headless = True  # Set the browser to headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    players_data = []
    
    player_id = 1  # Initialize player ID starting from 1

    while offset <= 1140:  # Loop until the offset reaches 1020
        base_url = f"https://sofifa.com/players?type=all&lg%5B0%5D=13&lg%5B1%5D=16&lg%5B2%5D=19&lg%5B3%5D=31&lg%5B4%5D=53&lg%5B5%5D=1&lg%5B6%5D=4&lg%5B7%5D=10&lg%5B8%5D=14&lg%5B9%5D=39&lg%5B10%5D=68&lg%5B11%5D=80&lg%5B12%5D=308&lg%5B13%5D=332&lg%5B14%5D=350&offset={offset}"
        driver.get(base_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find player rows
        player_rows = soup.find_all('tr')
        
        if not player_rows:  # If there are no player rows, exit the loop
            print("No more players found.")
            break
        
        players_fetched = False  # Flag to track if any player data was fetched
        
        for row in player_rows:
            # Player name and URL
            player_name_tag = row.find('a', href=True)
            if player_name_tag and '/player/' in player_name_tag['href']:
                player_name = player_name_tag.get_text(strip=True)
            else:
                continue
            
            # Player image URL extraction
            player_img_tag = row.find('td', class_='a1').find('img')
            if player_img_tag:
                # Using data-src attribute to get the high-resolution image
                player_image_url = player_img_tag['data-src'].replace('60.png', '180.png')
            else:
                player_image_url = 'N/A'  # Default value if image tag is not found

            # Country name
            country_flag_tag = row.find('div').find('img')
            country_name = country_flag_tag['title'] if country_flag_tag else 'Unknown'
            
            # Age extraction
            age_tag = row.find('td', class_='d2')
            age = age_tag.get_text(strip=True) if age_tag else 'Unknown'
            
            # Overall rating extraction
            overall_tag = row.find('em', title=re.compile(r'\d+'))
            overall = overall_tag.get_text(strip=True) if overall_tag else 'N/A'
            
            # Team name extraction
            team_tag = row.find_all('td')[5].find('a')  # Selecting the 6th <td> which contains the team info
            team_name = team_tag.get_text(strip=True) if team_tag else 'Unknown'
            
            # Market value extraction
            market_value_tag = row.find('td', class_='d6')
            market_value = market_value_tag.get_text(strip=True) if market_value_tag else 'N/A'
            
            # Add data to list with player ID
            players_data.append({
                'id': player_id,  # Assign unique ID starting from 1
                'player_name': player_name,
                'player_image_url': player_image_url,
                'team_name': team_name,
                'country_name': country_name,
                'age': age,
                'overall': overall,
                'market_value': market_value,
            })
            
            player_id += 1  # Increment player ID for the next player
            players_fetched = True  # Set flag to True if we fetch at least one player

        # Only increment offset if players were fetched
        if players_fetched:
            offset += 60  # Increment offset by 60 for the next page
            time.sleep(2)  # Wait for 2 seconds before fetching the next page
        else:
            print("No more players found on this page.")
            break

    driver.quit()

    # Write data to JSON file
    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)

    return players_data







def fetch_teams_data():
    with open('leagues_data.json', 'r', encoding='utf-8') as f:
        leagues_data = json.load(f)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    base_url = "https://sofifa.com/teams?type=all&lg%5B%5D={}"
    all_teams_data = []

    for league in leagues_data:
        league_id = league['league_id']
        url = base_url.format(league_id)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        teams = soup.find_all('tr')

        for team in teams:
            # Takım adı
            team_name_tag = team.find('a', href=True)
            if team_name_tag and 'team/' in team_name_tag['href']:
                team_name = team_name_tag.get_text(strip=True)
            else:
                continue

            # Overall
            overall_tag = team.find('td', {'data-col': 'oa'})
            overall = overall_tag.get_text(strip=True) if overall_tag else 'N/A'

            # Lig adı
            league_tag = team.find('a', class_='sub')
            league_name = league_tag.get_text(strip=True) if league_tag else 'N/A'

            # Takım resmi URL'si
            team_image_tag = team.find('img', class_='team')
            team_image_url = team_image_tag['data-src'] if team_image_tag else 'N/A'
            if team_image_url != 'N/A':
                team_image_url = team_image_url.replace('60.png', '180.png')

            # Ülke bayrağı ve ülke adı
            country_flag_tag = team.find('img', class_='flag')
            country_name = country_flag_tag['title'] if country_flag_tag else 'Unknown'

            # Takım bilgilerini listeye ekle
            all_teams_data.append({
                'team_name': team_name,
                'overall': overall,
                'league_name': league_name,
                'team_image_url': team_image_url,
                'country_name': country_name,
            })

        time.sleep(2)

    driver.quit()        
    team['stars'] = calculate_stars(int(overall))

    with open('teams.json', 'w', encoding='utf-8') as f:
        json.dump(all_teams_data, f, ensure_ascii=False, indent=4)

    return all_teams_data

def add_european_cups():
    with open('teams.json', 'r', encoding='utf-8') as f:
        teams_data = json.load(f)

    for team in teams_data:
        team_name = team['team_name']
        overall = team['overall']

        if team_name in champions_league_teams:
            team['european_cup'] = 'Champions League'
        elif team_name in europa_league_teams:
            team['european_cup'] = 'Europa League'
        elif team_name in conference_league_teams:
            team['european_cup'] = 'Conference League'
        else:
            team['european_cup'] = 'None'

        team['stars'] = calculate_stars(int(overall))
        

    with open('teams.json', 'w', encoding='utf-8') as f:
        json.dump(teams_data, f, ensure_ascii=False, indent=4)

    return teams_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-leagues')
def fetch_leagues_data():
    leagues_data = fetch_leagues()
    return jsonify(leagues_data)

@app.route('/fetch_teams_route')
def fetch_teams_route():
    teams_data = fetch_teams_data()
    return jsonify(teams_data)


@app.route('/add_european_cups')
def add_european_cups_route():
    teams_data = add_european_cups()
    return jsonify(teams_data)

# Update the route to call the new fetch function
@app.route('/fetch-players')
def fetch_players():
    players_data = fetch_players_data()  # Use the renamed function
    return jsonify(players_data)


if __name__ == '__main__':
    app.run(debug=True)
