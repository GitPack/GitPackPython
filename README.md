# GitPack

Python based git repository manager. Conceptually simular to a package manager like pip, rubygems, ect. GitPack handles the distrubuting of repositories without being tied to a specific language; although it does use python to execute commands. It specifically is designed to control multiple git repository dependances on a multiple user project.
* Clones multiple repositories in parallel.
* Controls read-only permissions on cloned repositories.
* Pulls multiple repositoires in parallel.
* Easy clean of repositories that do not have a clean git status.
* Submodule compatible

## Future improvements
* GitPack is not Git LFS compatible at the moment. Merge requests with this feature would be accepted.

Setup
-----

Add repos manually in GpackRepos file:

.. code::

    {"url": "`git@allegrogit.allegro.msad:AST-digital/iogen.git`", "local_dir": "./repos/iogen", "branch": "master"}

Add repos to GpackRepos file using gpack:

.. code::

    ./gpack add [url] [directory] [branch]

Usage
-----

Installs all repos in GpackRepos file:

.. code::

    ./gpack install

Checkout a repo tag or add tag to a repo:

.. code::

    ./gpack tag [repo]

Push local changes to remote on current branch:

.. code::

    ./gpack push [repo]

Description
-----------
Maintains a clean local repository directory by parsing
GpackRepos for user-defined repositores that they wish to clone.
By default, all cloned repositories have no write access.

.gpacklock holds a list of local repository directories that
will not be tracked when gpack cleans and updates by allowing
write access to those repositories.

Commands
--------
**add [url] [directory] [branch]**
   Adds a repo to the GpackRepos file given ssh URL and local directory
   relative to current directory
**branch [repo]**
   Checks branch on current repo
**checkout [repo]**
   Prompts user for branch to checkout. If the branch doesn't exist, ask if
   user wants to create a new one
**clean [repo]**
   Force cleans local repo directory with git clean -xdff
**help**
   Displays this message
**install [-v]**
   Clones repos in repo directory
   Optional verbose argument
**list**
   List all repos in GpackRepos file
**update**
   Pulls the repositories listed in the Repositories File and checks
   conformance
**uninstall [-f]**
   Removes all local repositories listed in the Repositories File
   Add -f to force remove all repositories
**uninstall [repo] [-f]**
   Removes all a given repositorie listed in the Repositories File
   repo is the local path to the repos directory
   Add -f to force remove the repo
**purge**
   Removes all repos and re-clones from remote
**push [repo]**
   Pushes local repo changes to origin
**tag [repo]**
   Asks user which tag to checkout for a repo. If given tag doesn't exists,
   ask for a new tag to create
