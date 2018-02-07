import os
import logging

from flask import Flask, jsonify, make_response
from flask_cache import Cache
from flask_cors import CORS

from prometheus_flask_exporter import PrometheusMetrics
from docker_helper import read_configuration

from api import ApiClient

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
metrics = PrometheusMetrics(app)

metrics.info('flask_app_info', 'Application info',
             version=os.environ.get('GIT_COMMIT') or 'unknown')

metrics.info(
    'flask_app_built_at', 'Application build timestamp'
).set(
    float(os.environ.get('BUILD_TIMESTAMP') or '0')
)

CORS(app, origins=read_configuration(
    'CORS_ORIGINS', '/var/secrets/secrets.env', default='http://localhost:?.*'
).split(','), methods='GET')

api = ApiClient(
    username=read_configuration('GITHUB_USERNAME', '/var/secrets/secrets.env'),
    password=read_configuration('GITHUB_PASSWORD', '/var/secrets/secrets.env'),
    token=read_configuration('GITHUB_TOKEN', '/var/secrets/secrets.env')
)

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('github-proxy')
logger.setLevel(logging.INFO)


@app.route('/repos/<username>')
@cache.memoize(timeout=30 * 60)
def list_repos(username):
    logger.info('Listing repositories for user %s', username)

    results = list()
    repos = list(api.list_repos(username))

    for repo in repos:
        repository_name = repo.get('name')

        logger.info('Processing repo: %s/%s', username, repository_name)

        details = {
            key: repo.get(key) for key in
            ('name', 'full_name', 'html_url', 'description', 'fork',
             'created_at', 'updated_at', 'pushed_at', 'language', 'homepage',
             'stargazers_count', 'watchers_count', 'open_issues_count')
        }

        details['owner'] = {
            key: repo.get('owner').get(key) for key in
            ('avatar_url', 'gravatar_id', 'html_url', 'login')
        }

        results.append(details)

    return jsonify(results)


@app.route('/repos/<username>/<repository>/readme')
@app.route('/repos/<username>/<repository>/readme/html')
@cache.memoize(timeout=30 * 60)
def get_readme_html(username, repository):
    logger.info('Fetching HTML readme for %s/%s', username, repository)

    readme = api.get_readme_html(username, repository)

    if readme:
        return readme

    else:
        return make_response('', 404, )


@app.route('/repos/<username>/<repository>/readme/raw')
@cache.memoize(timeout=30 * 60)
def get_readme_raw(username, repository):
    logger.info('Fetching raw readme for %s/%s', username, repository)

    readme = api.get_readme_raw(username, repository)

    if readme:
        return readme, 200, {'Content-Type': 'text/plain'}

    else:
        return make_response('', 404, )


@app.route('/repos/<username>/<repository>/commit-stats')
@cache.memoize(timeout=30 * 60)
def get_commit_stats(username, repository):
    logger.info('Fetching commit statistics for %s/%s', username, repository)

    return jsonify(api.get_commit_stats(username, repository))


if __name__ == '__main__':  # pragma: no cover
    app.run(host=os.environ.get('HTTP_HOST', '127.0.0.1'),
            port=int(os.environ.get('HTTP_PORT', '5000')),
            threaded=True, debug=False)
