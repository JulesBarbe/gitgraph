# gitgraph
(placeholder name)
play with and freely modify your github contribution graph.

# description
once you connect to your github account on the website, you gain access and can see your contribution graph for each year. you then have access to separate options and filters to generate new commits across time to fill that graph in the way that you want (days of the week, frequency, etc.)
you can also directly interact with the graph, where every click rotates between different colors for the graph, the way they would reflect on github (this is the main cool feature!)
Because colors are based on quartiles, there will be a 'budget' alloted for each color that the user has to be aware of. E.g., user won't be able to click to the fourth quartile if there are already the max amount of days with it. Left click = go down a color, right click = go up a color (it circles around)

for now, every dummy commit is added into a single repo tied to the service (can change with time to make it more convincing >:)
for now, every commit message is a dummy message (can change with time to make it more convincing, aka messages from a static list, llm gen, ...)

github api only lets you query contribution in one year ranges. therefore each year request has to be made separately.
we therefore save them in a user data storage on the backend (maybe redis later), cleared on ttl/after logout.
cannot be put in session cookies (each year json data is about 30kb, cookies are 4kb)

# tech stack
- frontend: html + htmx + tailwind/css + some vanilla JS for graph logic (canvas?)
- backend: flask / fastAPI + templates 
- sessions: encrypted cookies

# data flow
- user visits site for first time
- site contains dummy contrib data and uninteractble options until they log in
- oauth login w github -> add username, etc. to flask session, github token to token_store
- user redirected to / while backend fetches all github contrib data available
- graph for current year is rendered by htmx
- data for all other years is kept in browser (small) from github creation date to today
- user can iterate through years
- user can click through graph to change colors == contribution quartiles
- user can fill the graph automatically w some sliders and options (e.g. days of the week, frequency, etc.)
- user clicks 'generate' to activate the generation script
- new contribution data sent to backend
- (?) look for repo / create private repo for the service
- generate and add necessary commits to repo and push


# TODOS:
- [x] explore github api 
- [x] graph data modeling
- [ ] static graph renderer (html/css)
- [ ] dynamic graph renderer (canvas)
- [ ] graph logic (vanilla js)
- [ ] actually add stuff locally (tailwind ...)
- [ ] year navigation between different graphs
- [ ] full spa frontend
- [ ] simple flask backend skeleton
- [ ] api endpoints
- [ ] frontend - backend integration
- [ ] oauth flow
- [ ] live github data through oauth
- [ ] graph gen
- [ ] add gunicorn wsgi server and async
- [ ] tests
- [ ] error handling, ux
- [ ] vps deploy
- [ ] payments?



# questions:
- github tos
- rate limit github api use (batch change per year generation, only 10x a day by account?)
- full Oauth flow
- auth token in memory / db / encrypted cookies?

# prerequisities
- have python 3.x installed
- git installed and available in PATH
- github personal token (PAT) with repo scope. keep it secure by making it an environment variable. you can do with `export GITHUB_TOKEN=your_token_here` on Linux/macOS or with `set GITHUB_TOKEN=your_token_here` in Windows cmd or `$env:GITHUB_TOKEN = "your_token_here"` in Windows powershell.

