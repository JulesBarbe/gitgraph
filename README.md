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
- frontend: tailwind/css + vanilla js/css for graph + alpine for basic logic
- backend: flask / fastAPI + templates 
- sessions: encrypted cookies

# data flow
- user visits site for first time
- site contains demo contrib data. graph is interactive n stuff, but can't be generated.
- oauth login w github -> add username, etc. to flask session, github token to token_store
- user redirected to / while backend fetches current year of contrib data and account creation data
- graph for current year now rendered
- user can iterate through years from acct creation to current. unseen contrib data gets fetched and cached locally.
- user can click through graph to change colors == contribution quartiles
- user can fill the graph automatically w some sliders and options (e.g. days of the week, frequency, etc.)?
- user clicks 'generate' when happy. current year is unomdifiable while generation ongoing.
- new contribution data sent to backend -> generation script dispatched (dummy commits in private repo -> pushed)
- user gets notified when generation for year x successful


# TODOS:
- [x] explore github api 
- [x] graph data modeling
- [x] simple flask backend skeleton
- [x] main api endpoints
- [x] static graph renderer (html/css)
- [x] graph logic (vanilla js)
- [x] year navigation between different graphs
- [x] optimizations (dynamic level counting and validation, fresh graph or diff based for clearing)
- [x] better loading animation -> bouncing cells?
- [x] complete validation (future and preaccount days, possible quartile combinations, etc)
- [x] add sliders and options
- [x] add info popup
- [x] frontend code refactor (clarity, better use of alpine tools)
- [ ] actual slider etc. generation (respecting quartiles)
- [ ] oauth flow
- [ ] generation api
- [ ] actually add stuff locally (tailwind ...)
- [ ] live github data through oauth
- [ ] graph gen
- [ ] redis instead of python dicts lol
- [ ] add gunicorn wsgi server and async
- [ ] tests
- [ ] error handling, ux
- [ ] vps deploy
- [ ] payments?
- [ ] way down the line ... rewrite in rust w/ tokio, axios, well typed stuff, protobuffs?



# questions:
- rate limit github api use (batch change per year generation, only 10x a day by account?)
- full Oauth flow
- auth token in memory / db / encrypted cookies?
- demo data fully local in frontend? like separate json for 2-3 years?
- private repo name

# prerequisities
- have python 3.x installed
- git installed and available in PATH
- github personal token (PAT) with repo scope. keep it secure by making it an environment variable. you can do with `export GITHUB_TOKEN=your_token_here` on Linux/macOS or with `set GITHUB_TOKEN=your_token_here` in Windows cmd or `$env:GITHUB_TOKEN = "your_token_here"` in Windows powershell.

# disclaimer
This tool is intended solely for personal use and experimentation. It allows users to visualize and simulate GitHub contribution graphs by generating dummy commits in private repositories. These simulated contributions are not actual code contributions and do not reflect real-world activity. Using this tool to misrepresent your activity to others, including potential employers, is strictly prohibited and may violate GitHub’s Terms of Service. By using this tool, you agree to use it responsibly and acknowledge that any misuse is at your own risk.

