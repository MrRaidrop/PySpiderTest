import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from get_match import get_match_result

url = 'http://nba.hupu.com/games/2023-03-24'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

# Set the start and end dates
today = datetime.today().date()

start_date = today - timedelta(days=10)
end_date = today

# Find the element containing the match data
match_data = soup.find('div', class_='gamecenter_content_l')

# Find all the div elements containing the team names and scores
team_divs = match_data.find_all('div', class_=lambda x: x and 'team_vs' in x)

match_results = get_match_result(team_divs)

# Create a list of dictionaries with the team name and score
match_data = []
for i in range(0, len(match_results), 2):
    team_a, score_a = [s.strip() for s in list(match_results[i]) if s.strip()]
    team_b, score_b = [s.strip() for s in list(match_results[i+1]) if s.strip()]
    if team_a.isdigit():
        team_a, score_a = score_a, team_a
    if team_b.isdigit():
        team_b, score_b = score_b, team_b
    match_data.append({'Team': team_a, 'Score': score_a})
    match_data.append({'Team': team_b, 'Score': score_b})
    match_data.append({})  # Add a blank row

# Create a dataframe with the match data
df = pd.DataFrame(match_data)

# Write the dataframe to an Excel file
writer = pd.ExcelWriter('match_results{date}.xlsx')
df.to_excel(writer, index=False)
writer.save()
