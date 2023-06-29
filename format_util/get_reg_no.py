import random
import datetime
import time



# 统一社会信用代码
def create_uniSocialCreCode():
    # 开头四位写死
    str_4 = '2123'
    # 5-17位为生成13位随机数
    str_13 = str(random.randint(1000000000000, 9999999999999))
    # 通过加权因子值 计算求和
    sum_N = 2 + 3 + 18 + 81 + int(str_13[0]) * 19 + int(str_13[1]) * 26 + int(str_13[2]) * 16 + int(
        str_13[3]) * 17 + int(str_13[4]) * 20 + int(str_13[5]) * 29 + int(str_13[6]) * 25 + int(
        str_13[7]) * 13 + int(str_13[8]) * 8 + int(str_13[9]) * 24 + int(str_13[10]) * 10 + int(
        str_13[11]) * 30 + int(str_13[12]) * 28

    # 根据mod31 计算校验码
    if sum_N % 31 == 0:
        mod_N = 0
    else:
        mod_N = 31 - (sum_N % 31)
    # print(mod_N)

    str_Arr = {
        10: "A",
        11: "B",
        12: "C",
        13: "D",
        14: "E",
        15: "F",
        16: "G",
        17: "H",
        18: "J",
        19: "K",
        20: "L",
        21: "M",
        22: "N",
        23: "P",
        24: "Q",
        25: "R",
        26: "T",
        27: "U",
        28: "W",
        29: "X",
        30: "Y"
    }

    # 根据校验码得出最后一位的值
    if mod_N >= 10:
        str_last = str_Arr[mod_N]
    else:
        str_last = str(mod_N)

    return str_4 + str_13 + str_last


# 营业执照
def create_icRegNo():
    return '7' + current_time_str()


# 税务登记号
def create_taxRegNum():
    return '8' + current_time_str()


# 法人证件号码
def create_legalCertNo():
    return 'P' + current_time_str()


# 纳税人识别号
def create_taxpayerIdtfNumber():
    return 'T' + current_time_str()


# 团险组织机构代码
def create_orgCode():
    return '9' + current_time_str()


# 雇主组织机构代码
def create_employer_orgCode():
    return time.strftime('%m%d%H%M%S', time.localtime(time.time()))


# 生成当前系统时间日期格式
def current_time_str():
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


# 获取当前日期的前一天
def get_yesterday_date():
    today = datetime.date.today()  # datetime类型当前日期
    yesterday = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    # yesterday = '2021-04-01'
    return yesterday


# 获取当前日期
def get_today_date():
    today = datetime.date.today().strftime("%Y-%m-%d")  # datetime类型当前日期
    # today = '2021-04-02'
    return today

# 获取当前日期
def get_today_date_correct():
    today = datetime.date.today().strftime("%Y%m%d")  # datetime类型当前日期
    return today

# 获取一年后日期
def get_year_later_date():
    today = datetime.date.today()  # datetime类型当前日期
    year_later_day = (today + datetime.timedelta(days=+364)).strftime("%Y-%m-%d")
    # today = '2021-04-02'
    return year_later_day


# 生成当前日期中文字符集 几月几日
def get_date_str():
    chinese = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    month = datetime.datetime.now().month
    if month > 10:
        mouth_str = chinese[10] + chinese[month % 10] + "月"
    else:
        mouth_str = chinese[month] + "月"

    day = datetime.datetime.now().day
    if day > 30:
        day_str = chinese[3] + chinese[10] + chinese[day % 10] + "日"
    elif day == 30:
        day_str = chinese[3] + chinese[10] + "日"
    elif day > 20:
        day_str = chinese[2] + chinese[10] + chinese[day % 10] + "日"
    elif day == 20:
        day_str = chinese[2] + chinese[10] + "日"
    elif day > 10:
        day_str = chinese[10] + chinese[day % 10] + "日"
    elif day == 10:
        day_str = chinese[10] + "日"
    else:
        day_str = chinese[day % 10] + "日"

    return mouth_str + day_str


def get_cert_no(birthdate=None, sex=None):
    # 身份证号的前两位，省份代号
    sheng = (
    '11', '12', '13', '14', '15', '21', '22', '23', '31', '32', '33', '34', '35', '36', '37', '41', '42', '43', '44',
    '45', '46', '50', '51', '52', '53', '54', '61', '62', '63', '64', '65')

    # 随机选择距离今天在7000到25000的日期作为出生日期（没有特殊要求我就随便设置的，有特殊要求的此处可以完善下）
    if birthdate is None:
        birthdate = (datetime.date.today() - datetime.timedelta(days=random.randint(7300, 21900))).strftime("%Y%m%d")

    # 拼接出身份证号的前17位（第3-第6位为市和区的代码，中国太大此处就偷懒了写了定值，有要求的可以做个随机来完善下；第15-第17位为出生的顺序码，随机在100到199中选择）
    ident = sheng[random.randint(0, 30)] + '0101' + birthdate + str(random.randint(100, 199))

    if int(ident[-1]) % 2 == 0:
        sex = '女'
    else:
        sex = '男'
    # 前17位每位需要乘上的系数，用字典表示，比如第一位需要乘上7，最后一位需要乘上2
    coe = {1: 7, 2: 9, 3: 10, 4: 5, 5: 8, 6: 4, 7: 2, 8: 1, 9: 6, 10: 3, 11: 7, 12: 9, 13: 10, 14: 5, 15: 8, 16: 4,
           17: 2}
    summation = 0

    # for循环计算前17位每位乘上系数之后的和
    for i in range(17):
        summation = summation + int(ident[i:i + 1]) * coe[i + 1]  # ident[i:i+1]使用的是python的切片获得每位数字

    # 前17位每位乘上系数之后的和除以11得到的余数对照表，比如余数是0，那第18位就是1
    key = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}

    # 拼接得到完整的18位身份证号
    return ident + key[summation % 11], birthdate, sex


if __name__ == '__main__':
    print(current_time_str()[0:6])
