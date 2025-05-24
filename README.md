# Social Media API 

RESTful API platform for social networks

## Installation

Python3 must be already installed

```shell
git clone https://github.com/mtiunov/social-media-platform.git
cd social-media-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```


## Features

* User Registration and Authentication
* User Profile
* Follow/Unfollow
* Post Creation and Retrieval
* Likes and Comments
* Schedule Post creation using Celery


## Background Tasks (Celery & Redis)

To enable scheduled post creation, Celery is used with Redis as the broker. Make sure to start Redis before running Celery.

### Start Redis Server
```shell
redis-server

celery -A social_media_platform worker --loglevel=info
celery -A social_media_platform beat --loglevel=info
from social_media_platform.tasks import scheduled_post_creation
scheduled_post_creation.delay()

