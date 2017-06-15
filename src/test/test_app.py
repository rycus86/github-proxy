import os
import json
import unittest

import app


class AppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.api = ApiClient(token=os.environ.get('GITHUB_TOKEN', self._get_cached_token()))

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    @staticmethod
    def _get_cached_token():
        directory = os.path.dirname(__file__) or '.'
        path = os.path.join(os.path.abspath(directory), '../../github_token.txt')

        if os.path.exists(path):
            with open(path) as token_file:
                return token_file.read()

    def test_list_repos(self):
        response = self.client.get('/repos/rycus86')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')

        repos = json.loads(response.data)

        self.assertIsNotNone(repos)
        self.assertGreater(len(repos), 0)

        for repo in repos:
            for expected in ('name', 'full_name', 'owner', 'html_url', 'description', 'fork',
                             'created_at', 'updated_at', 'pushed_at', 'language', 'homepage',
                             'stargazers_count', 'watchers_count', 'open_issues_count'):
                self.assertIn(expected, repo, msg='The key %s is not found in the repo details' % expected)

    def test_get_readme(self):
        response = self.client.get('/repos/rycus86/docker-travis-cli/readme')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)
        self.assertEqual(response.charset, 'utf-8')

        readme = response.data

        self.assertIsNotNone(readme)
        self.assertIn('travis-cli', readme)
        self.assertIn('<h1>', readme)

    def test_get_commit_stats(self):
        response = self.client.get('/repos/rycus86/docker-travis-cli/commit-stats')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')

        commits = json.loads(response.data)

        self.assertIsNotNone(commits)
        self.assertGreater(len(commits), 0)
        self.assertGreater(commits.get('total'), 0)

        latest = commits.get('latest')

        self.assertIsNotNone(latest, msg='Latest commit details not found')
        self.assertIn('author', latest)
        self.assertIn('date', latest)
        self.assertIn('message', latest)
