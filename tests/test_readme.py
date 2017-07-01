import os
import re
import unittest


class ReadmeTest(unittest.TestCase):

    @staticmethod
    def get_file_contents(path):
        with open(path) as input_file:
            return input_file.read()

    def get_readme(self):
        return self.get_file_contents('README.md')

    def get_source(self, filename):
        return self.get_file_contents('src/%s' % filename)

    def test_app_endpoints(self):
        readme = self.get_readme()
        source = self.get_source('app.py')

        for line in source.splitlines():
            match = re.match(r'@app\.route\(\'([^\']+)\'\)', line)
            if match:
                url_pattern = match.group(1)
                self.assertIn('`%s`' % url_pattern, readme)

    def test_api_methods(self):
        readme = self.get_readme()
        source = self.get_source('api.py')

        for line in source.splitlines():
            match = re.match(r'\s*def (.+)\(self, (.*)\):', line)
            if match:
                name, args = match.groups()
                if name.startswith('_'):
                    continue

                self.assertIn('`%s(%s)`' % (name, args), readme)
