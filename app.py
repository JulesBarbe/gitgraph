from flask import Flask, render_template, redirect, session
from datetime import datetime
from data import fetch_demo_data, fetch_contribution_data, fetch_acct_creation_date
from collections import defaultdict
import secrets

# remove later
import os

app = Flask(__name__)

# secret key for sessions
# env generated on server when deployed on vps?
# could generate as part of startup script :)
# regenerate on restart -> sessions are cleared 
app.secret_key = secrets.token_hex(16)

# can use expiringdict or similar solution later
# in-memory token storage ds is fine; ok with token being lost on restart, already plan on removing when user signed out
# github token gets put here after github oauth
# TODO add ttl
token_store = {}

# github data store per username
# username : {year: {weekday: {date: count, level}}}
# TODO add ttl [faster than token?]
data_store = defaultdict(dict)


# root
# renders dummy data if not logged in, still interactive
@app.route('/')
def index():
    user_state = {
        'logged_in': session.get('logged_in', False),
        'username': session.get('github_username', None),
        'start_year': session.get('acct_creation_year', 2008)
    }

    curr_year = datetime.now().year
    
    if user_state['logged_in']:
        graph_data = data_store[user_state['username']][curr_year]
        print('graph data')
    else:
        graph_data = fetch_demo_data(curr_year)
        print('demo data')

    return render_template('index.html',
                        user_state=user_state,
                        graph_data=graph_data,
                        end_year=curr_year)

# htmx endpoint to fetch graph data for a specific year
@app.route('/api/graph/<int:year>')
def get_graph_data(year):
    user_state = {
        'logged_in': session.get('logged_in', False),
        'username': session.get('github_username', None),
        'start_year': session.get('acct_creation_year', 2008)
    }

    if user_state['logged_in']:
        username = user_state['username']

        if year in data_store[username]:
            graph_data = data_store[username][year]

        else:
            token = token_store.get(username)

            if token:

                graph_data = fetch_contribution_data(token, username, year)
                # update data_store
                data_store[username][year] = graph_data

            else:
                return {'error': 'No github token available'}, 401

    else:
        graph_data = fetch_demo_data(year)
    
    return {'year': year, 'graph_data': graph_data}


@app.route('/login')
def login():
    # OAuth here
    # update session info for users (missing token, github username, ...)
    github_username = 'JulesBarbe'
    session['github_username'] = 'JulesBarbe'
    github_token = os.getenv('GITHUB_SCRIPT_TOKEN')
    token_store[github_username] = github_token
    session['logged_in'] = True

    # fetch github account creation date
    print('fetching acct creation date')
    acct_creation_year = fetch_acct_creation_date(github_token, github_username)
    session['acct_creation_year'] = acct_creation_year
    
    # fetch contribution data for current year before refresh
    print('fetching graph data')
    curr_year = datetime.now().year
    graph_data = fetch_contribution_data(github_token, github_username, curr_year)
    print(graph_data)
    data_store[github_username][curr_year] = graph_data

    return redirect('/')

@app.route('/logout')
def logout():
    username = session.get('github_username')
    if username and username in token_store:
        token_store.pop(username)
        print(f'Cleared token for username {username}')
    else:
        print(f'User already logged out')
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)