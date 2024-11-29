import os
import subprocess
from datetime import datetime, timedelta
import sys
import requests
import random

def create_github_repo(repo_name, private=True):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not found")
    url = 'https://api.github.com/user/repos'
    headers = {
        'Authorization': f'token {token}' 
    }
    data = {
        'name': repo_name,
        'private': private
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository '{repo_name} successfully created.")
    else:
        print(f"Error creating repository: {response.json}")
        sys.exit(1)
    
def configure_git(name, email):
    subprocess.run(['git', 'config', 'user.name', name])
    subprocess.run(['git', 'config', 'user.emai', email])

def generate_commits(year, freq, repo):
    # Clone repo from github
    subprocess.run(['git', 'clone', f'https://github.com/{GITHUB_USERNAME}/{repo}'])
    print('Sucessfully cloned the repo locally.')
    os.chdir(repo)

    freq_map = {
        'low': 1,
        'medium': 3,
        'high': 6
    }
    max_commits_per_day = freq_map.get(freq.lower(), 1)
    start_date = datetime(year, 1, 1)
    end_date = datetime.now() if year == datetime.now().year else datetime(year, 12, 31)
    delta = timedelta(days=1)

    curr_date = start_date
    while curr_date <= end_date:
        num_commits = random.randint(0, max_commits_per_day)
        for commit_num in range(num_commits):
            # TODO: make the commit messages more fun
            commit_message = f'Commit on {curr_date.strftime("%Y-%m-%d")} #{commit_num + 1}'
            commit_date = curr_date.strftime('%Y-%m-%dT%H:%M:%S')
            # Modify a dummy file
            with open('dummy_file.txt', 'a') as file:
                file.write(f'{commit_message}\n')
            # Stage the changes
            subprocess.run(['git', 'add', 'dummy_file.txt'])
            # Commit with the specified date
            env = os.environ.copy()
            env['GIT_AUTHOR_DATE'] = commit_date
            env['GIT_COMMITTER_DATE'] = commit_date
            subprocess.run(['git', 'commit', '-m', commit_message], env=env)
            print(f"Committed {num_commits} times on {curr_date.strftime('%Y-%m-%d')}")
        curr_date += delta

    # Push the commits to GitHub
    subprocess.run(['git', 'push', 'origin', 'main'])



def main():
    # TODO: validate all of these. either custom function for restricted input or library, or as CLI w/ argparse
    print("Make sure your github personal access token is accessible in your environment variables as GITHUB_TOKEN.")
    global GITHUB_USERNAME
    GITHUB_USERNAME = input("Your github username: ")
    user_name = input("Your Git user.name: ")
    user_email = input("Your Git user.email: ")
    repo_name = input("Enter the name for your new repo: ")
    year = int(input("Enter the year for the commits (e.g. 2022): "))
    frequency = input("Enter the commit frequency (low, medium, high): ")

    create_github_repo(repo_name)
    configure_git(user_name, user_email)
    generate_commits(year, frequency, repo_name)
    print("All done!")


if __name__ == "__main__":
    main()