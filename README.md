# VLR Scraper - VLR.gg Web Scraper

VLR Scrapy is a web scraper for vlr.gg that allows users to view their upvote/downvote/net counts and their most upvoted/downvoted posts.

<img src = "https://github.com/numan-7/VLR-Scraper/assets/101899800/63947b32-97bf-4ebb-aa46-020feae071bf" />

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

Then grant docker script executable permissions and run it:

```sh
$ chmod +x docker_run_server.sh
$ ./docker_run_server.sh
```

And navigate to `http://127.0.0.1:8000/`.

To close down docker container:
```sh
$ docker compose down
```
