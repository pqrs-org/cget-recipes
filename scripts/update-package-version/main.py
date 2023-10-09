#!/usr/bin/python

'''Update recipes/*'''

import hashlib
import os
import re
from pathlib import Path

import requests
# pylint: disable = no-name-in-module
from github import Github


def update_recipes():
    '''Update recipes/*'''

    github = Github(os.environ.get('GITHUB_TOKEN'))

    recipes_directory = Path(__file__).resolve(True).parents[2] / 'recipes'
    package_txt_files = recipes_directory.glob('**/package.txt')
    for package_txt_file_path in package_txt_files:
        with package_txt_file_path.open('r+') as package_txt_file:
            line = package_txt_file.readline()
            match = re.search(r'^(.+?)/(.+?)@(.+?) ', line)
            owner = match.group(1)
            repo = match.group(2)
            version = match.group(3)

            print(f'{owner}/{repo}')

            latest_version_type = 'releases'

            if owner == 'pqrs-org':
                latest_version_type = 'tags'
            elif owner == 'ArashPartow' and repo == 'exprtk':
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

            github_repo = github.get_repo(f'{owner}/{repo}')

            if latest_version_type == 'releases':
                latest_version = github_repo.get_latest_release().tag_name
                tarball_url = f'https://github.com/{owner}/{repo}/archive/refs/tags/{latest_version}.tar.gz'
            elif latest_version_type == 'tags':
                latest_version = github_repo.get_tags()[0].name
                tarball_url = f'https://github.com/{owner}/{repo}/archive/refs/tags/{latest_version}.tar.gz'
            elif latest_version_type == 'master':
                latest_version = github_repo.get_branch("master").commit.sha
                tarball_url = f'https://github.com/{owner}/{repo}/archive/{latest_version}.tar.gz'
            else:
                print(
                    f'WARNING: {owner}/{repo} is not provided a way to find the latest version.')
                continue

            #
            # Update package.txt
            #

            if version != latest_version:
                print(f'{owner}/{repo} {version} -> {latest_version}')

                # pylint: disable = c-extension-no-member
                response = requests.get(tarball_url)
                hexdigest = hashlib.sha256(response.content).hexdigest()

                line = re.sub(r'@.+? ', f'@{latest_version} ', line)
                line = re.sub(r'sha256:[^ ]+',
                              f'sha256:{hexdigest}', line)

                package_txt_file.seek(0)
                package_txt_file.write(line)
                package_txt_file.write("\n")


if __name__ == "__main__":
    update_recipes()
