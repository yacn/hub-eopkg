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


def get_latest_github_release(repo):
    releases_url = f'https://api.github.com/repos/{repo}/releases/latest'
    resp = urllib.request.urlopen(releases_url)
    if resp.code != 200:
        print(f"error reaching out to github")
        return None, None
    encoding = resp.info().get_content_charset('utf-8')
    data = json.loads(resp.read().decode(encoding))
    version = data['tag_name'].lstrip('v')
    asset_url = next(a['browser_download_url'] for a in data['assets'] if 'linux-amd64' in a['browser_download_url'])
    return version, asset_url




with open('package.yml', 'r') as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)

# package.yml source field is a list of dicts where dict key is url and dict value is sha256sum
# there's only one source here so flatten to the two items we need:
source_url, _ = list(data['source'][0].items()).pop() 

new_version, new_source_url = get_latest_github_release('github/hub')

fname = os.path.basename(new_source_url)

if not new_version:
    print("could not determine latest version")
    sys.exit(1)

if source_url == new_source_url:
    print("Up to date, nothing to do")
    sys.exit(0)

print(f"fetching latest (v{new_version}) hub  from GitHub")
subprocess.check_output(
    shlex.split(f'curl -L -o {fname} {new_source_url}')
)

print(f"generating checksum of {fname}")
new_checksum, _ = subprocess.check_output(
    shlex.split(f'sha256sum {fname}')
).decode().strip().split()

print(f"removing {fname}, no longer needed")
os.remove(os.path.join(os.getcwd(), fname))

new_release = data['release'] + 1
print(" ".join([
    f"version: {data['version']} -> {new_version}",
    f"checksum: {data['source'][0][source_url]} -> {new_checksum}",
    f"release: {data['release']} -> {new_release}"
]))

print("updating package.yml")
package_dot_yml = os.path.join(os.getcwd(), 'package.yml')
package_dot_yml_dot_bak = f"{package_dot_yml}.bak"
with tempfile.NamedTemporaryFile(dir=os.getcwd()) as tmpfp:
    with open(package_dot_yml, 'rb') as pkg_yml:
        print(f'./update-package-yml.sh {new_version} {new_checksum} {new_release}')
        subprocess.run(shlex.split(f'./update-package-yml.sh {new_version} {new_checksum} {new_release}'),
                stdin=pkg_yml, stdout=tmpfp
        )
    if os.path.exists(package_dot_yml_dot_bak):
        os.unlink(package_dot_yml_dot_bak)
    os.link(package_dot_yml, package_dot_yml_dot_bak)
    os.unlink(package_dot_yml)
    os.link(tmpfp.name, package_dot_yml)
