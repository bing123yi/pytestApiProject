from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from util.opr_excel import OperationExcel
from conf.header_conf import headers, headers_ruixiang, headers_huangmian
from util.opr_json import OperationJson
from format_util import get_reg_no, plan_group_products
import json, os, time, random, string


# 意健险-新契约-投保单录入
# 团险线下出单
class groupInsurance:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("group_insurance")
        self.product_code_list = ReadYaml().read_yaml("group_product_code")

        # 选择环境
        self.host = 'test'  # 选择环境

        self.headers = headers  # 录入人
        self.view_headers = headers_ruixiang  # 复核人

        self.applyTime = get_reg_no.get_yesterday_date()  # 投保日期
        self.validateTime = get_reg_no.get_today_date()  # 保险起期
        self.applyTime = '2021-12-31'  # 投保日期
        self.validateTime = '2022-01-01'  # 保险起期

        self.haAppGroupNo = ''  # 投保单号

        self.isMouthPay = False  # 是否倍月薪  False True

        self.strNo = get_reg_no.get_date_str()
        random_str = random.sample(string.ascii_letters, 1)
        self.orgName = "投保" + self.strNo + random_str[0] + "单位"  # 投保单位名称
        # self.orgName = "腾佳保单2022年员工家属承保确认函"

        self.host_url = self.api_url_datas[self.host + '_url']
        self.healthDeclarationNo = "GG0001"  # 健康告知模板号
        self.opr_xls = OperationExcel(file_name='团险-正常标准团单被保人清单')  # 上传被保人清单模板
        self.channelType = 'A'  # 销售渠道 A 直接业务  B 中介业务
        self.bdSalesmanCode = '010003'  # 销售经理code
        self.plancode_list = []
        self.apply_id = None
        self.haGroupPolicyNo = None

    def run(self):
        self.get_apply_Id()
        self.test_01_create_policy()  # 生成投保单
        self.test_02_save_basic_info()  # 保存第一步（投保单基本信息）
        self.test_03_save_group_holder()  # 保存第二步（投保单位）
        self.test_04_product_selection()  # 保存第三步（产品选择）
        self.test_05_modify_group_product()  # 新契约-总单险种定义
        self.test_06_add_group_plan()  # 新契约-新建计划
        self.test_07_insured_import()  # 新契约-被保人清单导入
        self.test_08_submit_review()  # 新契约-提交
        self.test_09_finish_data_review()  # 新契约-复核
        self.test_10_save_group_decision()  # 新契约-人工核保
        self.test_show_data()  # 打印投保单 计划等id信息
        self.test_11_premiums_paid()  # 保费实收

    #
    def get_apply_Id(self):
        if not self.apply_id and self.haAppGroupNo:
            url = self.api_url_datas['getApplyId'].format(self.host_url, self.haAppGroupNo)
            response = self.API.send_request(url, 'get', None, self.headers)
            if 'success' in response.keys() and response['success'] == True:
                if len(response['result']['data']) > 0:
                    self.apply_id = response['result']['data'][0]['id']
                    self.validateTime = response['result']['data'][0]['validateTime'][0:10]
                    print(self.apply_id)
                else:
                    print('查询不到投保单号，请检查')
                    exit()
            else:
                print('投保单号查询错误！！！')
                exit()
            # print(register_response)

    # 生成投保单
    def test_01_create_policy(self):
        # time.sleep(3)
        url = self.api_url_datas['registerNewProposal'].format(self.host_url)
        # print(url)
        request_data = {
            "groupPolicyType": 1
        }
        # 新契约-生成id
        register_response = self.API.send_request(url, 'post', request_data, self.headers)
        self.apply_id = register_response['result']
        # print(register_response)

        # 锁定投保单
        lock_url = self.api_url_datas['lockApplyGroup'].format(self.host_url, self.apply_id)
        lock_response = self.API.send_request(lock_url, 'get', None, self.headers)
        if lock_response['result'] != True or lock_response['success'] != True:
            print('锁定投保单失败')
            exit()

        # 根据id查询投保单号
        findGroupPolicyInfo_url = self.api_url_datas['findGroupPolicyInfo'].format(self.host_url, self.apply_id)
        policy_info_response = self.API.send_request(findGroupPolicyInfo_url, 'get', None, self.headers)
        self.haAppGroupNo = policy_info_response['result']['haAppGroupNo']

        # print(self.haAppGroupNo)
        # print(type(policy_info_response))

    # 保存第一步（投保单基本信息）
    def test_02_save_basic_info(self):
        # time.sleep(3)
        url = self.api_url_datas['saveGroupPolicy'].format(self.host_url)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='group_basic_info')

        if self.channelType == 'A':
            secondPartnerCode = 'A030190'  # 直接业务 二级合作方 'A030190' 众安官网
        else:
            secondPartnerCode = 'B02OL358'  # 中介业务 二级合作方   'B02OL358' 美华保险销售有限公司
        # 更新生成id 并根据需求更改配置选项
        request_data['applyTime'] = self.applyTime  # 投保日期
        request_data['validateTime'] = self.validateTime  # 保险起期
        request_data['channelType'] = self.channelType  # 销售渠道
        request_data['secondPartnerCode'] = secondPartnerCode  # 二级合作方code 'A030190' 众安官网  'B02OL358' 美华保险销售有限公司
        request_data['bdSalesmanName'] = '傅歌'  # 销售经理姓名
        request_data['bdSalesmanCode'] = self.bdSalesmanCode  # 销售经理code

        request_data['id'] = self.apply_id  # 更新json中的id
        request_data['haAppGroupId'] = self.apply_id  # 更新json中的haAppGroupId
        request_data['haAppGroupNo'] = self.haAppGroupNo  # 更新json中的haAppGroupNo
        request_data['isPeriodicSettlement'] = True  # 是否定期结算
        request_data['isEffectBeforePayment'] = False  # 是否见费出单
        request_data['isHolderSendMsg'] = False  # 是否发送投保单位授权办理业务人短信
        request_data['isHolderSendMail'] = False  # 是否发送投保单位授权办理业务人邮件
        request_data['isInsuredSendMsg'] = False  # 是否发送被保险人承保短信
        request_data['isInsuredSendMail'] = False  # 是否发送被保人承保邮件
        request_data['isClaimSendMsg'] = False  # 是否发送被保人承包信息
        request_data['isClaimSendMail'] = False  # 是否发送被保人承包邮件
        request_data['retroactivePeriod'] = 100  # 保险追诉期

        # print(request_data)

        # 新契约-保存第一步（投保单基本信息）
        save_response = self.API.send_request(url, 'post', request_data, self.headers)
        if save_response['result'] != True or save_response['success'] != True:
            print('投保单基本信息保存失败')
            exit()

    # 保存第二步（投保单位）
    def test_03_save_group_holder(self):
        url = self.api_url_datas['saveGroupHolder'].format(self.host_url, self.apply_id)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='group_holder')

        # 更新生成id 并根据需求更改配置选项
        request_data['id'] = request_data['haAppGroupId'] = self.apply_id  # 更新json中的id haAppGroupId
        request_data['haAppGroupNo'] = self.haAppGroupNo  # 更新json中的haAppGroupNo

        request_data['orgName'] = self.orgName
        if self.isMouthPay is True:
            request_data['orgName'] += '倍月薪'
        request_data['invoiceTitle'] = request_data['orgName']  # 发票抬头

        request_data['legalRepresentative'] = "法人" + self.strNo  # 单位法人代表
        # request_data['legalCertType'] = "P"  # 法人证件类型：I 身份证；P 护照；
        # request_data['legalCertNo'] = get_reg_no.create_legalCertNo()  # 法人证件号码

        request_data['legalCertType'] = "I"  # 法人证件类型：I 身份证；P 护照；
        request_data['legalCertNo'] = get_reg_no.get_cert_no()[0]  # 法人证件号码

        request_data['uniSocialCreCode'] = get_reg_no.create_uniSocialCreCode()  # 统一社会信用代码
        # request_data['uniSocialCreCode'] = '9144030071526726XG'  # 统一社会信用代码
        request_data['orgCode'] = get_reg_no.create_orgCode()  # 组织机构代码
        request_data['taxRegNum'] = get_reg_no.create_taxRegNum()  # 税务登记号
        request_data['icRegNo'] = get_reg_no.create_icRegNo()  # 营业执照

        request_data['taxpayerIdtfNumber'] = get_reg_no.create_taxpayerIdtfNumber()  # 纳税人识别号
        request_data['contactName'] = "业务人" + self.strNo  # 授权办理业务人
        request_data['staffNum'] = 33  # 单位总人数

        # print(request_data)
        # 保存第二步（投保单位）
        save_response = self.API.send_request(url, 'post', request_data, self.headers)
        if save_response['result'] != True or save_response['success'] != True:
            print('投保单基本信息保存失败')
            exit()

    # 保存第三步（产品选择）
    def test_04_product_selection(self):
        url = self.api_url_datas['modificProductinfo'].format(self.host_url)
        # 获取请求json入参数据
        request_data = self.OprJson.read_data(file_name='group_choose_product')

        # 更新生成id 并根据需求更改配置选项
        request_data['appGroupId'] = self.apply_id  # 更新json中的id

        # 根据json中配置的产品版型code 重新生成时间的product code
        productid_list = request_data['productid'].split(",")
        productid = ",".join(str(self.product_code_list[product_code]) for product_code in productid_list)
        request_data['productid'] = productid

        # print(request_data)
        # 保存第三步（产品选择）
        save_response = self.API.send_request(url, 'post', request_data, self.headers)
        if save_response['success'] != True:
            print('产品选择保存失败')
            exit()

    # 新契约-总单险种定义
    def test_05_modify_group_product(self):
        url = self.api_url_datas['listAppGroupProductsByAppGroup'].format(self.host_url, self.apply_id)
        # 查询所选险种的列表信息
        result = self.API.send_request(url, 'get', None, self.headers)
        groupProductViewList = result['result']['groupProductViewList']

        modify_group_product_url = self.api_url_datas['modifyGroupProduct'].format(self.host_url)
        for product_viwe in groupProductViewList:
            find_product_url = self.api_url_datas['findAppGroupProductById'].format(self.host_url, product_viwe['id'])
            # 根据ProductId 查询详情
            product_result = self.API.send_request(find_product_url, 'get', None, self.headers)
            product_result = product_result['result']
            product_result = json.dumps(product_result)
            product_result = product_result.replace('null', '\"\"')
            product_result = json.loads(product_result)

            product_policyLiabilities = product_result['policyLiabilities']
            product_policyLiabilities[0]['isCheck'] = True  # 默认选择第一个责任
            product_datas = product_result['productDatas']
            # 如果productDatas有数据 更新一下relativityValue
            # print(product_result['wjsProductName'])
            # print("团体意外伤害保险" in product_result['wjsProductName'])
            if len(product_datas) > 0:
                product_datas = json.dumps(product_datas)
                product_datas = product_datas.replace('null', '\"\"')
                product_datas = json.loads(product_datas)
                checkRule_list = product_datas[0]['checkRule'].replace("{", "").replace("}", "").split(',')
                checkRule_data = checkRule_list[0]
                product_datas[0]['relativityValue'] = checkRule_data

            # 拼装接口入参
            if ("团体意外伤害保险" in product_result['wjsProductName']) and self.isMouthPay == True:
                amountUnitType = 3
            else:
                amountUnitType = 1
            datas = {
                "chargePeriodType": 2,
                "chargeYear": 1,
                "coveragePeriodType": 2,
                "paymentFrequency": 5,
                "countWay": 2,
                "discountRate": 100,
                "amountUnitType": amountUnitType,
                "coverageYear": 1,
                "commissionRate": 0,
                "policyLiabilities": product_policyLiabilities,
                "productDatas": product_datas,
                "id": product_result['id'],
                "wjsProductId": product_result['wjsProductId'],
                "haAppGroupId": product_result['haAppGroupId'],
                "productNum": product_result['productNum'],
                "wjsProductName": product_result['wjsProductName'],
                "isOptionalLiab": True,
                "isCommonSumInsured": False,
                "hasProductPremium": False,
                "isClaimRefund": False,
                "validateTime": product_result['validateTime'],
                "allowSumInsuredTimesSalary": False,
                "isChannelAgent": False
            }
            datas = json.dumps(datas, ensure_ascii=False)
            request_data = {"datas": datas}
            # print(request_data)
            # 发起选择责任条款请求
            save_response = self.API.send_request(modify_group_product_url, 'post', request_data, self.headers)
            if save_response['result'] != True or save_response['success'] != True:
                print('总单险种定义保存失败')
                exit()

    # 新契约-新建计划
    def test_06_add_group_plan(self):

        # 创建多个计划
        for plan_i in range(3):
            create_plan_code_url = self.api_url_datas['queryPlanProducts'].format(self.host_url, self.apply_id)
            random_str = random.sample(string.ascii_letters, 1)
            # 生成计划code
            result = self.API.send_request(create_plan_code_url, 'get', None, self.headers)
            planCode = result['result']['planCode']
            planInfo = result['result']
            groupProducts, countPlanPremium = plan_group_products.format_group_products(planInfo['groupProducts'],
                                                                                        premium=3, sumInsured=800)
            planDatas = {
                "groupPlanId": None,
                "id": None,
                "planCode": planCode,
                "planSerialNo": None,
                "haAppGroupId": self.apply_id,
                "planType": "1",
                "planName": "计划名称" + get_reg_no.current_time_str()[0:8] + random_str[0] + str(plan_i),  # 计划名称
                "isApplyFixedPlan": False,
                "groupProducts": groupProducts,
                "isSync": None,
                "countPlanPremium": countPlanPremium,  # 计划费用
                "occupationalCategory": "2",
                "assumpsit": "计划特别约定：这是一个文本约定" + get_reg_no.current_time_str(),
                "validMinAge": "30",  # 年龄区间开始时间
                "validMinAgeUnit": "day",  # 年龄区间开始时间-单位
                "validMaxAge": "88",  # 年龄区间结束时间
                "csChargeFullYearPremium": None
            }
            planDatas = json.dumps(planDatas, ensure_ascii=False)
            # print(planDatas)
            request_data = {
                'planDatas': planDatas,
                'type': 'add'
            }
            # 保存创建计划
            add_plan_url = self.api_url_datas['addGroupPlan'].format(self.host_url, self.apply_id)
            save_response = self.API.send_request(add_plan_url, 'post', request_data, self.headers)
            if save_response['result'] is not None or save_response['success'] != True:
                print('创建计划保存失败')
                exit()
            else:
                print('创建第{}个计划'.format(plan_i))

        # # 根据计划列表创建计划
        # plan_list_set = ["普通员工综合保障方案–基础"]
        # for plan_name in plan_list_set:
        #     create_plan_code_url = self.api_url_datas['queryPlanProducts'].format(self.host_url, self.apply_id)
        #     random_str = random.sample(string.ascii_letters, 1)
        #     planType = 1
        #     if '子女' in plan_name:
        #         planType = 3
        #     elif '配偶' in plan_name:
        #         planType = 4
        #     elif '父母' in plan_name:
        #         planType = 5
        #     # 生成计划code
        #     result = self.API.send_request(create_plan_code_url, 'get', None, self.headers)
        #     planCode = result['result']['planCode']
        #     planInfo = result['result']
        #     groupProducts, countPlanPremium = plan_group_products.format_group_products(planInfo['groupProducts'],
        #                                                                                 premium=3, sumInsured=800)
        #     planDatas = {
        #         "groupPlanId": None,
        #         "id": None,
        #         "planCode": planCode,
        #         "planSerialNo": None,
        #         "haAppGroupId": self.apply_id,
        #         "planType": planType,
        #         "planName": plan_name,  # 计划名称
        #         "isApplyFixedPlan": False,
        #         "groupProducts": groupProducts,
        #         "isSync": None,
        #         "countPlanPremium": countPlanPremium,  # 计划费用
        #         "occupationalCategory": "2",
        #         "assumpsit": "计划特别约定：这是一个文本约定" + get_reg_no.current_time_str(),
        #         "validMinAge": "30",  # 年龄区间开始时间
        #         "validMinAgeUnit": "day",  # 年龄区间开始时间-单位
        #         "validMaxAge": "88",  # 年龄区间结束时间
        #         "csChargeFullYearPremium": None
        #     }
        #     planDatas = json.dumps(planDatas, ensure_ascii=False)
        #     # print(planDatas)
        #     request_data = {
        #         'planDatas': planDatas,
        #         'type': 'add'
        #     }
        #     # 保存创建计划
        #     add_plan_url = self.api_url_datas['addGroupPlan'].format(self.host_url, self.apply_id)
        #     save_response = self.API.send_request(add_plan_url, 'post', request_data, self.headers)
        #     if save_response['result'] is not None or save_response['success'] != True:
        #         print('创建计划保存失败')
        #         exit()
        #     else:
        #         print('创建第{}个计划'.format(plan_name))

        # 查询增值服务列表
        get_services_url = self.api_url_datas['getServices'].format(self.host_url)
        response = self.API.send_request(get_services_url, 'get', None, self.headers)
        serviceslist = response['result']
        addedValueServiceList = []
        for services in serviceslist:
            # 过滤掉增值服务包
            if services['groupName'] == '':
                services["key"] = services['servicesList'][0]['serviceCode']
                addedValueServiceList.append(services)

        # 查看计划列表信息
        plan_list_url = self.api_url_datas['listAppGroupPlanByAppGroupId'].format(self.host_url, self.apply_id)
        res = self.API.send_request(plan_list_url, 'get', None, self.headers)
        haApplyGroupPlanViewList = res['result']['haApplyGroupPlanViewList']

        if len(haApplyGroupPlanViewList) > 0:
            new_haApplyGroupPlanViewList = []
            if not self.plancode_list:
                addplancode_list = True
            for haApplyGroupPlanView in haApplyGroupPlanViewList:
                if addplancode_list is True:
                    self.plancode_list.append(haApplyGroupPlanView["planCode"])
                PlanView = {
                    "healthDeclarationNo": self.healthDeclarationNo,
                    "haAppGroupId": self.apply_id,
                    "id": haApplyGroupPlanView["id"]
                }
                # 增值服务设置
                service_request_data = {
                    "addedValueServiceList": addedValueServiceList,
                    "planCode": haApplyGroupPlanView["planCode"],
                    "planId": haApplyGroupPlanView["id"]
                }
                # print(service_request_data)
                add_service_url = self.api_url_datas['addServices'].format(self.host_url)
                self.API.send_request(add_service_url, 'post_json', service_request_data, self.headers)
                new_haApplyGroupPlanViewList.append(PlanView)

                # 汇总plancodelist  后面导入清单用
                self.plancode_list.append(haApplyGroupPlanView["planCode"])

        # print(new_haApplyGroupPlanViewList)
        # 设置健康告知
        save_health_url = self.api_url_datas['savePlanHealthDeclaration'].format(self.host_url)
        health_response = self.API.send_request(save_health_url, 'post_json', new_haApplyGroupPlanViewList,
                                                self.headers)
        if health_response['result'] != True or health_response['success'] != True:
            print('设置健康告知失败')
            exit()

    # 新契约-被保人清单导入
    def test_07_insured_import(self):
        # time.sleep(180)

        if not self.plancode_list:
            # 查看计划列表信息
            plan_list_url = self.api_url_datas['listAppGroupPlanByAppGroupId'].format(self.host_url, self.apply_id)
            res = self.API.send_request(plan_list_url, 'get', None, self.headers)
            haApplyGroupPlanViewList = res['result']['haApplyGroupPlanViewList']
            if len(haApplyGroupPlanViewList) > 0:
                for haApplyGroupPlanView in haApplyGroupPlanViewList:
                    self.plancode_list.append(haApplyGroupPlanView["planCode"])

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
            self.opr_xls.save_to_excel_by_cell(i, 16, plan_code_value)

            # # 证件类型为‘护照’
            # insuranceCertNo = 'TX' + get_reg_no.current_time_str() + (str(i) if i >= 10 else '0' + str(i))

            # 证件类型为‘身份证’ , 生成身份证号和出生日期
            insuranceCertNo, birthday, sex = get_reg_no.get_cert_no()

            # 写入Excel文件 被保人证件号  excel表格对应为第7列
            self.opr_xls.save_to_excel_by_cell(i, 7, insuranceCertNo)

            # 写入Excel文件 出生日期  excel表格对应为第11列
            self.opr_xls.save_to_excel_by_cell(i, 11, birthday)

            # 写入Excel文件 性别  excel表格对应为第12列
            self.opr_xls.save_to_excel_by_cell(i, 12, sex)

        self.opr_xls.resave_excel('最终上传数据文件')  # 文件重开另存为'最终上传数据文件'

        # 上传被保人清单
        files_open = open(self.opr_xls.file_path + '最终上传数据文件.xlsx', 'rb')
        files = {'files': files_open}
        insured_import_url = self.api_url_datas['insuredImport'].format(self.host_url, self.apply_id)
        request_data = {
            "groupApplyId": self.apply_id,
            "isFullImport": True,
            "templateId": 100001
        }
        save_response = self.API.send_request(insured_import_url, 'post_file', request_data, self.headers, files)
        files_open.close()
        if save_response['errorMsg'] is not None or save_response['success'] is not True:
            print('上传被保人清单失败')
            exit()
        else:
            # 上传后删除生成的最终文件
            self.opr_xls.delete_excel_file(self.opr_xls.new_file)

            # 计算总保费
            count_premium_url = self.api_url_datas['createProPremiumBatch'].format(self.host_url, self.apply_id)
            premium_response = self.API.send_request(count_premium_url, 'get', None, self.headers)
            time_i = 0
            while premium_response['success'] is not True:
                # 查询结果为空 重新再请求一次
                print('计算总保费失败，等20s后重新查询')
                time.sleep(20)
                premium_response = self.API.send_request(count_premium_url, 'get', None, self.headers)
                if time_i == 5:
                    break
                else:
                    time_i += 1

            if premium_response['errorMsg'] is not None or premium_response['success'] is not True:
                print('计算总保费失败')
                exit()

    # 新契约-提交
    def test_08_submit_review(self):
        # 获取公安接口校验不通过数据
        validation_url = self.api_url_datas['NameValidationList'].format(self.host_url, self.apply_id)
        validation_respond = self.API.send_request(validation_url, 'get', None, self.headers)
        if validation_respond['result']['data'] is not None:
            validation_list = validation_respond['result']['data']
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
                    'policyCategory': validation_name['policyCategory']
                }
                upload_url = self.api_url_datas['addApplyAttachment'].format(self.host_url)
                self.API.send_request(upload_url, 'post_file', request_data, self.headers, files)

        submit_review_url = self.api_url_datas['validateBeforeFinish'].format(self.host_url, self.apply_id)
        self.API.send_request(submit_review_url, 'get', None, self.headers)

    # 新契约-复核
    def test_09_finish_data_review(self):
        # 复核 设置经办人
        lock_viwe_url = self.api_url_datas['lockViewGroup'].format(self.host_url, self.apply_id)
        self.API.send_request(lock_viwe_url, 'get', None, self.view_headers)

        # 查询保单号
        search_url = self.api_url_datas['queryForUnderCheck'].format(self.host_url, self.apply_id)
        res = self.API.send_request(search_url, 'get', None, self.view_headers)
        datas = res['result']
        # 更新复核数据
        if self.channelType == 'A':
            secondPartnerCode = 'A030190'  # 直接业务 二级合作方 'A030190' 众安官网
        else:
            secondPartnerCode = 'B02OL358'  # 中介业务 二级合作方   'B02OL358' 美华保险销售有限公司
            for i in range(len(datas['groupProductViewList'])):
                datas['groupProductViewList'][i]['commissionRate'] = '25.01'

            # print('中介业务要填佣金，请手工进行人工核保')
            # exit()
        datas['secondPartnerCode'] = secondPartnerCode
        datas['validateTime'] = self.validateTime
        datas['bdSalesmanCode'] = self.bdSalesmanCode
        datas.pop('agreementChannelCode', 404)
        datas.pop('agentChannelCode', 404)

        # 复核 数据确认
        check_url = self.api_url_datas['dataReviewCheck'].format(self.host_url)
        request_data = {
            "applyGroupId": self.apply_id,
            "datas": json.dumps(datas, ensure_ascii=False)
        }
        res = self.API.send_request(check_url, 'post', request_data, self.view_headers)
        if res['success'] is True and res['result'] is None:
            # 复核通过
            finish_url = self.api_url_datas['finishDataReview'].format(self.host_url, self.apply_id)
            res = self.API.send_request(finish_url, 'get', None, self.view_headers)

    # 新契约-人工核保
    def test_10_save_group_decision(self):
        # 查询人工核保列表
        get_task_url = self.api_url_datas['getPubTask'].format(self.host_url, self.apply_id)
        request_data = {
            "uwLevel": 1,
            "currentPage": 1,
            "pageSize": 10,
            "uwPolicyCategory": 1,
            "objectNo": self.haAppGroupNo
        }
        res = self.API.send_request(get_task_url, 'post', request_data, self.view_headers)
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
        res = self.API.send_request(locked_tast_url, 'post', {'systemSource': None}, self.view_headers)

        # 整单核保完成
        save_decision_url = self.api_url_datas['saveGroupDecision'].format(self.host_url)
        request_data = {
            "haUwId": tast_locked_id,
            "objectId": self.apply_id
        }
        res = self.API.send_request(save_decision_url, 'post', request_data, self.view_headers)

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
                currencyRate = res_get[0]['currencyRate']
                request_data = {
                    "businessList": [{
                        "id": billId,
                        "relatedPolicyId": relatedPolicyId
                    }],
                    "paymentType": "RECEIVABLES",
                    "currencyRate": currencyRate,
                    "confirmType": "1",
                    "recordList": [{
                        "zaAccountNo": zaAccountNo,
                        "_index": 0,
                        "_rowKey": 5
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

    test = groupInsurance()
    test.run()
