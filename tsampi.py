#!/usr/bin/env python3
"""Tsampi.

Usage:
  tsampi.py validate
  tsampi.py commit path
  tsampi.py pull
  tsampi.py push

Options:
  -h --help     Show this screen.
  --version     Show version.
  --path=<path> Path to Tsampi dir (default: .tsampi/repo)
"""

from docopt import docopt
from git import Repo
import subprocess
import gnupg
import os
import logging


def here(x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

os.environ['GNUPGHOME'] = here('keys')

TSAMPI_HOME = here('./repos/tsampi-0')
gpg = gnupg.GPG(homedir=here('keys'))
TIMEOUT = 1
MY_KEY = None


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


repo = Repo(TSAMPI_HOME)
repo.git.config('gpg.program', here('./gpg-with-fingerprint'))


def validate(branch='master'):
    for commit in repo.iter_commits(branch):
        valid = validate_commit(commit)
        if not valid:
            break


def validate_commit(commit):
    # print(repo.git.show(commit.hexsha))

    # is it a valid signiture
    try:
        repo.git.verify_commit(commit.hexsha)
        print('Valid commit! {}'.format(commit.hexsha))
    except Exception as e:
        logger.error('Commit: {}\nError: {}'.format(commit.hexsha, e))

    for p in commit.parents:
        repo.git.checkout(p.hexsha)
        # print('-' * 25)
        out = subprocess.check_output(['pypy-sandbox',
                                       '--tmp',
                                       repo.working_tree_dir,
                                       'validate.py'],
                                      universal_newlines=True,
                                      input=repo.git.show(
            commit.hexsha, c=True),
            timeout=TIMEOUT,
            stderr=subprocess.STDOUT)
        if '[Subprocess exit code: 1]' in out:
            # print(commit.hexsha, commit.parents, '=' * 10)
            # print('------')
            # print(repo.git.show(commit.hexsha, c=True))
            # print('-------')
            print(out)
            return False

    return True


def generate_key():
    NAME = input("Name")
    NAME_EMAIL = input('Email')
    EXPIRE_DATE = '2016-03-01'
    KEY_TYPE = 'RSA'
    KEY_LENGTH = 1024
    KEY_USAGE = 'sign,encrypt,auth,cert'
    allparams = {'name_real': NAME,
                 'name_email': NAME_EMAIL,
                 'expire_date': EXPIRE_DATE,
                 'key_type': KEY_TYPE,
                 'key_usage': KEY_USAGE,
                 'key_length': KEY_LENGTH,
                 }
    batchfile = gpg.gen_key_input(**allparams)

    key = gpg.gen_key(batchfile)
    fingerprint = key.fingerprint

    if not fingerprint:
        logger.error("Key creation seems to have failed: %s" % key.status)
        return None, None
    return key, fingerprint


def zeros():
    added = 0
    removed = 0
    for line in repo.git.diff().splitlines():
        print(line.strip())
        if line.startswith("+"):
            added += len(line)

        if line.startswith("-"):
            removed += len(line)

    changes = removed + added
    leading_zeros = len(str(changes)) * '0'
    print("Changes: ", changes)
    return leading_zeros


def commit(path='.', key=None):
    leading_zeros = zeros()
    if not key:
        key = assert_keys()
    for i in range(0, 10000):
        repo.git.add(path)
        repo.git.commit(m=i, gpg_sign=key)
        sha = repo.head.commit.hexsha
        print(sha, i)
        if sha.startswith(leading_zeros):
            return
        repo.git.reset('HEAD~')


def push():
    repo.git.push()


# TODO turn this in to fetch, validate, merge.
# Check that both have the same parent.

def pull():
    for r in repo.remotes:
        try:
            for remote in r.fetch():
                print(r.name, remote)
                try:
                    validate(remote)
                except Exception as e:
                    logger.error('Validation error on remote:{}\n{}'.format(remote, e))
                    continue
                try:
                    repo.git.pull(r.name, 'master')
                except Exception as e:
                    print(e)
                    repo.git.commit(m='merging conflict', a=True)
        except Exception as e:
            logger.exception(e)


def assert_keys():
    if len(gpg.list_keys()) == 0:
        print("Hey there, seems like you have not created your Tsampi ID")
        key, fingerprint = generate_key()

    fingerprint = gpg.list_keys()[0]['fingerprint']
    public_key_path = os.path.join(TSAMPI_HOME, 'keys', fingerprint)

    if not os.path.isfile(public_key_path):
        with open(public_key_path, 'w') as public_key_file:
            public_key_file.write(gpg.export_keys(fingerprint))

        commit(os.path.join('keys', fingerprint), fingerprint)

    return fingerprint


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.0.1')
    assert_keys()

    if arguments['validate']:
        print('Validating')
        validate()

    if arguments['commit']:
        print('commiting')
        commit()

    if arguments['pull']:
        print('pulling')
        pull()

    if arguments['push']:
        print('pushing')
        push()
