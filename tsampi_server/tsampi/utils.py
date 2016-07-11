#!/usr/bin/env python3

from git import Repo
import subprocess
# import gnupg
import os
import logging
import glob
import random
from hashlib import sha1
import string
import json
import cgitb
from tsampi_server import settings

cgitb.enable(format='text', context=10)


def here(x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), x)


# os.environ['GNUPGHOME'] = here('keys')

TSAMPI_HOME = os.path.expanduser('/code/repos/tsampi-0')
TIMEOUT = 30
# this module
me = os.path.splitext(os.path.split(__file__)[1])[0]


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


repo = Repo(TSAMPI_HOME)
repo.git.config('gpg.program', here('./gpg-with-fingerprint'))
# gpg = gnupg.GPG(homedir=here('keys'))

def reload_repo():
    repo = Repo(TSAMPI_HOME)

def validate(branch='master'):

    for commit in repo.iter_commits(branch):
        valid = validate_commit(commit)
        if not valid:
            yield False, commit
        else:
            yield True, commit
    repo.git.checkout(branch)


def validate_commit(commit):
    # print(repo.git.show(commit.hexsha))

    # is it a valid signiture
    try:
        repo.git.verify_commit(commit.hexsha)
        print('Valid signiture! {}'.format(commit.hexsha))
    except Exception as e:
        logger.debug(
            'Invalid gpg  signiture {} Error: {}'.format(commit.hexsha, e))

    for p in commit.parents:
        repo.git.checkout(p.hexsha)
        validate_input = repo.git.show(
            commit.hexsha, c=True, show_signature=True)
        out = subprocess.check_output(['pypy-sandbox',
                                       '--tmp',
                                       repo.working_tree_dir,
                                       'tsampi', 'validate'],
                                      universal_newlines=True,
                                      input=validate_input,
                                      timeout=TIMEOUT,
                                      stderr=subprocess.STDOUT)
        print('=' * 10)
        print('out: ', '\n'.join(out.splitlines()[1:]))
        print('=' * 10)
        if 'ValidationError' in out:
            # print(commit.hexsha, commit.parents, '=' * 10)
            # print('------')
            # print(repo.git.show(commit.hexsha, c=True))
            # print('-------')
            print('Invalid Commit!', commit)
            return False

    logger.info('Valid Commit!', commit)
    return True


def generate_key():
    NAME = input("Name: ")
    NAME_EMAIL = input('Email: ')
    EXPIRE_DATE = '2016-05-01'
    KEY_TYPE = 'RSA'
    KEY_LENGTH = 1024
    KEY_USAGE = 'sign,encrypt,auth'
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
    # if not key:
    #    key = assert_keys()
    repo.config_writer().set_value(section='user', option='name',value='foo').set_value(section='user', option='email',value='foo@bar.com').release()

    for i in range(0, 10000):
        repo.git.add(path)
        repo.git.commit("-m", str(i))
        sha = repo.head.commit.hexsha
        print(sha, i)
        if validate_commit(repo.head.commit):
            repo.git.checkout('master')
            return
        repo.git.checkout('master')
        repo.git.reset('HEAD~')


def random_bantz_hash():
    paths = glob.glob(os.path.join(TSAMPI_HOME, 'data', '*'))
    if not paths:
        return ""
    filepath = random.choice(paths)
    bantz_hash = os.path.basename(filepath)
    print(bantz_hash)
    return bantz_hash


def all_bantz_hashes():
    filepaths = glob.iglob(os.path.join(TSAMPI_HOME, 'data', '*'))
    for filepath in filepaths:
        bantz_hash = os.path.basename(filepath)
        yield bantz_hash


def get_bantz(bantz_hash):
    with open(os.path.join(TSAMPI_HOME, 'data', bantz_hash), 'rb') as f:
        data = Bencoder.decode(f.read().decode())
    return data


def random_bantz():
    bantz_hash = random_bantz_hash()
    return get_bantz(bantz_hash)


def all_bantz():
    for bantz_hash in all_bantz_hashes():
        yield get_bantz(bantz_hash)


def make_random_data():
    data = ''.join(random.choice(string.printable)
                   for i in range(random.randrange(5, 1000)))
    random_parent = random_bantz_hash()
    return save_bantz(random_parent, data)


def save_bantz(parent_sha1, data):
    bc = Bencoder.encode({'parent_sha1': parent_sha1 or '', 'data': data}).encode()
    name = sha1(bc).hexdigest()
    with open('/home/tim/tsampi-bantz/data/' + name, 'wb') as f:
        f.write(bc)
    return name


def push():
    repo.git.push()


def call_tsampi_chain(app=None, jsonrpc=None):
    app_and_rpc = []

    if app:
        app_and_rpc.append(app)

        if jsonrpc:
            app_and_rpc.extend(['--jsonrpc', jsonrpc])

    out = subprocess.check_output([settings.TSAMPI_SANDBOX_EXEC,
                                   '--tmp',
                                   repo.working_tree_dir,
                                   'tsampi', 'apps']  + app_and_rpc,
                                  universal_newlines=True,
                                  timeout=TIMEOUT,
                                  )
    print('=' * 10)
    print('out: \n' + out)
    print('=' * 10)
    return json.loads(out)

def list_apps():
    return call_tsampi_chain()

# TODO turn this in to fetch, validate, merge.
# Check that both have the same parent.

def pull():
    for r in repo.remotes:
        try:
            for remote in r.fetch():
                print(r.name, remote)
                try:
                    if not all(validate(remote)):
                        logger.debug(
                            'Validation error on remote:{}'.format(remote))
                        continue
                except Exception as e:
                    logger.error(
                        'Validation error on remote:{}\n{}'.format(remote, e))
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


#  ====== SERVER ======
from django.http import HttpResponse
from django.conf.urls import url
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect


DEBUG = True
ROOT_URLCONF = 'bantz'
DATABASES = {'default': {}}
SECRET_KEY = "sadfjnsadkfjn$@G#TBegf2#GrTegravfdgfdNHHWgrebtnwh5ERB"
TEMPLATE_DIRS = [
    here('.')
]
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

import django
django.setup()
from django.views.decorators.csrf import csrf_exempt

def index(request):
    bantz_hash = random_bantz_hash()
    return redirect('/' + bantz_hash)


def bantz_view(request, bantz_hash):
    bantz = get_bantz(bantz_hash)
    context = {'bantz': bantz}
    if request.method == "POST":
        data = request.POST['data']
        parent_sha1 = request.POST['parent_sha1']
        bantz_hash = save_bantz(parent_sha1, data)
        return redirect('/' + bantz_hash)

    return render(request, 'bantz.html', context)



urlpatterns = [
    url(r'^$', index),
    url(r'^(?P<bantz_hash>\w+)?$', bantz_view),
]


