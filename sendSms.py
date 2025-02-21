import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
import json


ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
SMS_TEMPLATE_CODE = os.getenv('ALIYUN_SMS_TEMPLATE_CODE')
SIGN_NAME = "代码管理"  # 签名名称

def send_sms(phone_number, name):
    client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, 'cn-hangzhou')

    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone_number)
    request.add_query_param('SignName', SIGN_NAME)
    request.add_query_param('TemplateCode', SMS_TEMPLATE_CODE)
    request.add_query_param('TemplateParam', json.dumps({"name": name}))

    try:
        client.do_action_with_exception(request)
    except (ClientException, ServerException) as e:
        print(f"短信发送失败，异常信息：{str(e)}")

# 示例调用
phone_number = "18570382437"
name = "张俊琛"
result = send_sms(phone_number, name)
print(result)