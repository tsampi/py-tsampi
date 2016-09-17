#!/usr/bin/env python3

from git import Repo, GitCommandError
import uuid
import random
import glob
import subprocess
import gnupg
import os
import logging
import json
import cgitb
import tempfile
from django.conf import settings
from django.core.cache import cache

cgitb.enable(format='text', context=10)


def here(x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), x)


# os.environ['GNUPGHOME'] = here('keys')

# this module
me = os.path.splitext(os.path.split(__file__)[1])[0]


logger = logging.getLogger(__name__)


# repo.git.config('gpg.program', here('./gpg-with-fingerprint'))
# gpg = gnupg.GPG(homedir=here('keys'))


def randomly(seq):
    shuffled = list(seq)
    random.shuffle(shuffled)
    return iter(shuffled)


def validate(repo_path, branch='master'):
    repo = Repo(repo_path)

    # There should be only one root commit
    root_commits = repo.git.rev_list('--max-parents=0', 'HEAD').splitlines()
    if len(root_commits) > 1:
        raise Exception('Too many root commits: %s.' % root_commits)

    # Why randomly? Arguable this is premature optimization.
    # But if we consistantly iterate over commits in order, they will also expire in order.
    # suffling them will allow other workers to validate_commit before (or after)
    # the cache has expired.
    for commit in randomly(repo.iter_commits(branch)):
        errors = validate_commit(repo_path, commit)
        valid = errors == {}
        if not valid:
            yield False, commit
        else:
            yield True, commit
    repo.git.checkout(branch)


def refresh_gpg_keys(repo_path):
    '''Removes all keys then load the keys in the current repo'''

    # Super inefficient but it's ok for now
    gpg = gnupg.GPG()
    fingerprints = [k['fingerprint'] for k in gpg.list_keys()]
    gpg.delete_keys(fingerprints)
    keys_path = os.path.join(repo_path, 'keys/*')
    for key_path in glob.glob(keys_path):
        with open(key_path) as f:
            logger.info('loading key: %s', key_path)
            gpg.import_keys(f.read())


