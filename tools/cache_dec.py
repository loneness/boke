from django.core.cache import cache

from .logging_dec import get_user_by_request

def topic_cache(expire):
    def _topic_cache(func):
        def wrapper(request,*args,**kwargs):
            # 根据查询字符串区分当前业务
            # 根据有没有 t_id 查询字符串 区分当前查的是批量数据和还是某个文章的数据
            if 't_id' in request.GET.keys():
            #  拿具体文章
                return func(request,*args,**kwargs)
            #以下为批量获取
            # 检查访问者的身份
            visitor_username=get_user_by_request(request)
            author_username=kwargs['author_id']
            print('visitor is %s author is %s'%(visitor_username,author_username))

            if visitor_username==author_username:
                cache_key=('topic_cache_self_%s'%(request.get_full_path()))
            else:
                cache_key = ('topic_cache_%s' % (request.get_full_path()))

            print('---cache key is %s'%(cache_key))

            res=cache.get(cache_key)

            if res:
                print('---cache in')
                return res

            res=func(request,*args,**kwargs)
            cache.set(cache_key,res,expire)

            return res



            # 根据访问者身份和博主的关系,生成特定的cache_key




        return wrapper
    return _topic_cache