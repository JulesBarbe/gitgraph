import requests
import random
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

# fetch github account creation date
def fetch_acct_creation_date(token, username):
    query = """
        query($userName: String!) {
            user(login:$userName) {
            createdAt
            }
        }
    """
    variables = {
        "userName" : username
    }

    response1 = requests.post(
        url='https://api.github.com/graphql', 
        headers={'Authorization': f'Bearer {token}'}, 
        json={'query': query, 'variables': variables}
    )
    response1.raise_for_status()

    try:
        data = response1.json()['data']['user']
    except KeyError as e:
        print(f"Error w/ query formatting: {e}")

    return data['createdAt']


# fetch contribution data for given year
# returns data on a weekday basis 
def fetch_contribution_data(token, username, year):
    if year < 2008 or year > datetime.now().year:
        print(f"Invalid year request: {year}")
        return

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
        "userName" : username,
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
    except KeyError as e:
        print(f"Error w/ query formatting: {e}")

    # transform data to a weekday basis
    # e.g. {0: [{date: 2025-11-19, count: 3 }, ...]}
    # count = -1 when day does not exist (padding for first/last few days of year)
    weekday_data = defaultdict(list)
    for week in data:
        for day in week['contributionDays']:
            weekday_num = day['weekday']
            weekday_data[weekday_num].append(
                {'date': day['date'], 
                'count': day['contributionCount'], 
                'level': day['contributionLevel'], 
                'og': False if day['contributionLevel'] in ('OUT', 'NONE') else True    # days that can't be regenerated to NONE
            })
            
    # padding for first/last few days of year
    first_week, last_week = data[0], data[-1]
    for i in range(first_week['contributionDays'][0]['weekday']):
        weekday_data[i].insert(0, {'date': day['date'], 'count': -1, 'level': 'OUT'})
    for i in range(last_week['contributionDays'][-1]['weekday'] + 1, 7):
        weekday_data[i].append({'date': day['date'], 'count': -1, 'level': 'OUT'})

    return weekday_data


# return static demo graph data 
def fetch_demo_data(year):
    start_date = datetime(year, 1, 1)
    is_curr_year = (year == datetime.now().year)
    today = datetime.now()

    # calculate number of days in year, taking account leap year and current year up to current date
    if calendar.isleap(start_date.year):
        num_days = 366
    else:
        num_days = 365

    # generate 365 days of contributions (between 0 and 10)
    weekday_data = defaultdict(list)
    all_contribs = []
    curr_date = start_date
    for _ in range(num_days):
        # python datetime weekdays are indexed at 0 on monday (sunday = 6), we want 0 on sunday
        weekday = (curr_date.weekday() + 1) % 7 

        # no contribs for later days this year
        if is_curr_year and curr_date > today:
            contribs = 0
        
        else:
            # weekend -> higher contributions
            if weekday in (6, 0):
                contribs = random.choices(range(0, 10), weights=[80, 10, 5, 3, 2, 1, 1, 1, 1, 1])[0]
            else:
                contribs = random.choices(range(0, 10), weights=[90, 5, 3, 2, 1, 1, 1, 1, 1, 1])[0]
        
        weekday_data[weekday].append({'date': curr_date.strftime('%Y-%m-%d'), 'count': contribs}) # add level later
        all_contribs.append(contribs)
        curr_date += timedelta(days=1)

    # calculate quartiles
    # bastardization of numpy linear interpolation?
    # ignore 0 contribution days (NONE level)
    sorted_counts = sorted([count for count in all_contribs if count > 0])
    n1 = len(sorted_counts)
    n2 = len(sorted_counts) - 1
    k1 = n2 * 0.25
    k2 = n2 * 0.5
    k3 = n2 * 0.75
    f1 = int(k1)
    f2 = int(k2)
    f3 = int(k3)
    c1 = k1 - f1
    c2 = k2 - f2
    c3 = k3 - f3
    q1 = sorted_counts[f1] if f1+1 >= n1 else sorted_counts[f1] + (sorted_counts[f1+1] - sorted_counts[f1]) * c1
    q3 = sorted_counts[f3] if f3+1 >= n1 else sorted_counts[f3] + (sorted_counts[f3+1] - sorted_counts[f3]) * c3
    q2 = sorted_counts[f2] if f2+1 >= n1 else sorted_counts[f2] + (sorted_counts[f2+1] - sorted_counts[f2]) * c2

    # update contribution level based on quartiles
    for weekday in weekday_data.keys():
        for day in weekday_data[weekday]:
            count = day['count']
            if count == 0:
                day['level'] = 'NONE'
            elif count <= q1:
                day['level'] = 'FIRST_QUARTILE'
            elif count <= q2:
                day['level'] = 'SECOND_QUARTILE'
            elif count <= q3:
                day['level'] = 'THIRD_QUARTILE'
            else:
                day['level'] = 'FOURTH_QUARTILE'
    
    # add padding for first week of the year
    first_weekday = (start_date.weekday() + 1) % 7
    for i in range(first_weekday):
        weekday_data[i].insert(0, {'date': '', 'count': -1, 'level': 'OUT'})
    
    # add padding for last week of the year
    last_weekday = (datetime(year, 12, 31).weekday() + 1) % 7
    for i in range(last_weekday+1, 7):
        weekday_data[i].append({'date': '', 'count': -1, 'level': 'OUT'})

    return weekday_data

# helper function for tests
# visualize weekday contribution data graph
def visualize_graph(weekday_data):
    CONTRIB_COLORS = {
        "OUT": "X",
        "NONE": " ",
        "FIRST_QUARTILE": "░",
        "SECOND_QUARTILE": "▒",
        "THIRD_QUARTILE": "▓",
        "FOURTH_QUARTILE": "█"
    }
    NUM_TO_WEEKDAY = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}

    line = " ".join([CONTRIB_COLORS['OUT']] * 55)
    print("    " + line)
    for weekday, data in sorted(weekday_data.items()):
        print(NUM_TO_WEEKDAY[weekday], CONTRIB_COLORS['OUT'], " ".join([CONTRIB_COLORS[day['level']] for day in data]), CONTRIB_COLORS['OUT'])
    print("    " + line)

if __name__ == "__main__":
    username = 'JulesBarbe'
    from dotenv import load_dotenv
    import os
    load_dotenv()
    token = os.getenv('GITHUB_SCRIPT_TOKEN')
    data = fetch_contribution_data(token, username, 2026)
    for wday in data.values():
        print(len(wday))