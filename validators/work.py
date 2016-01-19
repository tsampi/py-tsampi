from git import Repo
import os


REPO_PATH = os.getenv('REPO_PATH', os.path.dirname(os.path.realpath(__file__)))
repo = Repo(REPO_PATH)

for commit in repo.iter_commits('master', max_count=50):
    commit_hash = commit.hexsha
    commit.checkout()
    break


