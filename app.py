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
# Listeler
champions_league_teams = [
    "PSV", "Aston Villa", "Monaco", "Dinamo Zagreb", "LOSC Lille", "RB Leipzig", "Bologna", "Atlético Madrid",
    "Sparta Praha", "Benfica", "Young Boys", "Liverpool", "Sporting CP", "VfB Stuttgart", "Atalanta", "Bayer 04 Leverkusen",
    "Feyenoord", "Girona", "Inter", "FC Barcelona", "Paris Saint Germain", "Borussia Dortmund", "Sturm Graz",
    "Shakhtar Donetsk", "Milan", "FC Bayern München", "Juventus", "Manchester City", "Club Brugge", "Celtic", "Salzburg",
    "Arsenal", "Real Madrid", "Stade Brestois 29"
]

europa_league_teams = [
    "Bodø / Glimt", "Porto", "Roma", "Olympique Lyonnais", "Galatasaray", "Beşiktaş", "Union Saint-Gilloise", "Fenerbahçe",
    "Real Sociedad", "Qarabağ", "FCSB", "Ferencváros", "Anderlecht", "Nice", "FC Twente", "TSG Hoffenheim", "AZ Alkmaar",
    "Malmö FF", "Rangers", "Ajax", "PAOK", "Eintracht Frankfurt", "Midtjylland", "Lazio", "Olympiakos Piraeus",
    "Elfsborg", "Manchester United", "Slavia Praha", "Viktoria Plzeň", "Dynamo Kyiv", "Athletic Club", "Sporting Braga",
    "Tottenham Hotspur"
]

conference_league_teams = [
    "Shamrock Rovers", "Djurgården", "Heidenheim", "Cercle Brugge", "St. Gallen", "HJK", "Gent", "Legia Warszawa",
    "Rapid Wien", "LASK Linz", "Real Betis", "İstanbul Başakşehir", "Fiorentina", "Chelsea", "Jagiellonia Białystok",
    "Lugano", "Vitória SC", "APOEL", "Molde", "Hearts", "Panathinaikos", "København"
]


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
                # Logo URL'sindeki "60.png" kısmını "180.png" olarak değiştirelim
                logo_url = logo_img['data-src'].replace('60.png', '180.png')
            else:
                logo_url = 'N/A'  # Logo yoksa

            # Ülke bayrağı ve ismini bulma
            flag_img = row.find('img', {'class': 'flag'})
            if flag_img and 'data-src' in flag_img.attrs:
                # Bayrak URL'sini @3x.png çözünürlüğünde alalım
                flag_url = flag_img['data-src'].replace('.png', '@3x.png')
                country_name = flag_img['title'] if 'title' in flag_img.attrs else 'Unknown'
            else:
                flag_url = 'N/A'
                country_name = 'Unknown'

            # Lig bilgilerini ekleyelim
            leagues_data.append({
                'league_id': league_id,
                'league_name': league_name,
                'country': country_name,
                'logo_url': logo_url,  # Lig logosu URL'si (180.png)
                'flag_url': flag_url  # Ülke bayrağı URL'si (@3x.png)
            })

    driver.quit()

    # Veriyi JSON formatına dönüştürüp dosyaya kaydedelim
    with open('leagues_data.json', 'w', encoding='utf-8') as f:
        json.dump(leagues_data, f, ensure_ascii=False, indent=4)
    
    return leagues_data

def fetch_teams_from_leagues():
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
            team_name_tag = team.find('a', href=True)
            if team_name_tag and 'team/' in team_name_tag['href']:
                team_name = team_name_tag.get_text(strip=True)
            else:
                continue

            overall_tag = team.find('td', {'data-col': 'oa'})
            overall = overall_tag.get_text(strip=True) if overall_tag else 'N/A'

            league_tag = team.find('a', class_='sub')
            league_name = league_tag.get_text(strip=True) if league_tag else 'N/A'

            team_image_tag = team.find('img', class_='team')
            team_image_url = team_image_tag['data-src'] if team_image_tag else 'N/A'

            all_teams_data.append({
                'team_name': team_name,
                'overall': overall,
                'league_name': league_name,
                'team_image_url': team_image_url
            })

        time.sleep(1)

    driver.quit()

    with open('teams_overall.json', 'w', encoding='utf-8') as f:
        json.dump(all_teams_data, f, ensure_ascii=False, indent=4)
    return all_teams_data

# Takımlara Avrupa kupaları ekleyen fonksiyon
def add_european_cups():
    with open('teams_overall.json', 'r', encoding='utf-8') as f:
        teams_data = json.load(f)

    for team in teams_data:
        team_name = team['team_name']
        if team_name in champions_league_teams:
            team['european_cup'] = 'Champions League'
        elif team_name in europa_league_teams:
            team['european_cup'] = 'Europa League'
        elif team_name in conference_league_teams:
            team['european_cup'] = 'Conference League'
        else:
            team['european_cup'] = 'None'

    with open('all_teams_overall_with_cups.json', 'w', encoding='utf-8') as f:
        json.dump(teams_data, f, ensure_ascii=False, indent=4)
    return teams_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-leagues')
def fetch_leagues_data():
    leagues_data = fetch_leagues()
    return jsonify(leagues_data)

@app.route('/fetch-teams')
def fetch_teams_data():
    teams_data = fetch_teams_from_leagues()
    return jsonify(teams_data)

@app.route('/add-european-cups')
def add_european_cups_data():
    teams_data = add_european_cups()
    return jsonify(teams_data)

if __name__ == '__main__':
    app.run(debug=True)
