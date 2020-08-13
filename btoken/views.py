import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

# Create your views here.
from django.views import View

from user.models import UserProfile


class TokenView(View):

    def post(self,request):

        json_str=request.body
        json_obj=json.loads(json_str)
        username=json_obj['username']
        password=json_obj['password']

        user=UserProfile.objects.filter(username=username)[0]
        print(user)

        if not user:
            result={'code':10200,'error':'user is not exist'}
            return JsonResponse(result)

        p_m = hashlib.md5()
        p_m.update(password.encode())
        password_m = p_m.hexdigest()
        if password_m != user.password:
            result = {'code': 10201, 'error': 'password is error'}
            return JsonResponse(result)
        token=make_token(username)
        result={'code': 200,'username':username,'data':{'token':token.decode()}}



        # 获取用户名和密码
        # 校验----------
        # 校验成功 签发token 有效期为一天
        return JsonResponse(result)

def make_token(username,expire=3600*24):

    key=settings.JWT_TOKEN_KEY
    now=time.time()
    payload={'username':username,'exp':now+expire}

    return jwt.encode(payload,key,algorithm='HS256')

