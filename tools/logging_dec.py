from django.http import JsonResponse
import jwt
from django.conf import settings

from user.models import UserProfile


def logging_check(func):
    def wrap(request, *args, **kwargs):
        # 请求头 - Authorization
        token = request.META.get('HTTP_AUTHORIZATION')

        # 校验token
        if not token:
            result = {'code': 403, 'error': 'please login'}
            return JsonResponse(result)
        # 校验token
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
        except Exception as e:
            print('--check login error %s' % (e))
            result={'code':403,'error':'please login'}
            return JsonResponse(result)

        username = res['username']
        user = UserProfile.objects.get(username=username)

        request.myuser = user

        # 校验失败 则返回{'code':403,'error':Please login}

        #
        return func(request, *args, **kwargs)

    return wrap


def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    if not token:
        return None

    try:
        res=jwt.decode(token,settings.JWT_TOKEN_KEY)
    except Exception as e:
        print('-get user jwt error %s'%e)
        return None

    username=res['username']
    #TODO 还要不要查数据库
    return username



