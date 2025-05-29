# Social Media API 

RESTful API platform for social networks

## Installation

- Python3 must be already installed
- **Docker**: Check to see if Docker is installed and running on your machine.

```shell
git clone https://github.com/mtiunov/social-media-platform.git
cd social-media-platform
```
## How to run

- The **docker-compose build** command creates Docker images for all services (Django API, Celery, Celery Beat, Redis).

- The **docker-compose up** command starts services.


## Features

* User Registration and Authentication
* User Profile
* Follow/Unfollow
* Post Creation and Retrieval
* Likes and Comments
* Schedule Post creation using Celery


## Background Tasks (Celery & Redis)

To enable scheduled post creation, Celery is used with Redis as the broker. Make sure to start Redis before running Celery.
