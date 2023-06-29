from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from util.opr_excel import OperationExcel
from conf.header_conf import headers, headers_ruixiang, headers_sunchao
from util.opr_json import OperationJson
from format_util import get_reg_no
import json
import random
import string
import os, time


# 雇主责任险出单
class employerInsurance:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("employer_api_url")
        self.product_code_list = ReadYaml().read_yaml("employer_product_code")
        self.host_url = self.api_url_datas['uat_url']  # 环境地址
        self.headers = headers  # 录入人
        self.view_headers = headers_ruixiang  # 复核人
        self.issue_headers = headers_sunchao  # 核保人
        self.strNo = get_reg_no.get_date_str()
        self.opr_xls = OperationExcel(file_name='雇主-正常标准人员清单')  # 上传被保人清单模板
        self.planName_list = []
        self.apply_id = None
        self.applyNo = None
        self.channle = {}
        # self.planCode = None
        self.apply_id = 81520015
        self.applyNo = ''
        # self.planName_list = ['雇主计划0-20220221152755', '雇主计划1-20220221152756', '雇主计划2']
        self.orgName = self.strNo + "雇主投保单位"  # 投保单位名称
        # self.orgName = "测试环境出单"
        self.channelCategoryCode = 'B'  # A 直接业务  B 中介业务

    def run(self):
        self.test_01_create_policy()  # 生成投保单
        self.test_02_save_basic_info()  # 保存第一步（投保单基本信息）
        self.test_03_save_customer()  # 保存第二步（投保单位）
        self.test_04_product_selection()  # 保存第三步（产品选择）
        self.test_05_modify_group_product()  # 新契约-总单险种定义
        self.test_06_add_group_plan()  # 新契约-新建计划
        self.test_07_insured_import()  # 新契约-被保人清单导入
        # self.test_08_submit_review()  # 新契约-提交
        # self.test_09_finish_data_review()  # 新契约-复核
        # self.test_10_save_group_decision()  # 新契约-人工核保

    # 生成投保单
    def test_01_create_policy(self):
        # time.sleep(3)
        url = self.api_url_datas['registerNewEmployer'].format(self.host_url)
        # 雇主新契约-生成id
        register_response = self.API.send_request(url, 'post', None, headers)
        self.apply_id = register_response['result']
        # print(register_response)

        # 根据id查询投保单号
        findBasicPolicyInfo_url = self.api_url_datas['findBasicPolicyInfo'].format(self.host_url, self.apply_id)
        policy_info_response = self.API.send_request(findBasicPolicyInfo_url, 'get', None, headers)
        self.applyNo = policy_info_response['result']['applyNo']
        # print(self.haAppGroupNo)

    # 保存第一步（投保单基本信息）
    def test_02_save_basic_info(self):
        # 上传附件
        # 当前路径
        current_path = os.path.abspath(os.path.dirname(__file__))
        # 上一级路径（父级路径）
        parent_path = os.path.dirname(current_path)
        file_path = parent_path + "\\upload_file\\" + '雇主-投保单位基本信息-附件上传.jpg'
        files_open = open(file_path, 'rb')
        files = {'files': files_open}
        request_data = {
            "objectId": self.apply_id,
            "attachmentType": 1,
            'objectType': 1,
            'attachmentName': '雇主-投保单位基本信息-附件上传.jpg',
            "remark": '投保单基本信息附件描述'
        }
        upload_url = self.api_url_datas['employerUpload'].format(self.host_url)
        self.API.send_request(upload_url, 'post_file', request_data, self.headers, files)

        # time.sleep(3)
        url = self.api_url_datas['saveEmployerPolicy'].format(self.host_url)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='employer_basic_info')

        # 更新生成id 并根据需求更改配置选项
        request_data['applyTime'] = get_reg_no.get_yesterday_date()  # 投保日期
        request_data['effectiveTime'] = get_reg_no.get_today_date()  # 保险起期
        request_data['expiryTime'] = get_reg_no.get_year_later_date()  # 保险止期

        # request_data['applyTime'] = '2021-05-01'  # 投保日期
        # request_data['effectiveTime'] = '2021-05-01'  # 保险起期
        # request_data['expiryTime'] = '2022-04-30'  # 保险止期

        request_data['id'] = self.apply_id  # 更新json中的id
        request_data['applyNo'] = self.applyNo  # 更新json中的applyNo
        request_data['channel']['policyId'] = str(self.apply_id)  # 更新json中的channel下的policyId
        request_data['agreement']['policyId'] = str(self.apply_id)  # 更新json中的agreement下的policyId

        # 直接/中介业务
        if self.channelCategoryCode == 'A':
            request_data['channel']['secondPartnerId'] = '30045004'
            request_data['channel']['secondPartnerFullName'] = '翰威特'
        else:
            request_data['channel']['secondPartnerId'] = '10002539359'
            request_data['channel']['secondPartnerFullName'] = '美华保险销售有限公司'

        # 新契约-保存第一步（投保单基本信息）
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)

        if 'error' in save_response.keys() or ('success' in save_response.keys() and save_response['success'] != True):
            # # 二级合作方失效 找可用的
            # findSalesChannel_url = self.api_url_datas['findSalesChannel'].format(self.host_url)
            # SalesChannel_response = self.API.send_request(findSalesChannel_url, 'get', None, headers)
            # SalesChannelList = SalesChannel_response['result']
            # for channel in SalesChannelList:
            #     request_data['channel']['secondPartnerId'] = channel['resCode']
            #     request_data['channel']['secondPartnerFullName'] = channel['resName']
            #     print(channel['resName'])
            #     save_response2 = self.API.send_request(url, 'post_json', request_data, self.headers)
            #     if 'success' in save_response2.keys() and save_response2['success'] == True:
            #         break

            # 已保存过数据，重新请求获取入参
            findBasicPolicyInfo_url = self.api_url_datas['findBasicPolicyInfo'].format(self.host_url, self.apply_id)
            policy_info_response = self.API.send_request(findBasicPolicyInfo_url, 'get', None, headers)
            request_data['channel'] = policy_info_response['result']['channel']
            save_response = self.API.send_request(url, 'post_json', request_data, self.headers)

    # 保存第二步（投被保险人）
    def test_03_save_customer(self):
        url = self.api_url_datas['saveCustomer'].format(self.host_url, self.apply_id)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='employer_customer_new')

        # 更新生成id 并根据需求更改配置选项
        request_data['policyHolder']['policyId'] = self.apply_id  # 更新json中的policyId

        request_data['policyHolder']['orgName'] = self.orgName

        # request_data['policyHolder']['legalRepresentative'] = "法人" + self.strNo  # 单位法人代表
        # request_data['policyHolder']['legalCertType'] = "P"  # 法人证件类型：I 身份证；P 护照；
        # request_data['policyHolder']['legalCertNo'] = get_reg_no.create_legalCertNo()  # 法人证件号码

        request_data['policyHolder']['uniSocialCreCod'] = get_reg_no.create_uniSocialCreCode()  # 统一社会信用代码
        # request_data['policyHolder']['orgCode'] = get_reg_no.create_employer_orgCode()  # 组织机构代码
        # request_data['policyHolder']['taxRegNo'] = get_reg_no.create_taxRegNum()  # 税务登记号
        # request_data['policyHolder']['licencesNo'] = get_reg_no.create_icRegNo()  # 营业执照
        # request_data['policyHolder']['staffNum'] = 33  # 单位总人数
        request_data['insuredPerson'] = request_data['policyHolder']  # 被保单位信息与投保单位一致
        request_data['insuredPerson']['isSameAsPolicyHolder'] = "Y"

        request_data['paymentPerson']['objectId'] = self.apply_id  # 更新json中的objectId
        request_data['paymentPerson']['name'] = request_data['policyHolder']['orgName']
        request_data['paymentPerson']['certNumber'] = request_data['policyHolder']['uniSocialCreCod']

        request_data['invoice']['objectId'] = self.apply_id  # 更新json中的objectId

        # 保存第二步（投保单位）
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        if 'success' in save_response.keys() and save_response['success'] != True:
            print('投保单基本信息保存失败')
            exit()

    # 保存第三步（产品选择）
    def test_04_product_selection(self):
        url = self.api_url_datas['productCreate'].format(self.host_url)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='employer_choose_product')

        # 更新生成id 并根据需求更改配置选项
        request_data['policyId'] = self.apply_id  # 更新json中的id

        # 根据json中配置的产品版型code 重新生成时间的product code
        selectProducts = []
        for product_code in request_data['selectProducts']:
            selectProducts.append(str(self.product_code_list[product_code]))

        request_data['selectProducts'] = selectProducts

        # print(request_data)
        # 保存第三步（产品选择）
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        if 'success' in save_response.keys() and save_response['success'] != True:
            print('产品选择保存失败')
            exit()

    # 新契约-总单险种定义
    def test_05_modify_group_product(self):
        url = self.api_url_datas['ProductQueryTmpl'].format(self.host_url, self.apply_id)
        # 查询所选险种的列表信息
        result = self.API.send_request(url, 'get', None, self.headers)
        employerProductViewList = result['result']

        modify_employer_product_url = self.api_url_datas['modifyEmployerProduct'].format(self.host_url)
        for product_viwe in employerProductViewList:
            find_product_url = self.api_url_datas['findProductDetailsById'].format(self.host_url, self.apply_id,
                                                                                   product_viwe['id'],
                                                                                   product_viwe['wjsProductId'])

            # 根据ProductId 查询详情
            product_result = self.API.send_request(find_product_url, 'get', None, self.headers)
            # print(product_result)
            # exit()
            product_result = product_result['result']
            product_result = json.dumps(product_result)
            product_result = product_result.replace('null', '\"\"')
            product_result = json.loads(product_result)

            product_policyLiabilities = product_result['liabilitys']
            product_policyLiabilities[0]['isChecked'] = 'Y'  # 默认选择第一个责任
            if len(product_policyLiabilities[0]['factors']) > 0:
                factors = []
                for factor in product_policyLiabilities[0]['factors']:
                    if 'relativityValue' in factor:
                        factor['relativityValue'] = 8000
                        factors.append(factor)
                product_policyLiabilities[0]['factors'] = factors
                if product_policyLiabilities[0]['wjsLiabilityName'] == '法律费用':
                    product_policyLiabilities[1]['isChecked'] = 'Y'  # 主险要选择非法律费用的责任
            # 拼装接口入参
            request_data = {
                "countWay": "2",
                "factors": product_result['factors'],
                "liabilitys": product_policyLiabilities,
                "id": product_result['id'],
                "policyId": product_result['policyId'],
                "wjsProductId": product_result['wjsProductId'],
                "wjsProductCode": product_result['wjsProductCode'],
                "wjsProductName": product_result['wjsProductName'],
                "amountUnitType": product_result['amountUnitType'],
                "riskType": product_result['riskType'],
                "paymentFrequency": product_result['paymentFrequency'],
                "paymentFrequencyRate": product_result['paymentFrequencyRate'],
                "planCode": 7263,
                "channel": self.channle,
                "adCommissionRate": 0.01,  # 宣传服务推广费比例(%)
                "commissionRate": 0  # 佣金率(%)
            }
            # print(request_data)
            # 发起选择责任条款请求
            save_response = self.API.send_request(modify_employer_product_url, 'post_json', request_data, self.headers)
            if 'success' in save_response.keys() and save_response['success'] != True:
                print('总单险种定义保存失败')
                exit()

    # 新契约-新建计划
    def test_06_add_group_plan(self):
        # 创建多个计划
        for i in range(2):
            random_str = random.sample(string.ascii_letters, 1)
            # 创建计划
            request_data = {
                'policyId': self.apply_id
            }
            add_plan_url = self.api_url_datas['newEmployerPlan'].format(self.host_url)
            add_response = self.API.send_request(add_plan_url, 'post_json', request_data, self.headers)
            plan_info = add_response['result']

            # 填写计划内容
            # 处理险种责任定义
            planProducts = []
            total_premium = premium = 0

            # 险种层级
            for product in plan_info['planProducts']:
                # 责任层级
                liabilitys = []
                liabilitys_premium = 0
                for liability in product['liabilitys']:
                    liability['isChecked'] = "Y"
                    premium += 50
                    liability['premium'] = str(premium)
                    liabilitys_premium += premium  # 合计险种下的每个责任保费为险种保费
                    factors = []
                    for factor in liability['factors']:
                        if '赔偿限额' in factor['relativityName']:
                            factor['relativityValue'] = '8000'
                        elif '赔付金额' in factor['relativityName']:
                            factor['relativityValue'] = '600'
                        elif '天数' in factor['relativityName']:
                            factor['relativityValue'] = '50'
                        factors.append(factor)
                    liability['factors'] = factors

                    liabilitys.append(liability)
                product['liabilitys'] = liabilitys
                product['isChecked'] = "Y"
                product['premium'] = liabilitys_premium
                total_premium += liabilitys_premium  # 合计每个险种保费为总保费
                product_factors = []
                for product_factor in product['factors']:
                    if '赔偿限额' in product_factor['relativityName']:
                        product_factor['relativityValue'] = '8000'
                    elif '赔付金额' in product_factor['relativityName']:
                        product_factor['relativityValue'] = '600'
                    elif '天数' in product_factor['relativityName']:
                        product_factor['relativityValue'] = '50'
                    product_factors.append(product_factor)
                product['factors'] = product_factors

                planProducts.append(product)

            plan_info['planProducts'] = planProducts
            plan_info['planFactorsMap'] = {
                "HLOccupationCategory": "7",  # 计划职业类别
                "HLAgeRange": "[1,99]"  # 雇员年龄范围
            }

            plan_info['policyId'] = self.apply_id
            plan_info['planName'] = "雇主计划" + str(i) + '-' + get_reg_no.current_time_str()  # 计划名称
            self.planName_list.append(plan_info['planName'])
            plan_info['premium'] = total_premium

            # 保存创建计划
            add_plan_url = self.api_url_datas['saveEmployerPlan'].format(self.host_url)
            save_response = self.API.send_request(add_plan_url, 'post_json', plan_info, self.headers)
            if 'success' in save_response.keys() and save_response['success'] != True:
                print('创建计划保存失败')
                exit()

    # 新契约-被保人清单导入
    def test_07_insured_import(self):

        # 获取Excel文件最大的行数
        max_row = self.opr_xls.max_row
        code_index = 0
        # 更新保险计划code  数据是从第4行开始
        for i in range(4, max_row + 1):
            print("雇员姓名: {}".format(self.opr_xls.get_cell_value(i, 1)))  # 打印被保人信息

            # 循环计划列表，确保每个计划都有一个被保人，超出则重新排
            if code_index == len(self.planName_list):
                code_index = 0
            plan_code_value = self.planName_list[code_index]
            code_index += 1

            customerCertNo = 'GY' + str(i) + get_reg_no.current_time_str()
            # 写入Excel文件 雇员证件号  excel表格对应为第3列
            self.opr_xls.save_to_excel_by_cell(i, 3, customerCertNo)

            # 写入Excel文件 更新保险计划信息  excel表格对应为第6列
            self.opr_xls.save_to_excel_by_cell(i, 6, plan_code_value)

        self.opr_xls.resave_excel('雇主最终上传数据文件')

        # 上传被保人清单
        files_open = open(self.opr_xls.new_file, 'rb')
        files = {'files': files_open}
        employee_upload_url = self.api_url_datas['employeeUpload'].format(self.host_url, self.apply_id)
        request_data = {
            "policyId": self.apply_id,
            "isOverride": False
        }
        save_response = self.API.send_request(employee_upload_url, 'post_file', request_data, self.headers, files)
        files_open.close()
        if 'success' in save_response.keys() and save_response['success'] != True:
            print('上传被保人清单失败')
            exit()
        else:
            # 上传后删除生成的最终文件
            self.opr_xls.delete_excel_file(self.opr_xls.new_file)

    # 新契约-提交
    def test_08_submit_review(self):
        submit_review_url = self.api_url_datas['policyConfirm'].format(self.host_url, self.apply_id)
        self.API.send_request(submit_review_url, 'post', {}, self.headers)

    # 新契约-复核
    def test_09_finish_data_review(self):
        # 共享池领取复核任务
        requst_data = {
            "policyId": self.apply_id,
            "operationAction": 103
        }
        lock_viwe_url = self.api_url_datas['lockViewGroup'].format(self.host_url)
        self.API.send_request(lock_viwe_url, 'post_json', requst_data, self.view_headers)

        # 获取noteId
        request_data = {
            "id": "",
            "objectId": self.apply_id,
            "objectType": 1,
            "noteType": 1,
            "note": "",
            "action": 103
        }
        save_url = self.api_url_datas['noteSave'].format(self.host_url, self.apply_id)
        res = self.API.send_request(save_url, 'post_json', request_data, self.view_headers)
        noteId = res['result']

        # 复核通过
        pass_url = self.api_url_datas['passReviewPolicy'].format(self.host_url)
        request_data = {
            "noteId": noteId,
            "policyId": self.apply_id,
            "noteType": 1,
            "note": "",
            "action": 104
        }
        save_response = self.API.send_request(pass_url, 'post_json', request_data, self.view_headers)
        if 'success' in save_response.keys() and save_response['success'] != True:
            print('复核失败')
            exit()

    # 新契约-人工核保
    def test_10_save_group_decision(self):
        time.sleep(20)
        # 共享池领取核保任务
        requst_data = {
            "policyId": self.apply_id,
            "operationAction": 107
        }
        lock_viwe_url = self.api_url_datas['lockViewGroup'].format(self.host_url)
        self.API.send_request(lock_viwe_url, 'post_json', requst_data, self.issue_headers)

        # 整单核保完成
        save_decision_url = self.api_url_datas['underwritingIssue'].format(self.host_url, self.apply_id)
        request_data = {
            "policyId": self.apply_id,
            "comments": ""
        }
        res = self.API.send_request(save_decision_url, 'post_json', request_data, self.issue_headers)
        if 'success' in res.keys() and res['success'] == True:
            print('核保通过')
            print('投保单号为：'+self.applyNo)
        elif res['message'] == '保单保费跟汇总险种保费不一致':
            request_data = {
                "policyId": self.apply_id,
                "comments": "保单保费跟汇总险种保费不一致,退回重新提交"
            }
            decision_url = self.api_url_datas['underwritingBack'].format(self.host_url, self.apply_id)
            res = self.API.send_request(decision_url, 'post_json', request_data, self.issue_headers)
            self.test_08_submit_review()
            self.test_09_finish_data_review()
            self.test_10_save_group_decision()


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])

    test = employerInsurance()
    test.run()
