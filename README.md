# VLR Scraper - VLR.gg Web Scraper

VLR Scrapy is a web scraper for vlr.gg that allows users to view their upvote/downvote/net counts and their most upvoted/downvoted posts.

<img src = "https://github.com/numan-7/VLR-Scraper/assets/101899800/fce5589f-e3ab-4a68-b26d-3646afdaa964" />

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone git@github.com:numan-7/VLR-Scraper.git
$ cd VLR-Scraper
```

Install Docker & Docker-Compose:

```sh
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install docker.io
$ sudo apt install docker-compose
$ sudo usermod -aG docker $USER
```

Verify Docker & Docker Compose Installations:
```sh
$ docker --version
$ docker-compose --version
```

It's recommended to create a virtual environment for running the application. 

This step is optional but advisable:

```sh
$ pip install virtualenv (if not installed already)
$ virtualenv env
$ source env/bin/activate
```

Then grant docker script executable permissions and run it:

```sh
(env)$ chmod +x docker_run_server.sh
(env)$ ./docker_run_server.sh
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

And navigate to `http://127.0.0.1:8000/`.

To close down docker container:
```sh
(env)$ docker compose down
```

To leave virtual env:
```sh
(env)$ deactive
```
