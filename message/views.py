import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.logging_dec import logging_check
from topic.models import Topic


@logging_check
def message_view(request,topic_id):


    if request.method != 'POST':
        result={'code':10400,'error':'Please use POST'}
        return JsonResponse(result)

    json_str=request.body
    json_obj=json.loads(json_str)
    content=json_obj['content']
    parent_id=json_obj.get('parent_id',0)

    try:
        topic=Topic.objects.get(id=topic_id)
    except Exception as e:
        result={'code':10401,'error':'the topic id is wrong'}
        return JsonResponse(result)

    user=request.myuser

    Message.objects.create(topic=topic,
content=content,user_profile=user,parent_message=parent_id)
    return JsonResponse({'code':200})
