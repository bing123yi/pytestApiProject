from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from util.opr_excel import OperationExcel
from conf.header_conf import headers, headers_ruixiang, headers_huangmian
from util.opr_json import OperationJson
from format_util import get_reg_no, plan_group_products
import json, os, time, random, string


# 意健险-批改
# 团险线下出单
class groupCorrect:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("group_correct")
        self.product_code_list = ReadYaml().read_yaml("group_product_code")
        # 选择环境
        self.host = 'uat'  # 选择环境

        self.host_url = self.api_url_datas[self.host + '_url']  # 环境地址
        self.headers = headers  # 录入人
        self.view_headers = headers_ruixiang  # 复核人

        self.cs_no = 'CS0200000513503017'  # 批单号
        self.haGroupPolicyNo = 'HA1100001169013726'  # 保单号

        self.valiStringTime = get_reg_no.get_today_date()  # 批改生效日期
        self.validateTime = get_reg_no.get_today_date_correct()  # 生效日期
        self.validateEndTime = '20221112'  # 生效止期
        self.endorsementType = "66"  # 批改项   14 增减被保人   66 新增保险计划  15分单计划变更

        self.opr_xls = OperationExcel(file_name='团批改-增减被保人-6个人 - 新模板')  # 上传被保人清单模板
        self.changeId = None
        self.plancode_list = []
        self.haAppGroupNo = ''  # 投保单号

    def run(self):
        # self.test_01_regist_correcting()  # 生成批单号
        self.test_02_get_change_Id()  # 获取批单号
        self.test_03_set_valiStringTime()  # 填写生效日期
        # self.test_04_insured_import()  # 上传被保人
        # self.test_08_submit_review()  # 批改-提交
        # self.test_09_finish_data_review()  # 批改-复核
        self.test_10_save_group_decision()  # 人工核保


    # 生成批单号
    def test_01_regist_correcting(self):
        # time.sleep(3)
        url = self.api_url_datas['registerEndorsement'].format(self.host_url)
        # print(url)
        if self.haAppGroupNo:
            request_data = {
                "endorsementType": self.endorsementType,
                "haGroupApplyNo": self.haAppGroupNo  # 投保单号
            }
        elif self.haGroupPolicyNo:
            request_data = {
                "endorsementType": self.endorsementType,
                "haGroupPolicyNo": self.haGroupPolicyNo  # 保单号
            }
        else:
            print('请输入保单号或投保单号，请检查')
        # 批改-生成批单号
        if not self.cs_no:
            register_response = self.API.send_request(url, 'post_json', request_data, self.headers)
            if 'code' in register_response.keys() and register_response['code'] == '0':
                self.cs_no = register_response['result']
            else:
                exit()
        # print(register_response)

    def test_02_get_change_Id(self):
        if not self.changeId and self.cs_no:
            url = self.api_url_datas['endorsementSearch'].format(self.host_url)
            request_data = {
                "searchType": 0,
                "currentPage": 1,
                "pageSize": 10,
                "endorsementNo": self.cs_no
            }
            response = self.API.send_request(url, 'post_json', request_data, self.headers)
            if 'result' in response.keys() and response['code'] == '0':
                resultList = response['result']['resultList']
                if len(resultList) > 0:
                    self.changeId = resultList[0]['changeId']
                    print(self.changeId)
            else:
                print('查询不到批单号，请检查')
                exit()
            # print(register_response)

    # 查询信息并填写批单生效日期
    def test_03_set_valiStringTime(self):
        # baseInfo
        url = self.api_url_datas['queryEndorsementPolicy'].format(self.host_url, self.changeId)
        response = self.API.send_request(url, 'get', None, self.headers)
        baseInfo = response['result']

        # haCsPolicy、haCSMain
        url = self.api_url_datas['queryEndorsement'].format(self.host_url, self.changeId)
        response = self.API.send_request(url, 'get', None, self.headers)
        haCsPolicy = response['result']['haCsPolicy']
        haCsPolicy['changeCause'] = 1
        haCsPolicy['entrustType'] = 2

        haCSMain = response['result']['haCSMain']
        haCSMain['valiStringTime'] = self.valiStringTime
        haCSMain['applyMethod'] = 5

        url = self.api_url_datas['saveOrUpdateEndorsement'].format(self.host_url)
        # 批改-填写生效日期（投保单基本信息）
        request_data = {
            "baseInfo": baseInfo,
            "haCsPolicy": haCsPolicy,
            "haCSMain": haCSMain,
            "haCsPolicyAttachments": []
        }
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        if 'code' not in save_response.keys() or save_response['code'] != '0':
            print('生效日期提交错误，请检查')
            exit()

    # 批改-被保人清单导入
    def test_04_insured_import(self):
        # time.sleep(180)

        url = self.api_url_datas['queryPolicyBaseInfo'].format(self.host_url, self.haGroupPolicyNo)
        response = self.API.send_request(url, 'get', None, self.headers)
        haGroupPolicyId = response['result']['haGroupPolicyId']

        url = self.api_url_datas['queryPolicyPlan'].format(self.host_url, haGroupPolicyId, self.cs_no)
        response = self.API.send_request(url, 'get', None, self.headers)
        result_list = response['result']
        for planinfo in result_list:
            self.plancode_list.append(planinfo['planCode'])

        # 获取Excel文件最大的行数
        max_row = self.opr_xls.max_row
        code_index = 0
        # 更新保险计划code  数据是从第6行开始
        for i in range(6, max_row + 1):
            print("被保人姓名: {}".format(self.opr_xls.get_cell_value(i, 1)))  # 打印被保人信息

            # 循环计划列表，确保每个计划都有一个被保人，超出则重新排
            if code_index == len(self.plancode_list):
                code_index = 0
            plan_code_value = self.plancode_list[code_index]
            code_index += 1
            # 写入Excel文件 更新保险计划code  excel表格对应为第16列
            self.opr_xls.save_to_excel_by_cell(i, 15, plan_code_value)

            # 写入Excel文件 更新生效日期  excel表格对应为第16列
            self.opr_xls.save_to_excel_by_cell(i, 16, self.validateTime)

            # 写入Excel文件 更新生效止期  excel表格对应为第17列
            self.opr_xls.save_to_excel_by_cell(i, 17, self.validateEndTime)

            # # 证件类型为‘护照’
            # insuranceCertNo = 'TX' + get_reg_no.current_time_str() + (str(i) if i >= 10 else '0' + str(i))

            # 证件类型为‘身份证’ , 生成身份证号和出生日期
            insuranceCertNo, birthday, sex = get_reg_no.get_cert_no()

            # 写入Excel文件 被保人证件号  excel表格对应为第7列
            self.opr_xls.save_to_excel_by_cell(i, 7, insuranceCertNo)

            # 写入Excel文件 出生日期  excel表格对应为第11列
            self.opr_xls.save_to_excel_by_cell(i, 8, birthday)

            # 写入Excel文件 性别  excel表格对应为第12列
            self.opr_xls.save_to_excel_by_cell(i, 9, sex)

        self.opr_xls.resave_excel('最终上传数据文件')  # 文件重开另存为'最终上传数据文件'

        # 上传被保人清单
        files_open = open(self.opr_xls.file_path + '最终上传数据文件.xlsx', 'rb')
        files = {'files': files_open}
        insured_import_url = self.api_url_datas['excelImport'].format(self.host_url)
        request_data = {
            "endorsementNo": self.cs_no,
            "isFullImport": False,
            "templateId": 200001
        }
        save_response = self.API.send_request(insured_import_url, 'post_file', request_data, self.headers, files)
        files_open.close()
        if 'result' not in save_response.keys() or save_response['code'] != '0':
            print('上传被保人清单失败')
            exit()
        else:
            # 上传后删除生成的最终文件
            self.opr_xls.delete_excel_file(self.opr_xls.new_file)

    # 批改-提交
    def test_08_submit_review(self):
        time.sleep(20)
        # 获取公安接口校验不通过数据
        validation_url = self.api_url_datas['querySecurityNotPassed'].format(self.host_url, self.cs_no)
        validation_respond = self.API.send_request(validation_url, 'get', None, self.headers)
        if validation_respond['result']['resultList'] is not None:
            validation_list = validation_respond['result']['resultList']
            # 逐个上传证件附件
            # 当前路径
            current_path = os.path.abspath(os.path.dirname(__file__))
            # 上一级路径（父级路径）
            parent_path = os.path.dirname(current_path)
            file_path = parent_path + "\\upload_file\\" + '证件号不合法.jpg'
            files_open = open(file_path, 'rb')
            files = {'files': files_open}
            for validation_name in validation_list:
                request_data = {
                    "objectId": validation_name['objectId'],
                    "attachmentType": validation_name['attachmentType'],
                    'endorsementNo': self.cs_no
                }
                upload_url = self.api_url_datas['addAttachment'].format(self.host_url)
                self.API.send_request(upload_url, 'post_file', request_data, self.headers, files)
        time.sleep(5)
        submit_review_url = self.api_url_datas['complete'].format(self.host_url)
        request_data = {"endorsementNo": self.cs_no}
        result = self.API.send_request(submit_review_url, 'post_json', request_data, self.headers)
        if 'code' in result.keys() and result['code'] != '0':
            print('提交失败，请检查！')
            exit()


    # 批改-复核
    def test_09_finish_data_review(self):
        # 查询任务
        url = self.api_url_datas['sharedPoolSearchlock'].format(self.host_url)
        request_data = {
            "pageSize": 10,
            "currentPage": 1,
            "searchType": "1",
            "endorsementStatus": "3",
            "endorsementNo": self.cs_no,
            "taskDefKey": "TSK_REVIEW"
        }
        response = self.API.send_request(url, 'post_json', request_data, self.view_headers)
        if 'message' in response.keys() and response['message'] == '没有查询到数据':
            request_data = {
                "searchType": 0,
                "currentPage": 1,
                "pageSize": 10,
                "endorsementStatus": "3",
                "endorsementNo": self.cs_no,
                "taskDefKey": "TSK_REVIEW"
            }
            response = self.API.send_request(url, 'post_json', request_data, self.view_headers)
            if 'message' in response.keys() and response['message'] == '没有查询到数据': exit()

        # 复核 领取任务
        lock_viwe_url = self.api_url_datas['lockClaimTask'].format(self.host_url, self.cs_no)
        self.API.send_request(lock_viwe_url, 'get', None, self.view_headers)

        # 复核通过
        finish_url = self.api_url_datas['saveOrUpdateEndorsementTask'].format(self.host_url)
        request_data = {
            "reviewSolution": 1,
            "changeId": self.changeId,
            "endorsementNo": self.cs_no
        }
        res = self.API.send_request(finish_url, 'post_json', request_data, self.view_headers)

    # 新契约-人工核保
    def test_10_save_group_decision(self):
        if self.endorsementType in ["14"]:
            print('批改项不需要核保，请查看是否已生效')
            exit()
        # 查询人工核保列表
        get_task_url = self.api_url_datas['getPubTask'].format(self.host_url)
        request_data = {
            "uwLevel": 1,
            "currentPage": 1,
            "pageSize": 10,
            "uwPolicyCategory": 1,
            "objectNo": self.cs_no
        }
        res = self.API.send_request(get_task_url, 'post', request_data, self.view_headers)
        if len(res['result']['resultList']) == 0:
            get_mytask_url = self.api_url_datas['getMyTask'].format(self.host_url)
            request_data = {
                "uwLevel": 1,
                "currentPage": 1,
                "pageSize": 10,
                "uwPolicyCategory": 1,
                "objectNo": self.cs_no
            }
            res = self.API.send_request(get_mytask_url, 'post', request_data, self.view_headers)
        i = 0
        while len(res['result']['resultList']) == 0:
            # 查询结果为空 重新再请求一次
            print('核保查询列表为空，等20s后重新查询')
            time.sleep(20)
            res = self.API.send_request(get_task_url, 'post', request_data, self.view_headers)
            if i == 5:
                print('核保查询列表为空，请到运营系统检查')
                exit()
            else:
                i += 1

        tast_locked_id = res['result']['resultList'][0]['id']

        # 领取任务
        locked_tast_url = self.api_url_datas['uwdealLocked'].format(self.host_url, tast_locked_id)
        res = self.API.send_request(locked_tast_url, 'post_json', {'systemSource': None}, self.view_headers)

        # 查询整单信息
        get_init_url = self.api_url_datas['initPage'].format(self.host_url, tast_locked_id)
        res = self.API.send_request(get_init_url, 'get', None, self.view_headers)
        haUwId = res['result']['uwPolicyInfo']['id']
        appGroupId = res['result']['csPolicyInfo']['haGroupPolicyId']

        # 核保通过
        pass_url = self.api_url_datas['saveGroupDecision'].format(self.host_url, haUwId, self.cs_no, appGroupId)
        res = self.API.send_request(pass_url, 'get', None, self.view_headers)

    def test_show_data(self):
        time.sleep(15)
        policy_url = self.api_url_datas['underWriteQueryPolicy'].format(self.host_url, self.haAppGroupNo)
        res = self.API.send_request(policy_url, 'get', None, self.view_headers)
        self.haGroupPolicyNo = res['result']['data'][0]['haGroupPolicyNo']
        time_i = 0
        while self.haGroupPolicyNo is None:
            # 查询结果为空 重新再请求一次
            print('保单号未查询到，等20s后重新查询')
            time.sleep(15)
            res = self.API.send_request(policy_url, 'get', None, self.view_headers)
            self.haGroupPolicyNo = res['result']['data'][0]['haGroupPolicyNo']
            if time_i == 5:
                break
            else:
                time_i += 1
        print('投保单号是: {}'.format(self.haAppGroupNo))
        print('团单号是: {}'.format(self.haGroupPolicyNo))
        print('haAppGroupId是: {}'.format(self.apply_id))

    # 保费实收
    def test_11_premiums_paid(self):
        if self.haGroupPolicyNo is not None:
            time.sleep(20)
            if self.host == 'test':
                paid_host = 'http://za-newbee-ops.test.za.biz'
            elif self.host == 'uat':
                paid_host = 'http://newbee-uat.zhonganonline.com'
            paid_host_url = paid_host + '/api/newbee/bill/list/single'
            request_data = {
                "departmentId": 21,
                "feeCategory": "PREMIUM",
                "paymentDirection": "RECEIVABLES",
                "cusUserId": None,
                "dueDate": None,
                "dueDateEnd": None,
                "paymentDate": None,
                "paymentDateEnd": None,
                "period": None,
                "periodEnd": None,
                "topPolicyNo": None,
                "businessNo": self.haGroupPolicyNo,
                "settlementIdExist": False,
                "currentPage": 1,
                "pageSize": 10
            }
            paid_headers = {
                "Cookie": "_za_sso_session_=fjZk2taKZSqN3anFnSR4Y6ef9cYmd1VCDlemUZe9xqiZ0Th0BLIjTYbv6fkRbxuuP"
                          "/Qncc4TnkZgRUQly+0KyKvVf9fS4DGPCq8Rwr4oHKyI9ngRa/wfKjG0Sw2mficva6xdvsMJ2/WYpiTAaL8K1uqG"
                          "+lU9rVFz2cLYqZDziOlsFffK934aZPI63xoBURsUciABQ6yPq7YW4jiiz3lqDDNRv2b3996eZ0v8beg37nNcSJs9IvUVBI8qqWaWlfREhkhgMptZ5Bd0GDj8A+W32z7vT0yQNhsRMIHcT/3B/1/VUwIY/VXCLN0lj957UAllb00KAZ1UA02g4u9/m5r6pzdJrZuDGBvLEc5HlfDrb2hCKXOwwtkyeZ74swJFI6vQ2TwBLA3Iq3FL4jnabmZtC9lpbG5P2uwLaT/+lkOO0scan9tiiA7paMxQzf/NoFj7 "
            }
            res = self.API.send_request(paid_host_url, 'post_json', request_data, paid_headers)
            if 'success' in res.keys() and res['success'] is True and res['errMsg'] == '成功':
                resultList = res['value']['resultList']
                billId = resultList[0]['billId']
                relatedPolicyId = resultList[0]['businessId']
                url = paid_host + '/api/newbee/bill/common/accountNo?accountType=THIRD_PARTY_PAYMENT'
                res_get = self.API.send_request(url, 'get', None, paid_headers)
                zaAccountNo = res_get[0]['value']
                request_data = {
                    "businessList": [{
                        "id": billId,
                        "relatedPolicyId": relatedPolicyId
                    }],
                    "paymentType": "RECEIVABLES",
                    "confirmType": "1",
                    "recordList": [{
                        "zaAccountNo": zaAccountNo,
                        "_index": 0,
                        "_rowKey": 2
                    }]
                }
                confirm_url = paid_host + '/api/newbee/settlement/Confirm/single'
                res = self.API.send_request(confirm_url, 'post_json', request_data, paid_headers)
                if 'success' in res.keys() and res['success'] is True:
                    print('保费实收成功')
            else:
                print('未查到相关数据')
                exit()


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])

    test = groupCorrect()
    test.run()

