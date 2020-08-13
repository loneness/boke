import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from tools.logging_dec import logging_check, get_user_by_request
from .models import Topic
from user.models import UserProfile
from tools.cache_dec import topic_cache
from message.models import Message

#异常码 10300 - 10399


# Create your views here.
class TopicViews(View):


    def make_topics_res(self, author, author_topics):
        #博主主页 文章列表页的返回值

        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            #2018-09-03 10:30:20
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.nickname
            topics_res.append(d)

        res = {'code': 200, 'data': {}}
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    def make_topic_res(self, author, author_topic, is_self):
        #is_self: True 博主访问自己

        #上一篇 下一篇
        if is_self:
        #下一篇
        #select * from topic_topic where id > 当前文章id and user_profile_id = 'author' order by id ASC limit 1
            next_topic = Topic.objects.filter(id__gt=author_topic.id, user_profile_id=author.username).first()

        #上一篇
        #select * from topic_topic where id < 当前文章id and user_profile_id = 'author' order by id DESC limit 1
            last_topic = Topic.objects.filter(id__lt=author_topic.id, user_profile_id=author.username).last()
        else:
            #考虑权限
            next_topic = Topic.objects.filter(id__gt=author_topic.id, user_profile_id=author.username, limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, user_profile_id=author.username,limit='public').last()


        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None

        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None

        #生成message返回值
        all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')

        msg_list = []
        r_dict = {}
        msg_count = 0
        print(all_messages)
        for msg in all_messages:
            if  msg.parent_message:
                print(type(msg.parent_message))
                #回复
                r_dict.setdefault(msg.parent_message, [])
                r_dict[msg.parent_message].append({'msg_id':msg.id,'content':msg.content,'publisher':msg.user_profile.nickname, 'publisher_avatar':str(msg.user_profile.avatar), 'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                #留言/评论
                msg_count+=1

                msg_list.append({'id':msg.id,'content':msg.content, 'publisher':msg.user_profile.nickname,'publisher_avatar': str(msg.user_profile.avatar), 'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'reply':[]})

        print(msg_list)
        #将 留言和回复进行关联
        for m in msg_list:
            if m['id'] in r_dict:
                m['reply'] = r_dict[m['id']]

        #生成详情页的返回值
        result = {'code':200, 'data':{}}
        result['data']['nickname'] = author.nickname
        result['data']['title'] = author_topic.title
        result['data']['category'] = author_topic.category
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nickname
        result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        result['data']['last_id'] = last_id
        result['data']['last_title'] = last_title
        result['data']['next_id'] = next_id
        result['data']['next_title'] = next_title
        #评论相关
        result['data']['messages'] = msg_list
        result['data']['messages_count'] = msg_count
        return result

    def clear_topic_caches(self, request):
        #/v1/topics/guoxiaonao
        #/v1/topics/guoxiaonao?category=tec
        #/v1/topics/guoxiaonao?category=no-tec
        all_path = request.get_full_path()
        all_key_p = ['topic_cache_self_', 'topic_cache_']
        all_keys = []
        for key_p in all_key_p:
            for key_h in ['', '?category=tec', '?category=no-tec']:
                all_keys.append(key_p + all_path + key_h)

        print(all_keys)
        #删除
        # for del_key in all_keys:
        #     cache.delete(del_key)
        cache.delete_many(all_keys)


    @method_decorator(logging_check)
    def post(self, request, author_id):
        #发表文章
        author = request.myuser
        json_str = request.body
        json_obj = json.loads(json_str)
        #获取json串内容
        #{"content":"<p>aaaasdasdasd<br></p>","content_text":"aaaasdasdasd","limit":"public","title":"aaaaaaa","category":"tec"}
        #带有html的 文章内容
        content = json_obj['content']
        #纯文本的文章内容 - 用来截取文章简介
        content_text = json_obj['content_text']
        #根据 content_text 前20个字为文章简介
        introduce = content_text[:20]
        title = json_obj['title']
        #防止xss注入
        import html
        title = html.escape(title)


        limit = json_obj['limit']
        if limit not in ['public', 'private']:
            result = {'code':10300, 'error':'The limit is error'}
            return JsonResponse(result)

        category = json_obj['category']
        if category not in ['tec', 'no-tec']:
            result = {'code':10301, 'error':'The category is error'}
            return JsonResponse(result)

        #数据入库
        Topic.objects.create(title=title, content=content,limit=limit, category=category,introduce=introduce,user_profile=author)

        self.clear_topic_caches(request)

        return JsonResponse({'code':200, 'username':author.username})


    @method_decorator(topic_cache(600))
    def get(self, request, author_id):
        print('----topic get view in')
        #/v1/topics/guoxiaonao
        #/v1/topics/guoxiaonao?category=tec|no-tec
        #获取用户guoxiaonao的文章列表
        #1,访问者 visitor
        #2, 博主  author

        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code':10305, 'error':'The author id is error'}
            return JsonResponse(result)
        #尝试获取访问者的身份
        visitor_username = get_user_by_request(request)

        t_id = request.GET.get('t_id')
        is_self = False
        if t_id:
            #/v1/topics/guoxiaonao?t_id=xxx
            #获取指定文章数据 [文章详情页]
            if visitor_username == author_id:
                is_self = True
                #博主访问自己
                try:
                    author_topic = Topic.objects.get(id=t_id, user_profile_id=author_id)
                except Exception as e:
                    result = {'code':10310, 'error': 'The topic id is error'}
                    return JsonResponse(result)
            else:
                #非博主访问自己-只能看 public 文章
                try:
                    author_topic = Topic.objects.get(id=t_id, user_profile_id=author_id, limit='public')
                except Exception as e:
                    result = {'code':10310, 'error': 'The topic id is error'}
                    return JsonResponse(result)
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            # /v1/topics/guoxiaonao
            # /v1/topics/guoxiaonao?category=tec|no-tec
            #获取用户批量文章数据 [文章列表页]
            category = request.GET.get('category')
            filter_category = False
            if category in ['tec', 'no-tec']:
                filter_category = True

            if visitor_username == author_id:
                #博主访问自己的博客
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id)
            else:
                #非博主访问博主的博客
                if filter_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public', category=category)
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public')

            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)












