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