from django.db import models
import random
from django.utils import timezone


def default_sign():
    signs = ['come on ~~', 'i am very happy']
    return random.choice(signs)


# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='用户名', primary_key=True)
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    email = models.EmailField()
    password = models.CharField(max_length=32)
    sign = models.CharField(max_length=50, verbose_name='个人签名', default=default_sign)
    info = models.CharField(max_length=150, verbose_name='个人简介')
    avatar = models.ImageField(upload_to='avatar', null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone=models.CharField(max_length=11,default='')

    class Meta:
        db_table = 'user_user_profile'
