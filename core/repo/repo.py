from core.util import git
import os

class Repo:
    def __init__(self, data):
        self.url = data["url"]
        self.directory = data["local_dir"]
        self.directory = os.path.join(os.getcwd(), self.directory)
        self.dirname = os.path.dirname(self.directory)
        self.branch = data["branch"]
        if "lock" in data:
            self.lock = data["lock"]
        else:
            self.lock = True
        self.name = os.path.basename(self.directory)
        self.tag = None

    def clone(self, verbose=False):
        git.clone(self, verbose)

    def clean(self):
        git.clean(self)

    def add_tag(self, tag):
        git.add_tag(self, tag)

    def viewTags(self):
        return git.viewTags(self)

    def checkout(self, branch):
        git.checkout(self, branch)

    def checkout_tag(self, tag):
        git.checkout_tag(self, tag)

    def checkBranch(self):
        git.check_branch(self)

    def push(self):
        git.push(self)

    def update(self):
        return git.update(self)
