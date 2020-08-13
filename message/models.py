from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    #留言/回复
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.CharField(verbose_name='内容', max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    parent_message = models.IntegerField(verbose_name="回复的留言ID", default=0)