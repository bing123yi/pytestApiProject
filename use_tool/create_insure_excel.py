from util.send_request import SendRequest
from util.read_yaml import ReadYaml
from util.opr_excel import OperationExcel
from conf.header_conf import headers, headers_ruixiang
from util.opr_json import OperationJson
from format_util import get_reg_no, plan_group_products
import json, os, time, random, string


# 意健险-新契约-投保单录入
# 团险线下出单
class createInsureExcel:

    def __init__(self):
        self.API = SendRequest()
        self.OprJson = OperationJson()
        self.strNo = get_reg_no.get_date_str()
        self.opr_xls = OperationExcel(file_path="D:\\code\python\pytestApiProject\\upload_file\\create_insurance\\",
                                      file_name='标准团单被保人清单')  # 上传被保人清单模板
        self.plancode_list = ['HACP211222675005', 'HACP211222675004']   #计划编码
        self.haGroupPolicyNo = None

    # 新契约-被保人清单导入
    def create_insure_excel(self):

        # 获取Excel文件最大的行数
        max_row = self.opr_xls.max_row
        code_index = 0
        # 更新保险计划code  数据是从第6行开始
        for i in range(6, max_row + 1):

            print("第{}行，被保人姓名: {}".format(str(i), self.opr_xls.get_cell_value(i, 1)))  # 打印被保人信息

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
            birthdate, set_sex = None, None
            if i < 80:
                birthdate = '19920101'
            elif i < 12:
                birthdate = '20080101'
            elif i < 18:
                birthdate = '20100101'
            elif i < 36:
                birthdate = '20150101'




            insuranceCertNo, birthday, sex = get_reg_no.get_cert_no(birthdate, set_sex)

            # 写入Excel文件 被保人证件号  excel表格对应为第7列
            self.opr_xls.save_to_excel_by_cell(i, 7, insuranceCertNo)

            # 写入Excel文件 被保人证件号  excel表格对应为第11列
            self.opr_xls.save_to_excel_by_cell(i, 11, birthday)

            # 写入Excel文件 被保人证件号  excel表格对应为第12列
            self.opr_xls.save_to_excel_by_cell(i, 12, sex)

        self.opr_xls.resave_excel('团险导入文件')  # 文件重开另存为'最终上传数据文件'
        print('创建文件成功：文件名称为“团险导入文件”')


if __name__ == '__main__':
    # pytest.main(['-s', '-n 2'])

    test = createInsureExcel()
    test.create_insure_excel()  # 创建excel
