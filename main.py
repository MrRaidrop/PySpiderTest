import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta


def get_match_result(team_divs):
    match_results = []
    team_data = []
    for div in team_divs:
        score_elem = div.find('div', class_='txt')
        if score_elem is None:
            continue  # If no score is found, skip this div
        score_trans = score_elem.find('span', class_=lambda x: x and 'num' in x)
        if score_trans is None:
            continue  # If no score is found, skip this div
        score = score_trans.text.strip()
        team_name = div.find('div', class_='txt').find('a').text.strip()
        if(team_name in team_data):
            continue
        team_data.append(team_name)
        match_results.append({team_name, score})
    return match_results


today = datetime.today().date()

start_date = today - timedelta(days=10)
end_date = today

while start_date <= end_date:
    date = start_date.strftime("%Y-%m-%d")
    url = f'http://nba.hupu.com/games/{date}'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Find the element containing the match data
    match_data = soup.find('div', class_='gamecenter_content_l')

    # Find all the div elements containing the team names and scores
    team_divs = match_data.find_all('div', class_=lambda x: x and 'team_vs' in x)

    match_results = get_match_result(team_divs)

    # Create a list of dictionaries with the team name and score
    match_data_list = []
    for i in range(0, len(match_results), 2):
        team_a, score_a = [s.strip() for s in list(match_results[i]) if s.strip()]
        team_b, score_b = [s.strip() for s in list(match_results[i+1]) if s.strip()]
        if team_a.isdigit():
            team_a, score_a = score_a, team_a
        if team_b.isdigit():
            team_b, score_b = score_b, team_b
        match_data_list.append({'Team': team_a, 'Score': score_a})
        match_data_list.append({'Team': team_b, 'Score': score_b})
        match_data_list.append({})  # Add a blank row

    # Create a dataframe with the match data
    df = pd.DataFrame(match_data_list)

    # Write the dataframe to an Excel file
    writer = pd.ExcelWriter(f'match_results_{date}.xlsx')
    df.to_excel(writer, index=False)
    writer.save()

    start_date += timedelta(days=1)