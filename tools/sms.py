import base64
import datetime
import hashlib
import json

import requests  # 用于库可以发出http请求


class YunTongXing():
    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountsid, accountToken, appId, templateId):
        self.accountSid = accountsid
        self.accountToken = accountToken
        self.appId = appId
        self.templateId = templateId

    # 构造url
    def get_resquest_url(self, sig):
        self.url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s' % (self.accountSid, sig)

        return self.url

    def get_timestamp(self):
        # 生成时间戳
        now = datetime.datetime.now()
        now_str = now.strftime('%Y%m%d%H%M%S')
        return now_str

    def get_sig(self, timestamp):
        s = self.accountSid + self.accountToken + timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()

    def get_request_header(self, timestamp):
        s = self.accountSid + ':' + timestamp
        b_s = base64.b64encode(s.encode()).decode()
        return {
            'Accept': 'application/json',
            'content-Type': 'application/json;charset=utf-8',
            'Authorization': b_s,
        }

    def get_request_body(self, phone, code):
        #   构建请求体
        data = {
            "to": phone,
            'appId': self.appId,
            'templateId': self.templateId,
            'datas': [code, "3"]
        }
        return data

    def do_request(self, url, header, body):
        # 发请求
        res = requests.post(url, headers=header, data=json.dumps(body))
        return res.text

    def run(self, phone, code):
        timestamp = self.get_timestamp()
        sig = self.get_sig(timestamp)
        url = self.get_resquest_url(sig)
        header = self.get_request_header(timestamp)
        body = self.get_request_body(phone, code)
        res = self.do_request(url, header, body)
        print(url)



if __name__ == '__main__':
    aid = '8aaf0708730554fa017309cfe1c801c6'
    atoken = 'f76d52b7725e4514904a725c790b474b'
    appid = '8aaf0708730554fa017309cfe2b101cc'
    tid = '1'

    x = YunTongXing(aid, atoken, appid, tid)
    res=x.run('13100603072', '123456')
    print(res)
