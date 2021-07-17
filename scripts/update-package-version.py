#!/usr/bin/python

import hashlib
import os
import re
from pathlib import Path

import requests
from github import Github

g = Github(os.environ.get('GITHUB_TOKEN'))

recipes_directory = Path(__file__).resolve(True).parents[1] / 'recipes'
package_txt_files = recipes_directory.glob('**/package.txt')
for package_txt_file_path in package_txt_files:
    with package_txt_file_path.open('r+') as package_txt_file:
        line = package_txt_file.readline()
        m = re.search(r'^(.+?)/(.+?)@(.+?) ', line)
        owner = m.group(1)
        repo = m.group(2)
        version = m.group(3)

        print('{0}/{1}'.format(owner, repo))

        latest_version_type = 'releases'

        if owner == 'pqrs-org':
            latest_version_type = 'tags'
        elif owner == 'chriskohlhoff' and repo == 'asio':
            latest_version_type = 'tags'
        elif owner == 'jarro2783' and repo == 'cxxopts':
            latest_version_type = 'tags'
        elif owner == 'fr00b0' and repo == 'nod':
            latest_version_type = 'tags'
        elif owner == 'p-ranav' and repo == 'glob':
            latest_version_type = 'master'
        elif owner == 'scopeInfinity' and repo == 'NaturalSort':
            latest_version_type = 'master'

        #
        # Find latest_version
        #

        latest_version = None
        tarball_url = None

        github_repo = g.get_repo('{0}/{1}'.format(owner, repo))

        if latest_version_type == 'releases':
            latest_version = github_repo.get_latest_release().tag_name
            tarball_url = 'https://github.com/{0}/{1}/archive/refs/tags/{2}.tar.gz'.format(
                owner,
                repo,
                latest_version,
            )
        elif latest_version_type == 'tags':
            latest_version = github_repo.get_tags()[0].name
            tarball_url = 'https://github.com/{0}/{1}/archive/refs/tags/{2}.tar.gz'.format(
                owner,
                repo,
                latest_version,
            )
        elif latest_version_type == 'master':
            latest_version = github_repo.get_branch("master").commit.sha
            tarball_url = 'https://github.com/{0}/{1}/archive/{2}.tar.gz'.format(
                owner,
                repo,
                latest_version,
            )
        else:
            print(
                'WARNING: {0}/{1} is not provided a way to find the latest version.'.format(owner, repo))
            continue

        #
        # Update package.txt
        #

        if version != latest_version:
            print('{0}/{1} {2} -> {3}'.format(owner,
                  repo, version, latest_version))

            r = requests.get(tarball_url)
            hash = hashlib.sha256(r.content).hexdigest()

            line = re.sub(r'@.+? ', '@{0} '.format(latest_version), line)
            line = re.sub(r'sha256:[^ ]+', 'sha256:{0}'.format(hash), line)

            package_txt_file.seek(0)
            package_txt_file.write(line)
            package_txt_file.write("\n")
