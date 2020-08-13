from ddblog.celery import app
from tools.sms import YunTongXing
from django.conf import settings


@app.task
def send_sms(phone,code):
    x = YunTongXing(settings.SMS_ACCOUNT_ID, settings.SMS_ACCOUNT_TOKEN, settings.SMS_ACCOUNT_APPID,        settings.SMS_TEMPLATE_ID)


    res = x.run(phone, code)
    return res


