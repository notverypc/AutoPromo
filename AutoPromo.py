#!/usr/local/bin/managed_python3

# Git Function borrowed from https://github.com/Gusto/it-cpe-opensource/blob/main/autopkg/autopkg_tools.py
# Promote_apps borrowed from https://github.com/joshua-d-miller/munki-promote

import os
import plistlib
import subprocess
import requests

from datetime import datetime, timedelta

promo_list = []

# Set Variables
munki_repo = "path/to/munki/repo"

# Slack Variables
webhook_url = "https://hooks.slack.com/services/xxxxxxxxxxxxx"
channel = "channel_name"
icon_url = ":arrow_up:"
slack_username = "AutoPromo"

makecatalogs_binary = "/usr/local/munki/makecatalogs"


def promote_apps(munki_repo):
    '''This checks the pkgsinfo files for "_autopromotion_catalogs" Key. 
    If the key is there then when required the app will be promoted'''
    pkgsinfo_folder = munki_repo + "/pkgsinfo"
    os_walker = dict()
    now = datetime.now()
    for os_walker[0], os_walker[1], os_walker[2] in os.walk(pkgsinfo_folder):
        for os_walker[3] in os_walker[2]:
            # Omit hidden files
            if os_walker[3].startswith("."):
                continue
            working_file = os.path.join(os_walker[0], os_walker[3])
            with open(working_file, "rb") as pl:
                work_plist = plistlib.load(pl)
                if "_autopromotion_catalogs" in work_plist:
                    autopromotion_info = work_plist["_autopromotion_catalogs"]
                    for key in autopromotion_info.keys():
                        promo_days = (int(key))
                    current_catalogs = work_plist["catalogs"]
                    new_catalogs = autopromotion_info[str(key)]
                    app_name = work_plist["name"]
                    creation_date = work_plist.get("_metadata")["creation_date"]
                    version_num = work_plist["version"]
                    promo_date = creation_date + (timedelta(days=promo_days))
                    if current_catalogs != new_catalogs and promo_date < now:
                        work_plist["catalogs"] = new_catalogs
                        try:
                            with open(working_file, "wb") as plist_to_write:
                                plistlib.dump(work_plist, plist_to_write)
                                promo_list.append(app_name)
                        except:
                            print("AutoPromo Failed")

                        slack_notification(app_name, version_num, new_catalogs)
    return promo_list


def slack_notification(app_name, version_num, new_catalogs):
    '''This sends a slack notification for each promoted app'''
    slack_text = f"*App Promoted:*\nTitle: *{app_name}* Version:*{version_num}* Catalog: *{new_catalogs}*\n"
    slack_data = {'text': slack_text, 'channel': channel, 'icon_emoji': icon_url, 'username': slack_username}

    response = requests.post(webhook_url, json=slack_data)
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error %s, the response is:\n%s'% (response.status_code, response.text))


def git_run(cmd):
    '''This is borrowed from gusto'''
    cmd = ["git"] + cmd
    hide_cmd_output = True

    try:
        result = subprocess.run(" ".join(cmd), shell=True, cwd=munki_repo, capture_output=hide_cmd_output)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e


def current_branch():
    git_run(["rev-parse", "--abbrev-ref", "HEAD"])


def checkout(branch, new=True):
    if current_branch() != "main" and branch != "main":
        checkout("main", new=False)

    gitcmd = ["checkout"]
    if new:
        gitcmd += ["-b"]

    gitcmd.append(branch)
    # Lazy branch exists check
    try:
        git_run(gitcmd)
    except subprocess.CalledProcessError as e:
        if new:
            checkout(branch, new=False)
        else:
            raise e


def makecatalogs():
        '''If any apps are promoted then run makecatalogs and push changes to repo'''
        if promo_list:
            subprocess.run([makecatalogs_binary, munki_repo])
            git_run(["add ."])
            git_run(
                [
                    "commit",
                    "-m",
                    f"'AutoPromo_Update'",
                ]
            )
            # git_run(["push", "--set-upstream", "origin", recipe.branch])
            git_run(["push"])

# The Main Section
def main():
    promote_apps(munki_repo)
    makecatalogs()

if __name__ == "__main__":
    main()
