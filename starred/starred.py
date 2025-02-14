#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from io import BytesIO
from collections import OrderedDict
import click
from github3 import GitHub
from github3.exceptions import NotFoundError
from pytablewriter import MarkdownTableWriter
from starred import VERSION


desc = '''
# Awesome Stars

[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)
[![CI](https://github.com/ductnn/awesome-stars/actions/workflows/schedules.yml/badge.svg?branch=mas\
ter)](https://github.com/ductnn/awesome-stars/actions/workflows/schedules.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https:\
//github.com/ductnn/awesome-stars/pulls)

> A curated list of my GitHub stars ⭐ Generated by [starred](https://github.com/ductnn/starred)
## Contents
'''

like_my_awesome_stars = '''
## Support me
Give a ⭐ if you like this repo ❤️
'''

license_ = '''
## License
[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)]\
(https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, [{username}](https://github.com/{username})
has waived all copyright and related or neighboring rights to this work.
'''

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


@click.command()
@click.option('--username', envvar='USER', help='GitHub username')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub token')
@click.option('--sort',  is_flag=True, help='sort by language')
@click.option('--repository', default='', help='repository name')
@click.option('--message', default='update stars', help='commit message')
@click.option('--format', default='table', help='output repository format')
@click.version_option(version=VERSION, prog_name='starred')
def starred(username, token, sort, repository, message, format):
    """GitHub starred
    creating your own Awesome List used GitHub stars!
    example:
        starred --username ductnn --sort > README.md
    """
    if repository:
        if not token:
            click.secho('Error: create repository need set --token', fg='red')
            return
        file = BytesIO()
        sys.stdout = file
    else:
        file = None

    gh = GitHub(token=token)
    user = gh.user(username)
    stars = gh.starred_by(username)
    click.echo(desc)
    repo_dict = {}

    # store index
    repo_dict_idx = {}

    for s in stars:
        language = s.language or 'Others'
        description = html_escape(s.description).replace(
            '\n', '') if s.description else ''

        if language not in repo_dict:
            repo_dict[language] = []
            repo_dict_idx[language] = 1

        repo_dict[language].append([
            repo_dict_idx[language],
            s.name,
            s.html_url,
            description.strip()
        ])
        repo_dict_idx[language] += 1

    if sort:
        repo_dict = OrderedDict(sorted(repo_dict.items(), key=lambda l: l[0]))

    for language in repo_dict.keys():
        data = u'  - [{}](#{})'.format(
            language,
            '-'.join(language.lower().split())
        )
        click.echo(data)
    click.echo('')

    for language in repo_dict:
        click.echo('## {} \n'.format(language.replace('#', '# #')))

        if format == 'table':
            writer = MarkdownTableWriter(
                headers=['Index', 'Name', 'Repository URL', 'Description'],
                value_matrix=repo_dict[language],
                margin=1)
            click.echo(writer.dumps())
        else:
            for repo in repo_dict[language]:
                data = u'{}. [{}]({}) - {}'.format(*repo)
                click.echo(data)

        click.echo('')
    click.echo(like_my_awesome_stars)
    click.echo(license_.format(username=username))

    if file:
        try:
            rep = gh.repository(username, repository)
            readme = rep.readme()
            readme.update(
                message,
                file.getvalue(),
                author={
                    'name': user.name,
                    'email': user.email
                }
            )
        except NotFoundError:
            rep = gh.create_repository(
                repository, 'A curated list of my GitHub stars!')
            rep.create_file(
                'README.md', 'starred initial commit', file.getvalue(),
                author={'name': user.name, 'email': user.email})
        click.launch(rep.html_url)


if __name__ == '__main__':
    starred()
