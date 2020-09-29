import os
import yamale
from github import Github, GithubException
from yamale import YamaleError


class Repo(object):
    def __init__(self, j):
        self.labels = j['labels']
        self.name = j['name']


schema = yamale.make_schema(content="""
name: str()
repos: list(include('repo'), min=1)
---
repo:
    name: str()
    labels: list(include('label'), min=0)
---
label: str()
""")

data = yamale.make_data("config.yaml")

try:
    yamale.validate(schema, data)
    print('Validation success! 👍')
except YamaleError as e:
    print('Validation failed!\n')
    for result in e.results:
        print("Error validating data '%s' with '%s'\n\t" % (result.data, result.schema))
        for error in result.errors:
            print('\t%s' % error)
    exit(1)

org = data[0][0]['name']
repos = [Repo(i) for i in data[0][0]['repos']]

g = Github(os.environ['TOKEN'])

for repo in repos:
    try:
        ghr = g.get_organization(org).get_repo(repo.name)
        gh_labels = [label.name for label in ghr.get_labels()]
        for label in repo.labels:
            if label not in gh_labels:
                print("in repo %s label %s not found!" % (repo.name, label))
    except GithubException as e:
        print("repo %s not found!" % repo.name)
