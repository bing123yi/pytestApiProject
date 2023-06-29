from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from conf.header_conf import headers
from util.opr_json import OperationJson


# 公共功能-黑名单-黑名单管理
# 添加黑名单
class addBlacklist:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.api_url_datas = ReadYaml().read_yaml("add_blacklist_url")
        # 选择环境
        self.host_url = self.api_url_datas['uat_url']  # 环境地址
        self.headers = headers  # 登陆人cookie

        self.name = "父母反洗"  # 姓名
        self.certNo = "110101196501010114"  # 身份证号

        # 注意 如果只需要满足其中一个风险等级，则其他等级置为0，否则将按所配置的三个风险等级进行匹配对应的风险分类和风险描述
        self.riskGrade = 0  # 健康风险等级
        self.fraudRiskGrade = 0  # 欺诈风险等级
        self.launderMoneyGrade = 5  # 洗钱风险等级

        # 或者直接指定某个风险描述, 指定后 上面三个风险等级将会忽略
        self.riskCategory = ""  # 风险分类 例如"洗钱风险"
        self.riskDescription = ""  # 风险描述 例如"疑似套利、套现或洗钱"

        self.origin = "U"  # 来源  核保U
        self.status = "A"  # 黑名单 审核通过A / 审核拒绝D

    # 新增审核黑名单
    def test_01_add_blacklist(self):
        # time.sleep(3)
        # 获取风险规则列表
        riskRules_url = self.api_url_datas['riskRules'].format(self.host_url)
        riskRules_response = self.API.send_request(riskRules_url, 'get', None, headers)
        risk_rules_list = riskRules_response['result']
        riskId = self.get_riskId(risk_rules_list)
        if riskId == '':
            print("未找到符合条件的风险分类和风险描述，请检查！！！")
            exit()
        # 根据身份证号获取性别
        last_2_num = self.certNo[-2:-1]
        if int(last_2_num) % 2 == 1:
            gender = "M"
        else:
            gender = "F"

        # 根据身份证号获取生日
        birthday = self.certNo[6:10] + '-' + self.certNo[10:12] + '-' + self.certNo[12:14]

        request_data = {
            "certType": "I",
            "name": self.name,
            "certNo": self.certNo,
            "gender": gender,
            "birthday": birthday,
            "origin": self.origin,
            "operator": "liangzhixiao",
            "blackLists": [{
                "riskCategory": self.riskCategory,
                "riskId": riskId,
                "remark": "补充说明："
            }]
        }
        # 新建黑名单
        blacklistsAddurl = self.api_url_datas['blacklistsAdd'].format(self.host_url)
        register_response = self.API.send_request(blacklistsAddurl, 'post_json', request_data, self.headers)
        self.apply_id = register_response['result']

    # 审核黑名单
    def test_02_save_basic_info(self):

        # time.sleep(3)
        url = self.api_url_datas['blacklistsQuery'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "origin": "U",
            "batchNo": None,
            "currentPage": 1,
            "pageSize": 1000,
            "status": "I"
        }
        # print(request_data)
        # 新契约-保存第一步（投保单基本信息）
        save_response = self.API.send_request(url, 'post_json', request_data, self.headers)
        resultList = save_response['result']['resultList']
        blackListId = resultList[len(resultList) - 1]['id']
        Status_url = self.api_url_datas['blacklistStatus'].format(self.host_url)
        # 获取请求json入参数据
        request_data = {
            "blackListId": [str(blackListId)],
            "status": self.status
        }

        response=self.API.send_request(Status_url, 'put', request_data, self.headers)
        print('返回结果: {}'.format(response))

    def get_riskId(self, risk_rules_list):
        riskId = ''
        # 根据指定某个风险描述获取相应的风险等级名称和风险等级code
        if self.riskCategory != '' and self.riskDescription != '':
            for risk in risk_rules_list:
                if risk["riskCategory"] == self.riskCategory and risk["riskDescription"] == self.riskDescription:
                    riskId = risk['id']
                    self.riskGrade = risk['riskGrade']
                    self.fraudRiskGrade = risk['fraudRiskGrade']
                    self.launderMoneyGrade = risk['launderMoneyGrade']
                    break
        else:
            # 根据风险等级获取riskId
            for risk in risk_rules_list:
                if self.riskGrade == risk['riskGrade'] and risk['fraudRiskGrade'] == self.fraudRiskGrade and self.launderMoneyGrade == risk['launderMoneyGrade']:
                    riskId = risk['id']
                    self.riskCategory = risk['riskCategory']
                    self.riskDescription = risk['riskDescription']
                    break
        print("风险分类为：" + self.riskCategory)
        print("风险描述为：" + self.riskDescription)
        print("健康风险等级为：" + str(self.riskGrade))
        print("欺诈风险等级为：" + str(self.fraudRiskGrade))
        print("洗钱风险等级为：" + str(self.launderMoneyGrade))
        return riskId


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])

    test = addBlacklist()
    test.test_01_add_blacklist()  # 新增审核黑名单
    test.test_02_save_basic_info()  # 审核黑名单
