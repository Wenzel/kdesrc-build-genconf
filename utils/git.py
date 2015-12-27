import os
import git
import logging

# Git related functions
def update_repo(url, dest):
    logging.debug('[GIT] updating repo {} from {}'.format(dest, url))
    # test if dest repo exists
    if os.path.isdir(dest) \
        and os.path.isdir(os.path.join(dest, '.git')):
            logging.debug('[GIT] is a git repository')
            logging.debug('[GIT] pulling')
            # git pull !
            repo = git.Repo(dest)
            repo.remotes.origin.pull()
    else:
        logging.debug('[GIT] cloning')
        # we can clone the repo for the first time
        repo = git.Repo.clone_from(url, dest)

def update_submodules(dest):
    repo = git.Repo(dest)
    for s in repo.submodules:
        logging.debug('[GIT] updating submodule {} in {}'.format(s.name, dest))
        s.update()
