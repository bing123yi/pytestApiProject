import json
import os


class OperationJson:
    def __init__(self, file_path=None, file_name=None):
        pass

    def read_data(self, file_path=None, file_name=None):
        # 当前路径
        current_path = os.path.abspath(os.path.dirname(__file__))
        # print(current_path)
        # 上一级路径（父级路径）
        parent_path = os.path.dirname(current_path)
        if file_path is None:
            file_path = parent_path + "/json_conf/"
        else:
            file_path = parent_path + file_path
        if file_name is None:
            file_name = "basic_info"
        json_file = file_path + str(file_name) + '.json'
        with open(json_file, encoding='utf-8') as fp:
            data = json.load(fp)
            return data


if __name__ == '__main__':
    test = OperationJson()
    request_data = test.read_data()
    format_request_data = []
    if len(request_data) > 0:
        for key, value in request_data.items():
            format_request_data.append(key + '=' + value)
    print('&'.join(format_request_data))
