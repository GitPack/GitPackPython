import os
import sys
import shutil
import threading
import stat
import traceback
import yaml

from core.util import git
from core.util import ssh
from core.util.config import Config
from core.util.process import ProccessPool
from core.repo import Repo

ROOT_DIR = os.getcwd()  # saves root dir for clio-template

def install(args):
    os.chdir(ROOT_DIR)
    for repo in getRepos():
        if not os.path.isdir(repo.dirname):
            os.mkdir(repo.dirname)

    if len(args) == 0:
        ProccessPool(vinstallRepo, getRepos())  # multiprocessing pool
    elif args[0] == "-nogui":
        ProccessPool(installRepo, getRepos())  # multiprocessing pool
    else:
        help()

def vinstallRepo(repo):
    """verbose repo install"""
    if not os.path.isdir(repo.directory):  # don't try and clone existing directory
        repo.clone(verbose=True)
        if repo.lock == True:
            lock(repo)

def installRepo(repo):
    if not os.path.isdir(repo.directory):  # don't try and clone existing directory
        repo.clone()
        if repo.lock == True:
            lock(repo)

def tagRepo(repo):
    print("Available tags for %s: " % (repo.name,))
    print(", ".join([str(x) for x in repo.viewTags()]))
    repo.tag = input("Tag for %s (blank is origin/master): " % (repo.name,))
    if repo.tag != "":
        if not repo.tag in repo.viewTags():
            repo.add_tag(repo.tag)  # adds tag to repo
        repo.checkout_tag(repo.tag)  # creates a branch on tag

def checkout(repo):
    if os.path.isdir(repo.directory):
        repo.branch = input("Branch to checkout for %s: " % (repo.name,))
        if repo.branch != "":
            repo.checkout(repo.branch)  # checkout branch or create new one
    else:
        print("%s does not exist, try running ./gpack install" % (repo.name,))

def uninstall():
    for repo in getRepos():
        repoUninstall(repo)

def repoUninstall(repo):
    """Uninstalls a specific repository"""
    if os.path.isdir(repo.directory):
        unlock(repo)
        shutil.rmtree(repo.dirname+"/"+getFile(repo))

def getFile(repo):
    for file in os.listdir(repo.dirname):
        if file == repo.name:
            return file

def check():
    git.check(getRepos())

def clean():
    """Cleans all repos"""
    ProccessPool(cleanRepo, getRepos())

def cleanRepo(repo):
    """Cleans a repo of unstaged work"""
    if os.path.isdir(repo.directory):
        with open(ROOT_DIR + "/.gpacklock", "r") as f:
            if repo.directory not in [line.strip() for line in f.readlines()]:
                unlock(repo)
        repo.clean()
    else:
        print("%s does not exist, try running ./gpack install" % (repo.name,))

def update():
    for repo in getRepos():
        updateRepo(repo)

def updateRepo(repo):
    """Helper method for update"""
    if not os.path.isdir(repo.directory):
        print("Error: %s doesn't exist, cloning instead" % (repo.name,))
        repo.clone()
        lock(repo)
    elif repo.update() == False:
        try:
            shutil.rmtree(repo.directory)
        except FileNotFoundError:
            pass
        repo.clone()
        lock(repo)

def pushRepo(repo):
    """Pushes local changes"""
    repo.push()

def addRepo(args):
    """Adds repo to GpackRepos file"""
    args = [str(arg) for arg in args]
    data = {"name": {"url":args[0], "local_dir":args[1], "branch":args[2]}}
    with open("./GpackRepos", "a") as f:  # append repo to GpackRepos
        f.write("\n")
        yaml.dump(data, f, default_flow_style=False)

def list():
    """Prints all repo names in GpackRepos"""
    for repo in getRepos():
        print(repo.name)

def purge():
    """Full uninstall and install of ALL repos in GpackRepos"""
    uninstall()
    install([])

def checkBranch(repo):
    """Prints the current branch of input repo"""
    if os.path.isdir(repo.directory):
        repo.checkBranch()
    else:
        print("%s does not exist, try running ./gpack install" % (repo.name,))

def getRepos():
    """Returns a list of repositories from GpackRepos file"""
    repos = []

    data = yaml.load(open("GpackRepos"))
    if data == None:
        return []

    for key, value in data.items():
        if key == "config":
            config = Config(value)
        else:
            r = Repo(value)
            repos.append(r)
    return repos

