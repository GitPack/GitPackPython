from multiprocessing import Pool

class ProccessPool():
    def __init__(self, func, repos, allow=True):
        """Creates a multiprocessing pool with given func and repos"""
        if allow:
            pool = Pool()
            pool.map(func, repos)
            pool.close()
            pool.join()
        else:  # if multiprocessing is not allowed, then iter each repo
            for repo in repos:
                func(repo)