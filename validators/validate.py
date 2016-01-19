from git import Repo
import subprocess
import os


REPO_PATH = os.getenv('REPO_PATH', os.path.dirname(os.path.realpath(__file__)))

repo = Repo(REPO_PATH)

for commit in repo.iter_commits('master'):
    print(commit.hexsha, commit.parents, '=' * 50)
    # print(repo.git.show(commit.hexsha))
    for p in commit.parents:
        repo.git.checkout(p.hexsha)
        with open(repo.working_tree_dir + '/validate.py') as f:
            print('-' * 25)
            # print(f.read())
            proc = subprocess.Popen(['pypy-sandbox', '--tmp', repo.working_tree_dir, 'validate.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            try:
                outs, errs = proc.communicate(input=repo.git.show(commit.hexsha), timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
                outs, errs = proc.communicate()
            print(outs, errs)
