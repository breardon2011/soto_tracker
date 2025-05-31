import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_spotrac_position_salaries(position_code='c', year=2025, bench=False):
    url = f"https://www.spotrac.com/mlb/rankings/player/_/year/{year}/position/{position_code}/sort/cash_total"

    if bench: 
        url=f"https://www.spotrac.com/mlb/rankings/player/_/year/2025/sort/cash_total"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers)
    #print(response.status_code)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch Spotrac page: HTTP {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    player_items = soup.select('li.list-group-item, li.list-group-item-secondary')

    #print(player_items)

    players = []
    for item in player_items:
        name_tag = item.select_one('.link a')
        salary_tag = item.select_one('span.medium')

        if name_tag and salary_tag:
            name = name_tag.get_text(strip=True)
            salary_text = salary_tag.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                salary = float(salary_text)
            except ValueError:
                salary = None
            players.append({'Name': name, 'Salary': salary})

    return pd.DataFrame(players)

# # Example usage
# catcher_salaries = scrape_spotrac_position_salaries('c', 2025)
# print(catcher_salaries.head())
