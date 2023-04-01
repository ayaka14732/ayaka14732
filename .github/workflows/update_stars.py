import aiohttp
import asyncio
import re
import sys

GITHUB_TOKEN = sys.argv[1]

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json',
}

pattern = re.compile(r'- \*\*(\d+)\*\* \[([^\]]+)\]\((https://github\.com/[^\]]+)\): (.+)\n')

async def get_star_count(session, repo_name):
    async with session.get(f'https://api.github.com/repos/{repo_name}', headers=headers) as resp:
        data = await resp.json()
        return data['stargazers_count']

def regenerate_line(line: str, repo_star_dict: dict[str, int]) -> str:
    match = pattern.fullmatch(line)
    if not match:
        return line
    _, repo_name, repo_url, description = match.groups()
    repo_star = repo_star_dict[repo_name]
    return f'- **{repo_star}** [{repo_name}]({repo_url}): {description}\n'

async def main():
    # read the old file
    with open('README.md', encoding='utf-8') as f:
        lines = f.readlines()

    # extract all `repo_name`s
    repo_name_list = []
    for line in lines:
        match = pattern.fullmatch(line)
        if match:
            _, repo_name, _, _ = match.groups()
            repo_name_list.append(repo_name)

    # get `(repo_name, repo_star)` pairs`
    async with aiohttp.ClientSession() as session:
        tasks = [get_star_count(session, repo_name) for repo_name in repo_name_list]
        repo_star_list = await asyncio.gather(*tasks)
    repo_star_dict = dict(zip(repo_name_list, repo_star_list))

    # write to the new file
    with open('README.md', 'w', encoding='utf-8') as f:
        for line in lines:
            new_line = regenerate_line(line, repo_star_dict)
            f.write(new_line)

if __name__ == '__main__':
    asyncio.run(main())
