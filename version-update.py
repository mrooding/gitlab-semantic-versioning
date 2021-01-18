#!/usr/bin/env python3
import os
import re
import sys
import semver
import subprocess
import gitlab

def git(*args):
    return subprocess.check_output(["git"] + list(args))

def get_last_commit_message():
    return git("log", "-1", "--pretty=%B")

def verify_env_var_presence(name):
    if name not in os.environ:
        raise Exception(f"Expected the following environment variable to be set: {name}")

def extract_gitlab_url_from_project_url():
    project_url = os.environ['CI_PROJECT_URL']
    project_path = os.environ['CI_PROJECT_PATH']

    return project_url.split(f"/{project_path}", 1)[0]

def extract_merge_request_id_from_commit():
    message = get_last_commit_message()
    matches = re.search(r'(\S*\/\S*!)(\d+)', message.decode("utf-8"), re.M|re.I)

    if matches is None:
        raise Exception(f"Unable to extract merge request from commit message: {message}")

    return matches.group(2)

def retrieve_labels_from_merge_request(merge_request_id):
    project_id = os.environ['CI_PROJECT_ID']
    gitlab_private_token = os.environ['NPA_PASSWORD']

    gl = gitlab.Gitlab(extract_gitlab_url_from_project_url(), private_token=gitlab_private_token)
    gl.auth()

    project = gl.projects.get(project_id)
    merge_request = project.mergerequests.get(merge_request_id)

    return merge_request.labels

def get_mr_or_direct_commit_labels():
    skip_direct_commits = os.environ.get('SKIP_DIRECT_COMMITS')
    labels = []
    found_mr = True

    try:
        merge_request_id = extract_merge_request_id_from_commit()
        labels = retrieve_labels_from_merge_request(merge_request_id)
    except Exception as e:
        if skip_direct_commits is None:
            raise e
        else:
            found_mr = False

    if not (skip_direct_commits is None and found_mr):
        labels += get_last_commit_message()

    return labels

def bump(latest):
    minor_bump_label = os.environ.get("MINOR_BUMP_LABEL") or "bump-minor"
    major_bump_label = os.environ.get("MAJOR_BUMP_LABEL") or "bump-major"
    labels = get_mr_or_direct_commit_labels()

    if minor_bump_label in labels:
        return semver.bump_minor(latest)
    elif major_bump_label in labels:
        return semver.bump_major(latest)
    else:
        return semver.bump_patch(latest)

def tag_repo(tag):
    repository_url = os.environ["CI_REPOSITORY_URL"]
    username = os.environ["NPA_USERNAME"]
    password = os.environ["NPA_PASSWORD"]

    push_url = re.sub(r'([a-z]+://)[^@]*(@.*)', rf'\g<1>{username}:{password}\g<2>', repository_url)

    git("remote", "set-url", "--push", "origin", push_url)
    git("tag", tag)
    git("push", "origin", tag)

def main():
    env_list = ["CI_REPOSITORY_URL", "CI_PROJECT_ID", "CI_PROJECT_URL", "CI_PROJECT_PATH", "NPA_USERNAME", "NPA_PASSWORD"]
    [verify_env_var_presence(e) for e in env_list]

    try:
        latest = git("describe", "--tags", "--first-parent", "--match", "[[:digit:]].[[:digit:]].[[:digit:]]*").decode().strip()
    except subprocess.CalledProcessError:
        # Default to version 1.0.0 if no tags are available
        version = "1.0.0"
    else:
        # Skip already tagged commits
        if '-' not in latest:
            print(latest)
            return 0

        version = bump(latest)

    tag_repo(version)
    print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