def validate_commit(repo_path, commit):

    repo = Repo(repo_path)
    # print(repo.git.show(commit.hexsha))

    repo.git.config('--global', 'gpg.program', here('../../gpg-with-fingerprint'))

    if isinstance(commit, str):
        commit = repo.commit(commit)

    cached_validation = cache.get(commit.hexsha)
    logger.info('cached_validation: %s', cached_validation)
    if cached_validation is not None:  # Could be an empty dict, should clean that up
        return cached_validation

    # Load keys from repo
    refresh_gpg_keys(repo_path)

    # is it a valid signiture
    try:
        repo.git.verify_commit(commit.hexsha)
        logger.debug('Valid signiture! {}'.format(commit.hexsha))
    except Exception as e:
        logger.warn(
            'Oh noes! Invalid gpg signiture {} Error: {}'.format(commit.hexsha, e))

    for p in commit.parents:
        logger.info(p.hexsha)
        repo.git.checkout(p.hexsha)
        validate_input = repo.git.show(
            commit.hexsha, c=True, show_signature=True, no_abbrev=True)
        process = subprocess.Popen(['pypy-sandbox',
                                    '--tmp',
                                    repo.working_tree_dir,
                                    'tsampi', 'validate'],
                                   universal_newlines=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        raw_out, raw_err = process.communicate(input=validate_input)

        logger.info('=' * 10)
        logger.info(validate_input)
        logger.info('=' * 10)
        logger.info('out: %s', raw_out)
        logger.info('err: %s', raw_err)
        logger.info('=' * 10)
        out = json.loads(raw_out)
        # no news is good news
        if out:
            logger.info('Invalid Commit: %s\t parent: %s', commit, p)
            logger.info(out)
            return out

    logger.info('Valid Commit!, %s', commit)
    return_value = {}  # TODO: make this somethign useful
    cache.set(commit.hexsha, return_value)
    return return_value


def generate_key():
    NAME = input("Name: ")
    NAME_EMAIL = input('Email: ')
    #EXPIRE_DATE = '2016-05-01'
    KEY_TYPE = 'RSA'
    KEY_LENGTH = 2048
    KEY_USAGE = 'sign,encrypt,auth'
    allparams = {'name_real': NAME,
                 'name_email': NAME_EMAIL,
                 #'expire_date': EXPIRE_DATE,
                 'key_type': KEY_TYPE,
                 'key_usage': KEY_USAGE,
                 'key_length': KEY_LENGTH,
                 }
    gpg = gnupg.GPG()
    batchfile = gpg.gen_key_input(**allparams)

    key = gpg.gen_key(batchfile)
    fingerprint = key.fingerprint

    if not fingerprint:
        logger.error("Key creation seems to have failed: %s" % key)
        return None, None
    return key, fingerprint


def zeros(repo_path):
    repo = Repo(repo_path)

    added = 0
    removed = 0
    for line in repo.git.diff().splitlines():
        logger.info(line.strip())
        if line.startswith("+"):
            added += len(line)

        if line.startswith("-"):
            removed += len(line)

    changes = removed + added
    leading_zeros = len(str(changes)) * '0'
    logger.info("Changes: %", changes)
    return leading_zeros


def merge_from_peer(repo_uri, peer_uri, push=False, key=None, user='user', email='user@localhost'):
    with tempfile.TemporaryDirectory() as tmp_path:
        logger.info('tmp git merge repo: %s', tmp_path)
        repo = Repo.clone_from(repo_uri, tmp_path)
        repo.config_writer().set_value(section='user', option='name', value='foo').set_value(
            section='user', option='email', value='foo@bar.com').release()

        sign = None
        if key:
            repo.config_writer().set_value(
                section='user', option='signingkey', value=key).release()
            sign = '-S'

        # In the event of a merge conflict, our branch is to pre brefered over theirs.
        # This is arguably betteer, but will work for now.
        repo.git.pull(peer_uri, '--no-edit', sign, '-X', 'ours')

        print(repo.git.log('--graph'))
        try:
            validation_results = list(validate(repo.working_tree_dir))
            if not all(v for v, c in validation_results):
                logger.debug(
                    'Invalid commit error on remote:{} \n{}'.format(peer_uri, validation_results))
                return False
        except Exception as e:
            logger.exception(
                'Validation Exception on remote:{}\n{}'.format(peer_uri, e))
            return False
        if push:
            logger.info('Attempting to push')
            push_repo(repo.working_tree_dir, attempts=10)
        return True


def call_tsampi_chain(repo_uri, app=None, jsonrpc=None, commit=False, push=False, user='user', email='user@localhost'):
    errors = {}
    rpc_out = ''
    diff = ''
    try:
        with tempfile.TemporaryDirectory() as tmp_path:
            logger.info('tmp git repo: %s', tmp_path)
            cloned_repo = Repo.clone_from(repo_uri, tmp_path, depth=2)
            rpc_out, diff = tsampi_chain(
                cloned_repo.working_tree_dir, app, jsonrpc)
            # There should be something to commit
            if commit and diff:
                key = settings.TSAMPI_GPG_FINGERPRINT
                success, errors = make_commit(cloned_repo.working_tree_dir, key=key, user=user, email=email)
                if push and success:
                    try:
                        #import IPython; IPython.embed()
                        push_repo(cloned_repo.working_tree_dir, attempts=10)
                    except (Exception, GitCommandError) as e:
                        # push this to a branch and raise
                        new_branch = 'failed-%s' % uuid.uuid4()
                        push_info = cloned_repo.remotes.origin.push(
                            'master:' + new_branch)
                        errors = {'git': 'Failed pushhing'}
    except (Exception, GitCommandError) as e:
        errors['git'] = e
        logging.exception('Could not call tsampi chain')

    return {'rpc_response': rpc_out, 'diff': diff, 'tsampi_errors': errors}


def tsampi_chain(repo_path, app=None, jsonrpc=None):
    # shallow clone of repo
    # All interaction with the sandbox should be with a freshly cloned repo.
    repo = Repo(repo_path)
    app_and_rpc = []
    if app:
        app_and_rpc.append(app)
    if jsonrpc and app:
        app_and_rpc.extend(['--jsonrpc',  json.dumps(jsonrpc)])

    print(os.path.join(repo.working_tree_dir, './tsampi/pypy/'))
    out = subprocess.check_output([settings.TSAMPI_SANDBOX_EXEC,
                                   '--tmp',
                                   repo.working_tree_dir,
                                   '--lib_root',
                                   os.path.join(
                                       repo.working_tree_dir, './tsampi/pypy/'),
                                   'tsampi', 'apps'] + app_and_rpc,
                                  universal_newlines=True,
                                  timeout=settings.TSAMPI_TIMEOUT,
                                  )
    repo.git.add(repo.working_tree_dir)
    diff = repo.git.diff(cached=True)
    logger.info('=' * 10)
    logger.info('app: %s' % app)
    logger.info('jsonrpc: %s' % jsonrpc)
    logger.info('=' * 10)
    logger.info('out: \n' + out)
    logger.info('=' * 10)
    logger.info(diff)
    logger.info('=' * 10)
    return json.loads(out), diff


def make_commit(repo_path, key=None, user='user', email='user@localhost'):
    repo = Repo(repo_path)
    repo.git.config('--global', 'gpg.program', here('../../gpg-with-fingerprint'))
    # if not key:
    #    key = assert_keys()
    repo.config_writer().set_value(section='user', option='name', value=user).set_value(
        section='user', option='email', value=email).release()

    if key:
        repo.config_writer().set_value(
            section='user', option='signingkey', value=key).release()

    for i in range(0, 10000):
        repo.git.add('.')
        if key:
            sign = "-S"
        else:
            sign = None

        try:
            repo.git.commit("-a", sign, "-m", str(i))
        except GitCommandError as e:
            logger.info(e)
            return False, {'git': str(e)}
        #import IPython; IPython.embed()

        sha = repo.head.commit.hexsha
        logger.info("sha: %s, %s", sha, i)

        errors = validate_commit(repo_path, repo.head.commit)
        logger.info('errors %s', repr(errors))
        if errors == {}:  # no problems!
            logger.info('done commiting')
            repo.git.checkout('master')
            return True, errors

        # Try again for proper POW
        repo.git.checkout('master')
        repo.git.reset('HEAD~')

        # Just kidding, somethign else wrong happened, bail out
        if errors != {'pow': False}:
            logger.info('not going to try anymore')
            return False, errors

    # POW was too difficult
    return False, errors


def push_repo(repo_path, attempts=10):
    repo = Repo(repo_path)
    for i in range(attempts):
        repo.remotes.origin.pull('master', no_edit=True)
        push_info = repo.remotes.origin.push('master')
        if push_info:
            # If there was not an error, don't try again
            if not push_info[0].REJECTED & push_info[0].flags:
                return
    raise Exception(push_info.summary)


# TODO turn this in to fetch, validate, merge.
# Check that both have the same parent.


def pull(repo_path):
    repo = Repo(repo_path)
    for r in repo.remotes:
        try:
            for remote in r.fetch():
                logger.info(r.name, remote)
                try:
                    validation_results = list(validate(remote))
                    if not all(v for v, c in validation_results):
                        logger.debug(
                            'Invalid commit error on remote:{} \n{}'.format(remote, validation_results))
                        continue
                except Exception as e:
                    logger.error(
                        'Validation Exception on remote:{}\n{}'.format(remote, e))
                    continue
                try:
                    repo.git.pull(r.name, 'master')
                except Exception as e:
                    logger.exception(e)
                    repo.git.commit(m='merging conflict', a=True)
        except Exception as e:
            logger.exception(e)
