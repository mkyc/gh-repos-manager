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
        for _label in j['labels']:
            self.labels.append(MyLabel(_label))
        self.name = j['name']


def remove_label_from_repository(_label: Label, _repository: MyRepository):
    print("(%s) label should be not there, will delete: %s" % (_repository.name, _label.name))
    try:
        _label.delete()
    except GithubException as exception:
        print("Wasn't able to delete label (%s): %s" % (exception.status, exception.data))
        exit(1)


def create_label_in_repository(_repository: Repository, _label: MyLabel):
    print("(%s) label not found, will create: %s" % (_repository.name, _label.name))
    try:
        _repository.create_label(_label.name, _label.color, _label.description)
    except GithubException as exception:
        print("Wasn't able to create label (%s): %s" % (exception.status, exception.data))
        exit(1)


def is_label_unused(_label: Label, _repository: Repository) -> bool:
    try:
        _gh_labels = _repository.get_issues(labels=[_label.name])
        if _gh_labels.totalCount != 0:
            return False
        else:
            return True
    except GithubException as exception:
        print("Wasn't able to get issues filtered by label  %s: (%s) %s" % (
            _label.name, exception.status, exception.data))
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
                if is_label_unused(label, ghr):
                    remove_label_from_repository(label, repo)
                else:
                    print("Label %s is used and will not be removed by automation" % label.name)
    except GithubException as e:
        print("repo %s not found!" % repo.name)
