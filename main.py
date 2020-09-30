import os
import yamale
from github import Github, GithubException
from github.Label import Label
from github.Repository import Repository
from yamale import YamaleError


class MyLabel(object):
    def __init__(self, y):
        self.name = y['name']
        self.description = y['description']
        self.color = y['color']


class MyRepository(object):
    labels = []

    def __init__(self, j):
        for label in j['labels']:
            self.labels.append(MyLabel(label))
        self.name = j['name']


def remove_label_from_repository(label: Label, repository: MyRepository):
    print("(%s) label should be not there, will delete: %s" % (repository.name, label.name))
    try:
        label.delete()
    except GithubException as exception:
        print("Wasn't able to delete label (%s): %s" % (exception.status, exception.data))
        exit(1)


def create_label_in_repository(repository: Repository, label: MyLabel):
    print("(%s) label not found, will create: %s" % (repository.name, label.name))
    try:
        repository.create_label(label.name, label.color, label.description)
    except GithubException as exception:
        print("Wasn't able to create label (%s): %s" % (exception.status, exception.data))
        exit(1)


schema = yamale.make_schema(content="""
name: str()
repos: list(include('repo'), min=1)
---
repo:
    name: str()
    labels: list(include('label'), min=0)
---
label: 
    name: str()
    description: str()
    color: str()
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
repos = [MyRepository(i) for i in data[0][0]['repos']]

g = Github(os.environ['TOKEN'])

for repo in repos:
    try:
        ghr = g.get_organization(org).get_repo(repo.name)
        gh_labels = ghr.get_labels()
        for label in repo.labels:
            if label.name not in [label.name for label in gh_labels]:
                create_label_in_repository(ghr, label)
        for label in gh_labels:
            if label.name not in [label.name for label in repo.labels]:
                remove_label_from_repository(label, repo)
    except GithubException as e:
        print("repo %s not found!" % repo.name)
