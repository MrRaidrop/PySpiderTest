from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# Set up the MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="nba_matches"
)

# Set the start and end dates
today = datetime.today().date()

start_date = today - timedelta(days=10)
end_date = today

# Define a function to scrape the NBA match data and store it in the database
def scrape_and_store_data(date):
    url = f'http://nba.hupu.com/games/{date}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element containing the match data
    match_data = soup.find('div', class_='gamecenter_content_l')

    # Find all the div elements containing the team names and scores
    team_divs = match_data.find_all('div', class_=lambda x: x and 'team_vs' in x)

    # Parse the match results
    match_results = []
    for div in team_divs:
        score_elem = div.find('div', class_='txt')
        if score_elem is None:
            continue  # If no score is found, skip this div
        score_trans = score_elem.find('span', class_=lambda x: x and 'num' in x)
        if score_trans is None:
            continue  # If no score is found, skip this div
        score = score_trans.text.strip()
        team_name = div.find('div', class_='txt').find('a').text.strip()
        if team_name.isdigit():
            continue  # If the team name is a number, skip this div
        match_results.append({'team': team_name, 'score': score})

    # Store the match results in the database
    cursor = db.cursor()
    for result in match_results:
        cursor.execute(f"INSERT INTO matches (team, score, date) VALUES ('{result['team']}', '{result['score']}', '{date}')")
    db.commit()
    cursor.close()

# Scrape and store data for each day in the date range
for i in range((end_date - start_date).days + 1):
    date = start_date + timedelta(days=i)
    scrape_and_store_data(date)

# Define a route for the home page
@app.route("/")
def home():
    # Get the current date from the URL parameter, or use today's date if no parameter is provided
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = today

    # Get the match data from the database for the selected date
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM matches WHERE date = '{date}'")
    match_data = cursor.fetchall()
    cursor.close()

    # Generate the HTML page
    return render_template("home.html", match_data=match_data, date=date)

# Define a route for the previous day button
@app.route("/prev_day")
def prev_day():
    # Get the current date from the URL parameter, or use today's date if no parameter is provided

    #don't know why it didn't work
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = today

    # Calculate the previous day's date
    prev_date = date - timedelta(days=1)

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM matches WHERE date = '{prev_date}'")
    prev_match_data = cursor.fetchall()
    cursor.close()

    if not prev_match_data:
        # If the data for the previous day is not in the database, scrape it and store it
        scrape_and_store_data(prev_date.strftime('%Y-%m-%d'))

    # Redirect to the home page with the previous day's date
    return redirect(url_for('home', date=prev_date.strftime('%Y-%m-%d')))
    
# Define a route for the next day button
@app.route("/next_day")
def next_day():
    # Get the current date from the URL parameter, or use today's date if no parameter is provided
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = today

    # Calculate the next day's date
    next_date = date + timedelta(days=1)

    # Check if the next day's data is already in the database
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM matches WHERE date = '{next_date}'")
    next_match_data = cursor.fetchall()
    cursor.close()

    if not next_match_data:
        # If the data for the next day is not in the database, scrape it and store it
        scrape_and_store_data(next_date.strftime('%Y-%m-%d'))

    # Redirect to the home page with the next day's date
    return redirect(url_for('home', date=next_date.strftime('%Y-%m-%d')))

if __name__ == "__main__":
    app.run()

