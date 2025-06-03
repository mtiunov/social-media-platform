from django.utils import timezone

from posts.models import Post

from celery import shared_task


@shared_task
def planning_created_posts():
    now = timezone.now()
    posts_to_publish = Post.objects.filter(publish_at__lte=now, is_published=False)

    for post in posts_to_publish:
        post.is_published = True
        post.save()
        print(f"Published post {post.id}")
