import re
from agithub.GitHub import GitHub


class ApiClient(object):
    def __init__(self, username=None, password=None, token=None):
        self._api = GitHub(username=username, password=password, token=token)

    @staticmethod
    def _is_successful(status):
        return status / 100 == 2

    def _get_links(self):
        headers = self._api.getheaders()

        for key, value in headers:
            if key.lower() == 'link':
                return value

    def _get_link(self, rel):
        links = self._get_links()
        if links:
            for match in re.finditer(r'<([^>]+)>; rel="%s"' % rel, links, flags=re.IGNORECASE):
                return match.group(1)

    def _get_page_number(self, link_rel):
        link = self._get_link(link_rel)
        if link:
            return int(re.sub(r'.*?page=([0-9]+)', r'\1', link, flags=re.IGNORECASE))

    def list_repos(self, username):
        repos = list()

        next_page = 1

        while next_page:
            status, response = self._api.users[username].repos.get(page=next_page)

            if self._is_successful(status):
                repos.extend(response)
                next_page = self._get_page_number('next')

        return repos

    def get_readme(self, owner, repository):
        headers = {'accept': 'application/vnd.github.v3.html'}
        status, response = self._api.repos[owner][repository].readme.get(headers=headers)

        if self._is_successful(status):
            return response

    def get_commit_stats(self, owner, repository):
        status, first_page = self._api.repos[owner][repository].commits.get()
        if self._is_successful(status) and first_page:
            last_commit = first_page[0].get('commit', dict())

            message = last_commit.get('message')
            author = last_commit.get('author', dict())
            author_name = author.get('name')
            commit_date = author.get('date')

            num_commits = len(first_page)

            last_page_num = self._get_page_number('last')

            if last_page_num > 1:
                last_status, last_page = self._api.repos[owner][repository].commits.get(page=str(last_page_num))

                if self._is_successful(last_status) and last_page:
                    num_commits = num_commits * (last_page_num - 1) + len(last_page)

            return {
                'total': num_commits,
                'latest': {
                    'author': author_name,
                    'date': commit_date,
                    'message': message
                }
            }
