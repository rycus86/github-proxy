import os
import unittest
from api import ApiClient


class TestApiClient(unittest.TestCase):
    api = ApiClient()

    @classmethod
    def setUpClass(cls):
        if os.path.exists('github_token.txt'):
            with open('github_token.txt') as token_file:
                TestApiClient.api = ApiClient(token=token_file.read())

    def test_list_repos(self):
        repos = self.api.list_repos('rycus86')

        self.assertIsNotNone(repos)
        self.assertGreater(len(repos), 0)

        for repo in repos:
            for expected in ('name', 'full_name', 'owner', 'html_url', 'description', 'fork',
                             'created_at', 'updated_at', 'pushed_at', 'language', 'homepage',
                             'stargazers_count', 'watchers_count', 'open_issues_count'):

                self.assertIn(expected, repo, msg='The key %s is not found in the repo details' % expected)

    def test_readme(self):
        readme = self.api.get_readme('rycus86', 'docker-travis-cli')

        self.assertIsNotNone(readme)
        self.assertIn('travis-cli', readme)
        self.assertIn('<h1>', readme)

    def test_commit_stats(self):
        commits = self.api.get_commit_stats('rycus86', 'docker-travis-cli')

        self.assertIsNotNone(commits)
        self.assertGreater(len(commits), 0)
        self.assertGreater(commits.get('total'), 0)

        latest = commits.get('latest')

        self.assertIsNotNone(latest, msg='Latest commit details not found')
        self.assertIn('author', latest)
        self.assertIn('date', latest)
        self.assertIn('message', latest)


if __name__ == '__main__':
    unittest.main()
