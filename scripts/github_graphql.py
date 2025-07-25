import requests
import os
from collections import defaultdict

# token with private repo scope for the one you want the dummy commits to be generated in
TOKEN = os.getenv('GITHUB_SCRIPT_TOKEN')

# weekday to num mapping
NUM_TO_WEEKDAY = {
  0: "Sun",
  1: "Mon",
  2: "Tue",
  3: "Wed",
  4: "Thu",
  5: "Fri",
  6: "Sat"
}

# ascii color enum for contribution levels
CONTRIB_COLORS = {
  "NONE": " ",
  "FIRST_QUARTILE": "░",
  "SECOND_QUARTILE": "▒",
  "THIRD_QUARTILE": "▓",
  "FOURTH_QUARTILE": "█"
}

# symbol for out of calendar days / exterior of the graph
OUT_SYMBOL = "X"

# github graphql api request for contributions of given year
def fetch_contributions(name, year, token):
  if not token: 
    raise ValueError("Github token is required")

  # github graphql api query
  query = """
  query($userName: String!, $startDate: DateTime!, $endDate: DateTime!) {
    user(login:$userName) {
      contributionsCollection(from: $startDate, to: $endDate) {
        contributionCalendar {
          weeks {
            contributionDays {
              date
              weekday
              contributionCount
              contributionLevel
            }
          }
        }
      }
    }
  }
  """

  variables = {
    "userName" : name,
    "startDate" : f"{year}-01-01T00:00:00Z",
    "endDate" : f"{year}-12-31T23:59:59Z"
  }

  response = requests.post(
    url='https://api.github.com/graphql', 
    headers={'Authorization': f'Bearer {token}'}, 
    json={'query': query, 'variables': variables}
  )
  response.raise_for_status()

  try:
    data = response.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return data
  except KeyError as e:
    raise ValueError(f"Unexpected API schema error: {e}")

# draw github contribution graph in terminal
def draw_contrib_graph(calendar_data):
  weekday_data = defaultdict(list)
  for week in calendar_data:
    for day in week['contributionDays']:
      weekday = day['weekday']
      weekday_data[weekday].append(CONTRIB_COLORS[day['contributionLevel']])

  # account for first and last few weekdays not fitting in the calendar year
  first_week, last_week = calendar_data[0], calendar_data[-1]
  for i in range(first_week['contributionDays'][0]['weekday']):
    weekday_data[i].insert(0, OUT_SYMBOL)
  for i in range(last_week['contributionDays'][-1]['weekday'] + 1, 7):
    weekday_data[i].append(OUT_SYMBOL)

  # print the graph
  line = " ".join([OUT_SYMBOL] * 55)
  print("    " + line)
  for weekday in sorted(weekday_data.items()):
    print(NUM_TO_WEEKDAY[weekday[0]], OUT_SYMBOL, " ".join(weekday[1]), OUT_SYMBOL)
  print("    " + line)


if __name__ == "__main__":
    data = fetch_contributions('JulesBarbe', 2025, TOKEN)
    draw_contrib_graph(data)