import hashlib
import time

import jwt
from django.http import HttpResponse, JsonResponse

import json
from .models import UserProfile
from tools.logging_dec import logging_check

from django.utils.decorators import method_decorator

from django.conf import settings
# Create your views here.
from django.views import View

from tools.sms import YunTongXing
from .tasks import send_sms

import random
from django.core.cache import cache
from django.conf import settings




def users_view(request):
    return HttpResponse('--user view')


class UsersView(View):

    def get(self, request, username=None):

        if username:
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                print('--get user error %s' % e)
                result = {'code': 10202, 'error': 'the username is wrong'}
                return JsonResponse(result)

            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        data[k] = getattr(user, k)

                result = {'code': 200, 'username': username, 'data': data}

            else:
                result = {'code': 200,
                          'data': {'info': user.info, 'sign': user.sign, 'nickname': user.nickname, 'avatar': str(
                              user.avatar)}}

            return JsonResponse(result)
        else:
            pass

        return HttpResponse('--user get')

    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)

        username = json_obj['username']
        email = json_obj['email']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        phone = json_obj['phone']
        sms_num = json_obj['sms_num']

        # 校验验证码
        old_code=cache.get('sms_%s'%(phone))
        if not old_code:
            result={'code':10113,'error':'code is wrong'}
            return JsonResponse(result)

        if int(sms_num) != old_code:
            result = {'code': 10114, 'error': 'code is wrong'}
            return JsonResponse(result)


        if len(username) > 11:
            result = {'code': 10100, 'error': 'The name is wrong'}

        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10101, 'error': 'The username is already exist'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'code': 10102, 'error': 'the password is error'}
            return JsonResponse(result)
        p_m = hashlib.md5()
        p_m.update(password_1.encode())
        password_m = p_m.hexdigest()
        try:
            user = UserProfile.objects.create(username=username, nickname=username, email=email, password=password_m,
                                              phone=phone)
        except Exception as e:
            print('create error is %s' % (e))
            result = {'code': 10103, 'error': 'The username is already exist'}
            return JsonResponse(result)

        token = make_token(username)
        return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})

        # return JsonResponse({'code': 200,'data':{}})
        # return HttpResponse('--user post')

    @method_decorator(logging_check)
    def put(self, request, username):
        # method_decorator 将传入的函数装饰器转换为 方法装饰器
        json_str = request.body
        json_obj = json.loads(json_str)

        request.myuser.sign = json_obj['sign']
        request.myuser.nickname = json_obj['nickname']
        request.myuser.info = json_obj['info']
        request.myuser.save()

        result = {'code': 200, 'username': request.myuser.username}
        return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'username': username, 'exp': now + expire}

    return jwt.encode(payload, key, algorithm='HS256')


@logging_check
def user_avatar(request, username):
    if request.method != 'POST':
        result = {'code': 10105, 'error': 'please give me POST'}
        return JsonResponse(result)

    user = request.myuser

    user.avatar = request.FILES['avatar']
    user.save()

    result = {'code': 200, 'username': user.username}
    return JsonResponse(result)


def sendSMS(request):

        json_str = request.body
        json_obj = json.loads(json_str)
        phone = json_obj['phone']
        print(phone)
        cache_key='sms_%s'%(phone)
        old_code=cache.get(cache_key)
        if old_code:
            result={'code':10112,'error':'请稍后再来'}
            return JsonResponse(result)

        code = random.randint(0, 9999)
        cache.set(cache_key, code, 65)
        print(code)

        # 异步发送
        send_sms.delay(phone,code)

        # x = YunTongXing(settings.SMS_ACCOUNT_ID, settings.SMS_ACCOUNT_TOKEN, settings.SMS_ACCOUNT_APPID, settings.SMS_TEMPLATE_ID)
        # try:
        #     res = x.run(phone, code)
        # except Exception as e:
        #     print('send message is error %s'%e)
        #     result = {'code': 10301, 'error': 'send message is error'}
        #     return JsonResponse(result)


        result = {'code': 200}


        return JsonResponse(result)