def getRepo(name):
    """Returns repo object from getRepos if it exist"""
    if(name in [repo.name for repo in getRepos()]):
        for repo in getRepos():
            if repo.name == name:
                return repo
    else:
        help()

def lockAll():
    for repo in getRepos():
        lock(repo)

def lock(repo):
    """Updates .gpacklock file and locks given repository"""
    os.chdir(ROOT_DIR)
    checkLock()  # checks if .gpacklock exists
    with open(".gpacklock", "r+") as f:
        locked = [line.strip() for line in f.readlines()]
    open(".gpacklock", "w").close() # deletes file contents

    if repo.directory in locked:
        if not os.path.isdir(repo.directory):
            locked = [line for line in locked if line != repo.directory]
            with open(".gpacklock", "r+") as f:
                for line in locked:
                    f.write(line + "\n")
                return

        locked = [line for line in locked if line != repo.directory]
        applyPerms(repo, "lock")  # removes write access
        with open(".gpacklock", "r+") as f:
            for line in locked:
                f.write(line + "\n")
    else:
        if not os.path.isdir(repo.directory):
            return
        applyPerms(repo, "lock")  # removes write access
        with open(".gpacklock", "r+") as f:
            for line in locked:
                f.write(line + "\n")

def unlockAll():
    for repo in getRepos():
        unlock(repo)

def unlock(repo):
    """Updates .gpacklock file and unlocks given repository"""
    os.chdir(ROOT_DIR)
    checkLock()  # checks if .gpacklock exists
    if not os.path.isdir(repo.directory):
        return

    with open(".gpacklock", "r+") as f:
        locked = [line.strip() for line in f.readlines()]
    open(".gpacklock", "w").close() # deletes file contents

    if repo.directory in locked:
        applyPerms(repo, "unlock")  # grants write access
        with open(".gpacklock", "r+") as f:
            for line in locked:
                f.write(line + "\n")
    else:
        locked += [repo.directory]
        applyPerms(repo, "unlock")  # removes write access
        with open(".gpacklock", "r+") as f:
            for line in locked:
                f.write(line + "\n")

def checkLock():
    """Checks to see if .gpacklock exists"""
    if not os.path.isfile(".gpacklock"):
        open(".gpacklock", "w").close()

def applyPerms(repo, action):
    """Applys given chmod permissions to a repository"""
    os.chdir(ROOT_DIR)  # reset back to root dir
    REPO_DIRECTORY = repo.directory  # directory to repo from root
    exclude = [".git"]  # exclude certain directories
    repo_walk = []
    for root, dirs, files in os.walk(REPO_DIRECTORY, topdown = True):
        dirs[:] = [d for d in dirs if d not in exclude]  # remove git dir
        files[:] = [f for f in files if f not in exclude]  # remove .git files
        repo_walk.append((root, files))

    repo_walk = reversed(repo_walk)  # reverse dir to lock from top dir
    for directory, files in repo_walk:
        os.chdir(directory)
        for file in files:
            try:
                st = os.stat(file)
            except FileNotFoundError:  # broken links
                continue
            if action == "lock":
                try:
                    os.chmod(file, st.st_mode & ~stat.S_IWUSR)
                except PermissionError:
                    continue
            elif action == "unlock":
                try:
                    os.chmod(file, st.st_mode | stat.S_IWUSR)
                except PermissionError:
                    continue

        st = os.stat(directory)
        if action == "lock":
            os.chmod(directory, st.st_mode & ~stat.S_IWUSR)
        elif action == "unlock":
            os.chmod(directory, st.st_mode | stat.S_IWUSR)
    os.chdir(ROOT_DIR)  # reset back to root dir

