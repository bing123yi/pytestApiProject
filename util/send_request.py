import requests
import json
import logging
import urllib3

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


class SendRequest:

    def __init__(self):
        pass

    def send_request(self, url, method, request_data=None, header=None, files=None, NotResponse=None):
        logger.info('请求地址: {}'.format(url))
        logger.info('请求参数: {}'.format(request_data))
        print('请求地址: {}'.format(url))
        if request_data is not None:
            request_data = json.loads(json.dumps(request_data, ensure_ascii=False), encoding='utf-8')
            print('请求参数: {}'.format(request_data))
        if header is not None:
            if method == 'get':
                result = requests.get(url=url, headers=header, verify=False)
            elif method == 'post':
                result = requests.post(url=url, data=request_data, headers=header, verify=False)
            elif method == 'post_json':
                result = requests.post(url=url, json=request_data, headers=header, verify=False)
            elif method == 'post_file':
                result = requests.post(url=url, data=request_data, headers=header, files=files, verify=False)
            elif method == 'put':
                result = requests.put(url=url, json=request_data, headers=header, verify=False)

        else:
            if method == 'get':
                result = requests.get(url=url, verify=False)
            elif method == 'post':
                result = requests.post(url=url, data=request_data, verify=False)
            elif method == 'post_json':
                result = requests.post(url=url, json=request_data, verify=False)
            elif method == 'post_file':
                result = requests.post(url=url, data=request_data, files=files, verify=False)
            else:
                result = 'wrong method'

        # 获取接口返回状态码
        # print(result.status_code)

        # print(request_data)

        # print(result.json())
        response = json.dumps(result.json(), indent=2, sort_keys=True)
        logger.info('接口返回结果: {}'.format(response))
        if NotResponse == None:
            print('返回结果: {}'.format(json.loads(response)))

        return json.loads(response)


if __name__ == '__main__':
    test = SendRequest()
    # url = 'https://care.seewo.com/easicare/account/v2/login'
    # request_data = json.dumps({'userName': '10156121201', 'password': 'e10adc3949ba59abbe56e057f20f883e'})
    # print(request_data)
    # header = {'appKey': 'easicare-ios', 'Content-Type': 'application/json',
    #           'deviceId': '917DB1EB-B6E5-4325-BD5D-8A87AC9FACD7'}
    # print(test.send_request(url, 'post', request_data, header))
