import subprocess
import requests
import os
import sys
import yaml
from core.util.config import Config

def download_key(ROOT_DIR):
    """Downloads a new key from a remote server"""
    key_url = ""
    os.chdir(ROOT_DIR)
    if not os.path.isfile("GpackRepos"):
        with open("GpackRepos", "w") as f:
            print("No GpackRepos file found, creating one...")
            print("Add repos with ./gpack add [url] [dir] [branch]")

    data = yaml.load(open("GpackRepos"))

    found_config = False
    for key, value in data.items():
        if key == "config":
            found_config = True
            config = Config(value)

    if found_config:
        key_url = config.key
    else:
        key_url = False

    if key_url != False:
        try:
            r = requests.get(key_url)
        except Exception:
            print("Key Error: Check GpackRepos for ssh_key")
            sys.exit()

        with open(".temp_ssh_key", "w") as f:
            f.write(r.content.decode("utf-8"))  # convert bytes like string to utf-8
        os.chmod(".temp_ssh_key", 0o600)  # read + write
        ssh = ["ssh", "-i", ".temp_ssh_key"]
        try:
            subprocess.check_output(ssh, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8").replace("fatal", "gpack").strip())

def remove_key(ROOT_DIR):
    os.chdir(ROOT_DIR)
    if os.path.isfile(".temp_ssh_key"):
        os.remove(".temp_ssh_key")
    else:
        return
