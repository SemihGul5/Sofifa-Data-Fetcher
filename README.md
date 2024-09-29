# Sofifa Data Fetcher

This is a web application that scrapes league and team data from Sofifa using Python (Flask, Selenium, and BeautifulSoup). The application allows you to fetch leagues and teams data and display it in JSON format on the browser.

## Features
- **Fetch Leagues**: Scrape leagues data from Sofifa, including league name, country, and league ID.
- **Fetch Teams**: Scrape teams data for each league, including team name, overall rating, and league name.
- The scraped data is saved in JSON files (`leagues_data.json` and `teams_overall.json`) and displayed on the web interface.

## Requirements
Make sure you have the following installed:
- Python 3.x
- Flask
- Selenium
- BeautifulSoup4
- Webdriver Manager for Selenium
- Google Chrome Browser and ChromeDriver

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Sofifa-Sata-Fetcher.git
   cd sofifa-data-fetcher
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
3. Ensure that you have Google Chrome installed and its ChromeDriver is managed by webdriver_manager. This will be installed automatically with the requirements.txt.

## How to Run

1. Start the Flask application:
   ```bash
   python app.py
2. Open your browser and navigate to:
   ```bash
   http://127.0.0.1:5000
3. Use the interface to:

 - Fetch Leagues: Scrape the leagues from Sofifa.
 - Fetch Teams: After leagues are scraped, fetch teams for each league.
4. The JSON data will be displayed on the web page and saved as leagues_data.json and teams_overall.json.

## JSON Output Files
leagues_data.json: Sofifa'daki tüm takımları içerir.
teams_overall.json: Contains all the teams from the scraped leagues
all_teams_overall_with_cups.json: Includes all teams in Sofifa. Along with European cups

## Dependencies
 - Flask: Web framework for Python.
 - Selenium: For browser automation.
 - BeautifulSoup: For parsing HTML data.
 - WebDriverManager: Automatically handles downloading and managing ChromeDriver for Selenium.
