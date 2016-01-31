#!/usr/bin/env python3
"""Tsampi.

Usage:
  tsampi.py init GIT_URL [--path=<path>]
  tsampi.py add NAME GIT_URL  [--path=<path>]
  tsampi.py remove NAME [--path=<path>]
  tsampi.py fetch [--path=<path>]
  tsampi.py push [--path=<path>]
  tsampi.py verify [--path=<path>]
  tsampi.py merge [--path=<path>]

Options:
  -h --help     Show this screen.
  --version     Show version.
  --path=<path> Path to Tsampi dir (default: .tsampi/repo)
"""

from docopt import docopt
from git import Repo

TSAMPI_HOME = '.tsampi/repo'


def init(git_url):
    repo = Repo.init(TSAMPI_HOME)
    origin = repo.create_remote('origin', git_url)
    origin.fetch()
    repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master)


def add_peer(name, git_url):
    repo = Repo(TSAMPI_HOME)
    repo.create_remote(name, git_url)


def remove_peer(name):
    repo = Repo(TSAMPI_HOME)
    repo.delete_remote(name)


def fetch():
    repo = Repo(TSAMPI_HOME)
    for remote in repo.remotes:
        remote.fetch()


def push():
    repo = Repo(TSAMPI_HOME)
    repo(push)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')

    print(arguments)
    if arguments['init']:
        init(git_url=arguments['GIT_URL'])

    if arguments['add']:
        add_peer(name=arguments['NAME'], git_url=arguments['GIT_URL'])

    if arguments['remove']:
        remove_peer(name=arguments['NAME'])

    if arguments['fetch']:
        fetch()


