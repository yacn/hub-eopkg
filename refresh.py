#!/usr/bin/env python3

import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.request

import yaml


def get_tag_of_latest_github_release(repo):
    releases_url = f'https://api.github.com/repos/{repo}/releases/latest'
    resp = urllib.request.urlopen(releases_url)
    if resp.code != 200:
        print(f"error reaching out to github")
        return None
    encoding = resp.info().get_content_charset('utf-8')
    data = json.loads(resp.read().decode(encoding))
    return data.get('tag_name', None)



with open('package.yml', 'r') as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)

# package.yml source field is a list of dicts where dict key is url and dict value is sha256sum
# unless it's a git source in which case the value is the tag or commit sha
# there's only one source here so flatten to the two items we need:
_, current_tag = list(data['source'][0].items()).pop()

new_tag = get_tag_of_latest_github_release('github/hub')

if not new_tag:
    print("could not determine latest version")
    sys.exit(1)

if current_tag == new_tag:
    print(f"Latest version is still {current_tag}. Up to date, nothing to do")
    sys.exit(0)

new_release = data['release'] + 1
print(" ".join([
    f"version: {data['version']} -> {new_tag}",
    f"tag: {current_tag} -> {new_tag}",
    f"release: {data['release']} -> {new_release}"
]))

print("updating package.yml")
package_dot_yml = os.path.join(os.getcwd(), 'package.yml')
package_dot_yml_dot_bak = f"{package_dot_yml}.bak"
with tempfile.NamedTemporaryFile(dir=os.getcwd()) as tmpfp:
    with open(package_dot_yml, 'rb') as pkg_yml:
        subprocess.run(shlex.split(f'./update-package-yml.sh {new_tag} {new_release}'),
                stdin=pkg_yml, stdout=tmpfp
        )
    if os.path.exists(package_dot_yml_dot_bak):
        os.unlink(package_dot_yml_dot_bak)
    os.link(package_dot_yml, package_dot_yml_dot_bak)
    os.unlink(package_dot_yml)
    os.link(tmpfp.name, package_dot_yml)
