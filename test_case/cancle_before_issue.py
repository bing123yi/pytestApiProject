from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from conf.header_conf import headers,lvzhou_headers
from util.opr_json import OperationJson


# 意健险-新契约-承保前撤件
class cancleBeforeIssue:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("group_insurance")
        self.host_url = self.api_url_datas['test_url']
        self.headers = headers
        self.lvzhou_headers = lvzhou_headers
        self.delete_list = []
        self.delete_No = ''

    def run(self):
        # self.search_task()  # 人工核保
        self.delete_sele_null()  # 撤销新契约未录入投保单
        # self.test_cancle_by_liangzhixiao()

    def search_task(self):
        # 查询列表数据
        # 查询人工核保列表
        get_task_url = self.api_url_datas['getPubTask'].format(self.host_url)
        request_data = {
            "uwLevel": 1,
            "currentPage": 1,
            "pageSize": 100,
            "uwPolicyCategory": 1

        }
        res = self.API.send_request(get_task_url, 'post', request_data, self.headers, None, 1)
        if len(res['result']['resultList']) != 0:
            for i in res['result']['resultList']:

                if 1:
                    print(i['objectNo'])
                    delete_info = {
                        'id': i['objectId'],
                        'objectNo': i['objectNo']
                    }
                    self.delete_list.append(delete_info)

    def delete_sele_null(self):
        # 查询个人投保单录入页面
        url = '{}/api/artemis/api/artemis/queryPolicy?groupPolicyType=1&currentPage=1&pageSize=50'.format(self.host_url)
        response = self.API.send_request(url, 'get', None, headers)
        my_policy_list = response['result']['data']
        for my_policy in my_policy_list:
            print("开始循环遍历list")
            if my_policy['partnerName'] is None or my_policy['holderName'] is None or "自动化调试" in my_policy['holderName'] :
                applyGroupId = my_policy['id']
                applyGroupNo = my_policy['applyGroupNo']
                # 进行撤件
                url = self.api_url_datas['callBackSavePolicy'].format(self.host_url, applyGroupId, applyGroupNo)
                response = self.API.send_request(url, 'get', None, headers)



    # 承保前撤件
    def test_cancle_by_liangzhixiao(self):
        # time.sleep(3)
        if len(self.delete_list) == 0:
            print("删除列表为空，请检查~~~")
            exit()
        else:
            for delete_No in self.delete_list:
                # 团险进行撤件
                print(delete_No['objectNo'])
                url = self.api_url_datas['callBackSavePolicy'].format(self.host_url, delete_No['id'],
                                                                      delete_No['objectNo'])
                response = self.API.send_request(url, 'get', None, headers, None, 1)

                #  # 批改撤件
                #  # 先按批单号查询
                # url = '{}/api/correcting/v1/endorsement/cancellation/query'.format(self.host_url)
                # request_data = {
                #     "currentPage": 1,
                #     "pageSize": 10,
                #     "endorsementNo": delete_No['objectNo']
                # }
                # res = self.API.send_request(url, 'post_json', request_data, self.headers)
                #
                # delete_url = '{}/api/correcting/v1/endorsement/cancellation/cancel'.format(self.host_url)
                #
                # if len(res['result']['resultList']) > 0:
                #     for i in res['result']['resultList']:
                #         request_data = {
                #             "cancelReason": "1",
                #             "resaonDescp": "122",
                #             "haGroupPolicyId": i['haGroupPolicyId'],
                #             "haGroupPolicyNo": i['haGroupPolicyNo'],
                #             "endorsementNo": i['endorsementNo'],
                #             "operator": "liangzhixiao",
                #             "csType": 22
                #         }
                #         res = self.API.send_request(delete_url, 'post_json', request_data, self.headers, None, 1)
                #
                #  执行sql数据库删
                if 1>2:
                    sql_url = 'https://oasis.zhonganinfo.com/lvz/query/executeSql'
                    request_data = {
                        "env": "PRE",
                        "dbId": 2627,
                        "sql": "UPDATE ha_uw_policy SET is_deleted = 'Y' WHERE object_no = '{}'".format(delete_No['objectNo']),
                        "modifyFlag": "Y"
                    }
                    res = self.API.send_request(sql_url, 'post_json', request_data, self.lvzhou_headers, None, 1)


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])
    test = cancleBeforeIssue()
    test.run()
