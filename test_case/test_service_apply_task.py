from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from conf.header_conf import headers
from util.opr_json import OperationJson
import os


# 公共功能-增值服务管理-保单服务审核与派发
# 添加增值服务
class serviceApplyTask:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("service_apply_task_url")
        # 选择环境
        self.host_url = self.api_url_datas['uat_url']  # 环境地址
        self.headers = headers  # 登陆人cookie

        self.policyNo = "HA1200001784870358"  # 保单号
        self.serviceName = "肿瘤特药"  # 服务名称 暂时只支持肿瘤特药

    # 创建增值服务
    def test_01_create_manual(self):
        # time.sleep(3)
        # 查询保单是否支持增值服务
        request_data = {
            "policyNo": self.policyNo,
            "operator": "liangzhixiao"
        }
        supplier_url = self.api_url_datas['supplierPolicyNo'].format(self.host_url)
        response = self.API.send_request(supplier_url, 'post_json', request_data, headers)

        if response['result'] == None or len(response['result']['serviceInfoList']) == 0:
            print('该保单没有查到增值服务，请检查！！！')
            exit()
        serviceInfoList = response['result']['serviceInfoList']
        for serviceInfo in serviceInfoList:
            if serviceInfo['serviceName'] == self.serviceName:
                self.serviceId = serviceInfo['serviceId']
        # 创建增值服务
        request_data = {
            "operator": "liangzhixiao",
            "operatorChineseName": "梁志骁",
            "policyNo": self.policyNo,
            "serviceId": self.serviceId,
            "serviceName": self.serviceName
        }
        create_url = self.api_url_datas['createManual'].format(self.host_url)
        response = self.API.send_request(create_url, 'post_json', request_data, headers)
        if response['result'] == None:
            print('创建服务失败' + response['message'])
            exit()
        taskId = response['result']

        # 保存增值服务

        code_url = self.api_url_datas['withPackcode'].format(self.host_url)
        request_data = {"policyNo": self.policyNo, "serviceId": self.serviceId, "operator": "liangzhixiao"}
        response = self.API.send_request(code_url, 'post_json', request_data, headers)
        if response['result'] == None:
            print('项目名称查询失败' + response['message'])
            exit()
        packcodelist = response['result']
        itemCode = ''
        for packcode in packcodelist:
            if packcode['itemName'] == '用药服务':
                itemCode = packcode['itemCode']
                itemId = packcode['itemId']
        request_data = {
            "operator": "liangzhixiao",
            "operatorChineseName": "梁志骁",
            "taskId": taskId,
            "saveTemporary": "N",
            "reservationProvinceCode": "110000",
            "reservationCityCode": "110100",
            "reservationCountyCode": "110101",
            "residentialProvinceCode": "110000",
            "residentialCityCode": "110100",
            "residentialCountyCode": "110101",
            "familyProvinceCode": "110000",
            "familyCityCode": "110100",
            "familyCountyCode": "110101",
            "reservationHospitalCode": "0000009",
            "reservationDepartment": "预约科室",
            "intentionServiceTime": "2021-07-07",
            "familyAddressDetail": "家庭住址详细地址详细地址详细地址详细地址详细地址详细地址",
            "contactName": "联系人",
            "contactPhoneNo": "13262640680",
            "emailAddress": "liangzhixiao@qq.com",
            "applyItemList": [{
                "itemCode": itemCode,
                "itemName": '用药服务',
                "itemId": itemId,
                "packCode": None
            }],
            "diseaseDesc": "病情描述病情描述"
        }
        save_url = self.api_url_datas['saveManual'].format(self.host_url)
        response = self.API.send_request(save_url, 'post_json', request_data, headers)
        if response['code'] == '20001':
            print('该保单有相同的在途的服务申请！')
            exit()

        # 服务申请附件上传
        # 必须上传附件列表 necessaryMaterial: "BR,CL,I,IR,JR,YR,ZL,ZR"
        attachmentType_list = ['BR', 'CL', 'I', 'IR', 'JR', 'YR', 'ZL', 'ZR']
        upload_url = self.api_url_datas['uploadManual'].format(self.host_url)
        for attachmentType in attachmentType_list:
            file_path = self.get_file_path()
            files_open = open(file_path, 'rb')
            files = {'files': files_open}
            request_data = {
                "taskId": taskId,
                "attachmentType": attachmentType,
                "operator": 'liangzhixiao'
            }
            save_response = self.API.send_request(upload_url, 'post_file', request_data, self.headers, files)

        #  提交
        request_data = {
            "taskId": taskId,
            "operator": "liangzhixiao",
            "operatorChineseName": "梁志骁"
        }
        save_url = self.api_url_datas['submitManual'].format(self.host_url)
        response = self.API.send_request(save_url, 'post_json', request_data, headers)

    # 领取任务到个人任务列表中
    def test_02_chang_service_status(self):
        # time.sleep(3)
        url = self.api_url_datas['serviceTask'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "currentPage": 1,
            "pageSize": 100,
            "operator": "liangzhixiao",
            "searchSource": 0,
            "searchType": 1
        }
        # print(request_data)
        # 查询服务任务id
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        resultList = save_response['result']['resultList']
        taskId = resultList[len(resultList) - 1]['taskId']
        Status_url = self.api_url_datas['statusChange'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "operator": "liangzhixiao",
            "operatorChineseName": "梁志骁",
            "taskId": taskId,
            "taskStatus": "CLAIM_CHECKING"
        }

        response = self.API.send_request(Status_url, 'post_json', request_data, self.headers)

    # 领取任务到个人任务列表中
    def test_03_chang_service_status(self):
        # time.sleep(3)
        url = self.api_url_datas['serviceTask'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "currentPage": 1,
            "pageSize": 100,
            "operator": "liangzhixiao",
            "searchSource": 1,
            "searchType": 1
        }
        # print(request_data)
        # 查询服务任务id
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        resultList = save_response['result']['resultList']
        taskId = resultList[len(resultList) - 1]['taskId']
        Status_url = self.api_url_datas['statusChange'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "operator": "liangzhixiao",
            "operatorChineseName": "梁志骁",
            "taskId": taskId,
            "taskStatus": "DISTRIBUTE_CHECKING"
        }

        response = self.API.send_request(Status_url, 'post_json', request_data, self.headers)


    def get_file_path(self):
        # 当前路径
        current_path = os.path.abspath(os.path.dirname(__file__))
        # print(current_path)
        # 上一级路径（父级路径）
        parent_path = os.path.dirname(current_path)
        file_path = parent_path + "\\upload_file\\" + '增值服务-肿瘤特药-附件上传.jpg'
        return file_path


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])

    test = serviceApplyTask()
    test.test_01_create_manual()  # 创建服务
    test.test_02_chang_service_status()  # 处理服务任务
