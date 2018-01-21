import os
from unittest import main as test_main, SkipTest, TestCase

class TestGpack(TestCase):
    """Testing all gpack commands"""
    def test_branch(self):
        branch = os.popen("./gpack branch test4").read().strip()
        self.assertEqual(branch, "'test4' is currently on branch 'build_test'")

    def test_list(self):
        repos = os.popen("./gpack list").read().strip()
        string = "test1\ntest2\ntest3\ntest4\niogen"
        self.assertEqual(repos, string)

if __name__ == "__main__":
    os.system("./gpack install -nogui")
    test_main()
