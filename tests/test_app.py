import json
import unittest
from unittest_helper import get_api_client

import app


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.api = get_api_client()

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

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

    def test_get_readme_html(self):
        response = self.client.get('/repos/rycus86/docker-travis-cli/readme')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)
        self.assertEqual(response.charset, 'utf-8')

        readme = response.data

        self.assertIsNotNone(readme)
        self.assertIn('travis-cli', readme)
        self.assertIn('<h1>', readme)

        alternative_response = self.client.get('/repos/rycus86/docker-travis-cli/readme/html')

        self.assertEqual(response.data, alternative_response.data)

    def test_get_readme_raw(self):
        response = self.client.get('/repos/rycus86/docker-travis-cli/readme/raw')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response.content_type)
        self.assertEqual(response.charset, 'utf-8')

        readme = response.data

        self.assertIsNotNone(readme)
        self.assertIn('# travis-cli', readme)
        self.assertIn('### Usage', readme)

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
