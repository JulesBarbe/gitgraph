import requests
import os
import argparse
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

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

def main():
  parser = argparse.ArgumentParser(description="Fetch your GitHub contribution graph in the terminal")
  parser.add_argument('username', help='Github username')
  parser.add_argument('--year', '-y', type=validate_year, default=datetime.now().year, help='Year to fetch (defaults to current year)')
  parser.add_argument('--token', '-t', type=str, help='Github token with private and public repo read access (can also be stured in GITHUB_SCRIPT_TOKEN env var)')

  args = parser.parse_args()

  load_dotenv()

  token = args.token or os.getenv('GITHUB_SCRIPT_TOKEN')
  if not token:
    print("Error: GitHub token required (--token or GITHUB_SCRIPT_TOKEN env variable)")
    return

  contrib_data = fetch_contributions(args.username, args.year, token)
  draw_contrib_graph(contrib_data)

  
def validate_year(value):
  year = int(value)
  if year < 2008 or year > datetime.now().year:
    raise argparse.ArgumentError("Year passed is invalid")
  return year

# github graphql api request for contributions of given year
def fetch_contributions(name, year, token):

  # github graphql api query
  query = """
    query($userName: String!, $startDate: DateTime!, $endDate: DateTime!) {
      user(login:$userName) {
        createdAt,
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

  # json response here is about 34kb
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
    main()