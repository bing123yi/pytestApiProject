import random
import datetime
import time


# 处理计划中的险种和责任
def format_group_products(groupProducts, premium=800, sumInsured=10000):
    new_groupProducts = []
    countPlanPremium = 0
    i = 1
    if len(groupProducts) > 0:
        for product in groupProducts:
            # print("产品层级:-------------------" )
            # print(product)
            # 更新保额 保费
            len_num = len(product['liabilities'])
            product['premium'] = premium * len_num * i
            product['sumInsured'] = sumInsured * len_num
            product['isAddUpIndividual'] = "Y"
            product['planSelect'] = True
            product['liabilities'] = format_liabilities(product['liabilities'], premium * i, sumInsured * i)
            new_groupProducts.append(product)
            if product['amountUnitType'] == 3:
                product['premium'] = 0.01
                product['sumInsured'] = 10
            else:
                countPlanPremium += product['premium']
            i += 1
    else:
        print("险种责任列表为空，请确认已选择产品和责任")

    return new_groupProducts, countPlanPremium


# 处理责任
def format_liabilities(liabilities, premium, sumInsured):
    new_liabilities = []
    if len(liabilities) > 0:
        for liabilitiy in liabilities:
            # print("责任层级:+++++++++++++++++++++")
            # print(liabilitiy)
            # 更新保额 保费
            liabilitiy['premium'] = premium
            liabilitiy['sumInsured'] = sumInsured
            if liabilitiy['amountUnitType'] == 3:
                liabilitiy['premium'] = 0.01
                liabilitiy['minInsured'] = 200
                liabilitiy['maxInsured'] = 180000
                liabilitiy['sumInsured'] = 10
            liabilitiy['isAddUpProduct'] = "Y"
            liabilitiy['isSelect'] = True
            liabilitiy['libityRelativeData'] = format_liabililibityRelativeData(liabilitiy['libityRelativeData'])
            new_liabilities.append(liabilitiy)
    else:
        print("责任列表为空，请确认已选择责任")

    return new_liabilities


# 处理责任明细
def format_liabililibityRelativeData(libityRelativeData):
    new_libityRelativeData = []
    if len(libityRelativeData) > 0:
        for libityRelative in libityRelativeData:
            # 去除多余字段
            libityRelative.pop('haAppPlanId', 404)
            libityRelative.pop('haAppPlanProductId', 404)
            libityRelative.pop('haAppPlanProLiabId', 404)
            libityRelative.pop('isDisplay', 404)
            libityRelative.pop('isReadonly', 404)
            libityRelative.pop('orderNo', 404)
            libityRelative.pop('checkRule', 404)
            libityRelative.pop('checkRuleDesc', 404)
            new_libityRelativeData.append(libityRelative)
    else:
        print("责任明细为空，不处理")

    return new_libityRelativeData


