import requests
import click
import pygit2
import os
import json
import traceback
from typing import Tuple
from pathlib import Path



@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--output_directory', '-d', default='.', help='Output dir for clone repos.', show_default=True)
@click.option('--stars-expression', '-s', default='>500', help='Stars search condition. ">200" / "=400" / "<300" as example.', show_default=True)
@click.option('--languages', '-ls', nargs=0, required=True)
#@click.option('--users', nargs=0, required=True)
@click.argument('languages', nargs=-1)
@click.option('--token', '-t', help='Access token for increase rate limit. Read from $github_token if specify.', default='', show_default=True)
@click.option('--amount', '-n', help='Amount of repo.', type=int, default=50, show_default=True)
def clone_repos(output_directory: str, stars_expression: str, languages: Tuple, token: str, amount: int):
    """
    Clone repos from search api to output dir.
    Be careful check of upload size not provide

    output structure:
    - output_dir
      - language 1
        - repo 1
        - repo 2
        ...
      - language 2
        - repo 1
        - repo 2
        ...
      ...


    """

    token= os.environ.get('github_token', token)

    

    if token == '':
        click.echo(f'Token not found!')
        raise

    
    headers = {'accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {token}'}
    

    resolve_path = Path(output_directory)

    if not os.path.exists(resolve_path):
        os.makedirs(resolve_path)

    with click.progressbar(languages) as bar:        
        for lang in bar:
            try:
                search_expresion = f'stars:{stars_expression}+language:{lang.capitalize()}'

                request_url = f'https://api.github.com/search/repositories?q={search_expresion}&per_page={amount}&page=1'
                search_responce = requests.get(request_url, headers=headers)

                data = json.loads(search_responce.text)

                if not data.get("items"):
                    break

                
                print(resolve_path)

                for repo in data["items"]:
                    git_url = repo['git_url']
                    print(git_url)
                    out_path = resolve_path / lang.capitalize() / repo["name"]
                    print(out_path)
                    if not os.path.exists(out_path):
                        os.makedirs(out_path)
                    pygit2.clone_repository(git_url, out_path)
            except:
                traceback.print_exc()

        




if __name__ == "__main__":
    repos()