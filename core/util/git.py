import os
import sys
import subprocess
import gpack

ROOT_DIR = os.getcwd()

def rinse(repo):
    """Performs a clean, reset and recursive update to submodules"""
    clean = ["git", "clean", "-xdff"]
    reset = ["git", "reset", "--hard"]
    sub_clean = ["git", "submodule", "foreach", "--recursive", "git",
    "clean", "-xdff"]
    sub_reset = ["git", "submodule", "foreach", "--recursive", "git",
    "reset", "--hard"]
    sub_update = ["git", "submodule", "update", "--init", "--recursive"]
    directory = repo.directory
    branch = "origin/" + repo.branch

    os.chdir(directory)

    try:
        subprocess.check_output(clean, stderr=subprocess.STDOUT)
        subprocess.check_output(reset+[branch], stderr=subprocess.STDOUT)
        subprocess.check_output(sub_clean, stderr=subprocess.STDOUT)
        subprocess.check_output(sub_reset, stderr=subprocess.STDOUT)
        subprocess.check_output(sub_update, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output.decode("utf-8").replace("fatal", "gpack").strip())

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def clean(repo):
    """Performs a clean to submodules"""
    rinse(repo)

def clone(repo, verbose):
    """Spawns terminal for each repo, showing clone output"""
    _name = repo.name
    _url = repo.url
    _dir = repo.directory
    _branch = repo.branch

    os.chdir(repo.dirname)

    if verbose:
        CLONE="git clone --recursive %s %s" % (_url, _name)
        DIR="cd %s" % (_dir,)
        CHECKOUT="git checkout %s" % (_branch,)
        SUB_MODULES="git submodule foreach git checkout %s" % (_branch,)
        COMMAND = "%s && %s && %s && %s" % (CLONE, DIR, CHECKOUT, SUB_MODULES)
        try:
            os.system("xterm -T %s -geometry 90x30 -e \"%s || read -p 'Press return to close window'\"" % (_dir, COMMAND,))
        except subprocess.CalledProcessError as e:
            e = e.output.decode("utf-8")
            if "error" in e:
                print(e.replace("error", "gpack").strip())
            else:
                print(e.replace("fatal", "gpack").strip())
        else:
            print("Successfully installed %s..." % (_name))
    else:
        clone = ["git", "clone", "--recursive"]
        check = ["git", "checkout"]
        sub_check = ["git", "submodule", "foreach", "git", "checkout"]
        try:
            subprocess.check_output(clone+[_url, repo.name], stderr=subprocess.STDOUT)
            os.chdir(_dir)
            subprocess.check_output(check+[_branch],stderr=subprocess.STDOUT)
            subprocess.check_output(sub_check+[_branch],stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            e = e.output.decode("utf-8")
            if "error" in e:
                print(e.replace("error", "gpack").strip())
            else:
                print(e.replace("fatal", "gpack").strip())
        else:
            print("Successfully installed %s..." % (_name))

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def pull(repo):
    os.chdir(repo.directory)  # move to repo dir
    pull = "git pull".split(" ")
    sub = "git submodule update --recursive".split(" ")
    try:
        subprocess.check_output(pull, stderr=subprocess.STDOUT)
        subprocess.check_output(sub, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        e = e.output.decode("utf-8")
        if "error" in e:
            print(e.replace("error", "gpack").strip())
        else:
            print(e.replace("fatal", "gpack").strip())

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def current_branch(repo):
    """Returns the current branch that a repo is on"""
    branch = "git rev-parse --abbrev-ref HEAD".split(" ")
    try:
        process = subprocess.check_output(branch)
    except subprocess.CalledProcessError as e:
        return ""
    return process.decode("utf-8")

def check_branch(repo):
    """Checks the current branch on repo"""
    os.chdir(repo.directory)  # move to repo dir
    branch = current_branch(repo).strip()  # get cur branch
    print("'%s' is currently on branch '%s'" % (repo.name, branch))
    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def push(repo):
    """Push local changes"""

    os.chdir(repo.directory)  # move to repo dir
    branch = current_branch(repo).strip()  # get cur branch

    if(branch == "master"):
        print("%s currently on branch master, can't push" % (repo.name,))
        return

    msg = input("Commit message: ")
    add = ["git", "add", "-A"]
    commit = ["git", "commit", "-m", msg]
    p = ["git", "push", "--set-upstream", "origin", branch.strip()]

    try:
        subprocess.check_output(add, stderr=subprocess.STDOUT)
        subprocess.check_output(commit, stderr=subprocess.STDOUT)
        subprocess.check_output(p, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:  # if nothing on branch
        print("\nOn branch " + branch)
        print("Your branch is up-to-date")
        print("Nothing to commit, working directory clean")

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def add_tag(repo, tag):
    """Checksout a specific tag and creates branch at tag"""
    add = ["git", "tag", "-a", tag, "-m", "'%s created by gpack'"]
    os.chdir(repo.directory)

    try:
        subprocess.check_output(add, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        e = e.output.decode("utf-8")
        if "error" in e:
            print(e.replace("error", "gpack").strip())
        else:
            print(e.replace("fatal", "gpack").strip())

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def check(repos):
    """Checks if all tracked repos are clean and up-to-date"""
    for repo in repos:
        print(repo.name)

def checkout(repo, branch):
    """Checkout a branch"""
    check = ("git checkout %s" % (branch,)).split(" ")
    create =("git checkout -b %s" % (branch,)).split(" ")

    os.chdir(repo.directory)
    try:
        subprocess.check_output(checkout, stderr=subprocess.STDOUT)
        subprocess.check_output(branch, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        e = e.output.decode("utf-8")
        if "error" in e:
            print(e.replace("error", "gpack").strip())
        else:
            print(e.replace("fatal", "gpack").strip())

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

    try:
        subprocess.check_output(check, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("'%s' does not exist, would you like to create '%s'" % (branch,branch))
        ans = input("[y/n]: ")
        if(ans.lower() == "y" or ans.lower() == "yes"):
            try:
                subprocess.check_output(create, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print("Error checkout out %s" % (branch,))
    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def checkout_tag(repo, tag):
    """Checksout a specific tag and creates branch at tag"""
    checkout = ["git", "checkout", "tags/%s"%(tag,)]
    branch = ["git", "checkout", "-b", "build_%s" % (tag,)]
    os.chdir(repo.directory)

    try:
        subprocess.check_output(checkout, stderr=subprocess.STDOUT)
        subprocess.check_output(branch, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        e = e.output.decode("utf-8")
        if "error" in e:
            print(e.replace("error", "gpack").strip())
        else:
            print(e.replace("fatal", "gpack").strip())

    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone

def fetch():
    """Performs a git pull on all repos in the testing dir"""
    fetch = ["git", "fetch"]

    try:
        subprocess.check_output(fetch, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        e = e.output.decode("utf-8")
        if "error" in e:
            print(e.replace("error", "gpack").strip())
        else:
            print(e.replace("fatal", "gpack").strip())

def update(repo):
    """Performs update flow diagram on repo"""
    directory = repo.directory
    os.chdir(directory)
    locked = False
    with open(ROOT_DIR + "/.gpacklock", "r") as f:
        if directory not in [line.strip() for line in f.readlines()]:
            locked = True

    print("gpack: updating %s, please be patient..." % (repo.name,))

    if not localClean():
        if locked == False:
            print("\t" + repo.name + " is unlocked and not clean...")
            return True
        print("\t" + repo.name + " not clean, rinsing...")
        gpack.unlock(repo)
        rinse(repo)
    fetch()
    if not commitsMatch(repo) and locked:
        print("\t" + repo.name + " commits don't match, pulling...")
        gpack.unlock(repo)
        COMMAND = "git pull && git submodule update --recursive"
        os.system("xterm -T %s -geometry 90x30 -e \"%s || read -p 'Press return to close window'\"" % (repo.directory, COMMAND,))
        print("Successfully pulled %s..." % (repo.name,))#pull(repo)
        if not localClean():
            print("\t" + repo.name + " not clean, rinsing...")
            rinse(repo)
            if not localClean():
                print("\t" + repo.name + " not clean, resetting...")
                return False
    if locked:
        gpack.lock(repo)  # re-lock repo
    return True


def commitsMatch(repo):
    """Checks to see if commits match between local repo and remote"""
    branch = repo.branch
    log = ["git", "log"]
    log_remote = ["git", "log", "origin/" + branch]

    try:
        local = subprocess.check_output(log, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return False

    try:
        remote = subprocess.check_output(log_remote, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return False

    if local == remote:
        return True
    else:
        return False

def localClean():
    """Checks to see if the local directory is clean"""
    status = ["git", "status", "-u"]
    clean = "nothing to commit, working directory clean"

    try:
        output = subprocess.check_output(status, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return False
    else:
        if clean in output.decode("utf-8"):
            return True
        else:
            return False

def viewTags(repo):
    """Returns all available tags for a repo"""
    tag = ["git", "tag", "-l"]
    os.chdir(repo.directory)
    try:
        process = subprocess.check_output(tag)
    except subprocess.CalledProcessError as e:
        return []
    output = process.decode("utf-8")
    tags = output.split("\n")
    tags = [tag for tag in tags if tag != ""]  # remove blank tag
    os.chdir(ROOT_DIR)  # Go back to ROOT_DIR after clone
    return tags
