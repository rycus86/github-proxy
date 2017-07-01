# GitHub Proxy

A simple `Python` [Flask](http://flask.pocoo.org) *REST* server to proxy calls to *GitHub*.

[![Build Status](https://travis-ci.org/rycus86/github-proxy.svg?branch=master)](https://travis-ci.org/rycus86/github-proxy)
[![Build Status](https://img.shields.io/docker/build/rycus86/github-proxy.svg)](https://hub.docker.com/r/rycus86/github-proxy)
[![Coverage Status](https://coveralls.io/repos/github/rycus86/github-proxy/badge.svg?branch=master)](https://coveralls.io/github/rycus86/github-proxy?branch=master)
[![Code Climate](https://codeclimate.com/github/rycus86/github-proxy/badges/gpa.svg)](https://codeclimate.com/github/rycus86/github-proxy)

## Usage

The *GitHub* API is implemented using [agithub](https://github.com/jpaugh/agithub) and supports
authenticated calls (with better rate limiting) using these environment variables:

- `GITHUB_USERNAME`: a valid *GitHub* username
- `GITHUB_PASSWORD`: password for the same *GitHub* account
- `GITHUB_TOKEN`: alternatively an authenticated *GitHub* token can be used instead of
  username and password

To get a reference to the `ApiClient` class use something like:
```python
api = ApiClient(username=os.environ.get('GITHUB_USERNAME'),
                password=os.environ.get('GITHUB_PASSWORD'),
                token=os.environ.get('GITHUB_TOKEN'))
```

The `api.ApiClient` class wraps endpoints with the following methods:

- `list_repos(username)`: returns a list of *all* repositories for the *GitHub* user
  identified by `username` - regardless of pagination (e.g. from all pages)
- `get_readme_html(owner, repository)`: returns the *HTML README* of the
  `owner/repository` *GitHub* repository
- `get_readme_raw(owner, repository)`: returns the *raw plain text README* of the
  `owner/repository` *GitHub* repository
- `get_commit_stats(owner, repository)`: returns a dictionary containing the total number
  of commits in the `owner/repository` *GitHub* repository plus the author, date and message
  of the last commit

The `app` module is responsible for the *REST* presentation layer exposing *JSON* endpoints.
The exposed endpoints are cached using [Flask-Cache](https://pythonhosted.org/Flask-Cache).

Configuration options:

- `HTTP_HOST`: the host (interface) for *Flask* to bind to (default: `127.0.0.1`)
- `HTTP_PORT`: the port to bind to (default: `5000`)
- `CORS_ORIGINS`: comma separated list of *origins* to allow *cross-domain* `GET` requests from
  (default: `http://localhost:?.*`)

To allow connections from other hosts apart from `localhost` set the `HTTP_PORT` environment
variable to `0.0.0.0` or as appropriate.

List of endpoints:

- `/repos/<username>`: lists the repositories of the `<username>` *GitHub* user  
  This will be a list of objects with a reduced set of properties from
  `ApiClient.list_repos(<username>)`
- `/repos/<username>/<repository>/readme` or  
  `/repos/<username>/<repository>/readme/html`: an *HTML* endpoint returning the 
  rendered *README* markup for the `<username>/<repository>` *GitHub* repository
- `/repos/<username>/<repository>/readme/raw`: an *plain text* endpoint returning the 
  raw *README* contents for the `<username>/<repository>` *GitHub* repository
- `/repos/<username>/<repository>/commit-stats`: returns the commit statistics for the
  `<username>/<repository>` *GitHub* repository  
  The object is the same as the return value of `ApiClient.get_commit_stats(owner, repository)`

## Docker

The web application is built as a *Docker* image too based on *Alpine Linux*
for 3 architectures with the following tags:

- `latest`: for *x86* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/github-proxy.svg)](https://microbadger.com/images/rycus86/github-proxy "Get your own image badge on microbadger.com")
- `armhf`: for *32-bits ARM* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/github-proxy:armhf.svg)](https://microbadger.com/images/rycus86/github-proxy:armhf "Get your own image badge on microbadger.com")
- `aarch64`: for *64-bits ARM* hosts  
  [![Layers](https://images.microbadger.com/badges/image/rycus86/github-proxy:aarch64.svg)](https://microbadger.com/images/rycus86/github-proxy:aarch64 "Get your own image badge on microbadger.com")

`latest` is auto-built on [Docker Hub](https://hub.docker.com/r/rycus86/github-proxy)
while the *ARM* builds are uploaded from [Travis](https://travis-ci.org/rycus86/github-proxy).

To run it:
```shell
docker run -d --name="github-proxy" -p 5000:5000           \
  -e GITHUB_USERNAME='user' -e GITHUB_PASSWORD='pass'      \
  -e CORS_ORIGINS='http://site.example.com,*.website.com'  \
  rycus86/github-proxy:latest
```

Or with *docker-compose* (for a *Raspberry Pi* for example):
```yaml
version: '2'
services:

  github-proxy:
    image: rycus86/github-proxy:armhf
    expose:
      - "5000"
    restart: always
    environment:
      - HTTP_HOST=0.0.0.0
    env_file:
      - github-secrets.env
```

This way you can keep the secrets in the `env_file` instead of passing them to the *Docker*
client from the command line.