def parseArgs(args):
    """Parses input arguments for gpack"""
    if len(args) > 4:  # largest arg count aloud
        help()
    else:
        if args[0] == "install":
            if len(args) > 2:
                help()
            print("Cloning repositories, this could take awhile, please be patient...")
            install(args[1:])
        elif args[0] == "uninstall":
            if len(args) == 1:
                print("Removing repositories, this could take awhile, please be patient...")
                uninstall()
            elif len(args) == 2:
                repoUninstall(getRepo(args[1]))
            else:
                help()
        elif args[0] == "list":
            if len(args) == 1:
                list()
            else:
                help()
        elif args[0] == "push":
            if len(args) != 2:
                help()
            pushRepo(getRepo(args[1]))
        elif args[0] == "tag":
            if len(args) != 2:
                help()
            tagRepo(getRepo(args[1]))
        elif args[0] == "help":
            help()
        elif args[0] == "check":
            check()
        elif args[0] == "checkout":
            if len(args) != 2:
                help()
            checkout(getRepo(args[1]))
        elif args[0] == "add":
            if len(args) != 4:
                help()
            addRepo(args[1:])
        elif args[0] == "branch":
            if len(args) != 2:
                help()
            checkBranch(getRepo(args[1]))
        elif args[0] == "update":
            if len(args) > 2:
                help()
            if len(args) == 1:
                update()
            elif len(args) == 2:
                updateRepo(getRepo(args[1]))
        elif args[0] == "clean":
            if len(args) == 1:
                clean()
            elif len(args) == 2:
                cleanRepo(getRepo(args[1]))
        elif args[0] == "purge":
            if len(args) != 1:
                help()
            print("This could take awhile, please be patient...")
            purge()
        elif args[0] == "lock":
            if len(args) > 2:
                help()
            elif len(args) == 1:
                lockAll()
            elif len(args) == 2:
                lock(getRepo(args[1]))
        elif args[0] == "unlock":
            if len(args) > 2:
                help()
            elif len(args) == 1:
                unlockAll()
            elif len(args) == 2:
                unlock(getRepo(args[1]))
        else:
            help()

def help():
    msg = ("\nGit Package Manager\n"
       "-------------------\n"
       "\tMaintains a clean local repository directory by parsing\n"
       "\tGpackRepos for user-defined repositores that they wish to clone.\n"
       "\tBy default, all cloned repositories have no write access.\n\n"
       "\t.gpacklock holds a list of local repository directories that\n"
       "\twill not be tracked when gpack cleans and updates by allowing\n"
       "\twrite access to those repositories.\n"
       "\nCore Commands\n"
       "-------------\n"
       "\tadd [url] [directory] [branch]\n"
       "\t\tAdds a repo to the GpackRepos file given ssh URL and local\n"
       "\t\tdirectory relative to current directory\n"
       "\tcheck\n"
       "\t\tChecks if all repos are clean and match GpackRepos\n"
       "\tclean [repo]\n"
       "\t\tForce cleans local repo directory with git clean -xdff\n"
       "\thelp\n"
       "\t\tDisplays this message\n"
       "\tinstall [-nogui]\n"
       "\t\tClones repos in repo directory\n"
       "\t\t-nogui doesn't open terminals when installing\n"
       "\tlist\n"
       "\t\tList all repos in GpackRepos file\n"
       "\tlock [repo]\n"
       "\t\tMakes all repos read-only, removes from .gpacklock file\n"
       "\tuninstall [repo] [-f]\n"
       "\t\tRemoves all local repositories listed in the Repositories File\n"
       "\t\tAdd -f to force remove all repositories\n"
       "\tunlock [repo]\n"
       "\t\tAllows writing to all repos, appends to .gpacklock file\n"
       "\tpurge\n"
       "\t\tRemoves all repos and re-clones from remote\n"
       "\tupdate [repo]\n"
       "\t\tCleans all repos in GpackRepos, resetting it to the default\n"
       "\nGit Commands\n"
       "------------\n"
       "\tbranch [repo]\n"
       "\t\tChecks branch on current repo\n"
       "\tcheckout [repo]\n"
       "\t\tPrompts user for branch to checkout. If the branch doesn't\n"
       "\t\texist, ask if user wants to create a new one\n"
       "\tpush [repo]\n"
       "\t\tPushes local repo changes to origin\n"
       "\t\tWon't push if on master\n"
       "\tpull [repo]\n"
       "\t\tPulls changes to repo\n"
       "\ttag [repo]\n"
       "\t\tAsks user which tag to checkout for a repo. If given tag\n"
       "\t\tdoesn't texists, ask for a new tag to create\n")
    print(msg)
    os.chdir(ROOT_DIR)
    ssh.remove_key(ROOT_DIR)
    sys.exit()  # force termination

def main(args):
    if len(args) != 0:
        ssh.download_key(ROOT_DIR)
        parseArgs(args)
        ssh.remove_key(ROOT_DIR)
    else:
        help()

if __name__ == "__main__":
    """Running gpack from gpack.py not bash file"""
    args = sys.argv[1:]
    try:
        if len(args) != 0:
            ssh.download_key(ROOT_DIR)
            parseArgs(args)
            ssh.remove_key(ROOT_DIR)
        else:
            help()
    except Exception:
        pass
