import yaml
import os


class ReadYaml:

    def __init__(self):
        pass

    def read_yaml(self, file_name):

        # 当前路径
        current_path = os.path.abspath(os.path.dirname(__file__))
        # print(current_path)
        # 上一级路径（父级路径）
        parent_path = os.path.dirname(current_path)
        # print(parent_path)

        config_file = parent_path + "\\conf\\{}.yaml".format(file_name)
        # print(config_file)
        with open(config_file, encoding='UTF-8') as fs:
            datas = yaml.load(fs, Loader=yaml.FullLoader)
            # print(type(datas))
            return datas


if __name__ == '__main__':
    test = ReadYaml()
    test.read_yaml("api_url")
