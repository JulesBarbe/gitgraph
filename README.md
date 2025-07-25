# gitgraph
(placeholder name)
play with and freely modify your github contribution graph.

# description
once you connect to your github account on the website, you gain access and can see your contribution graph for each year. you then have access to separate options and filters to generate new commits across time to fill that graph in the way that you want (days of the week, frequency, etc.)
you can also directly interact with the graph, where every click rotates between different colors for the graph, the way they would reflect on github (this is the main cool feature!)

for now, every dummy commit is added into a single repo tied to the service (can change with time to make it more convincing >:)
for now, every commit message is a dummy message (can change with time to make it more convincing, aka messages from a static list, llm gen, ...)

# tech stack
- frontend: html + htmx + tailwind/css + some vanilla JS for graph logic (canvas?)
- backend: flask / fastAPI + templates 
- sessions: encrypted cookies

# TODOS:
- [x] explore github api 
- [x] graph data modeling
- [ ] static graph renderer (html/css)
- [ ] dynamic graph renderer (canvas)
- [ ] graph logic (vanilla js)
- [ ] year navigation between different graphs
- [ ] full spa frontend
- [ ] simple flask backend skeleton
- [ ] api endpoints
- [ ] frontend - backend integration
- [ ] oauth flow
- [ ] live github data through oauth
- [ ] graph gen
- [ ] error handling, ux
- [ ] tests
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

