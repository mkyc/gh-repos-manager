import os

from github import Github

g = Github(os.environ['TOKEN'])

for repo in g.get_organization(os.environ['ORG']).get_repos():
    print(repo.name)
