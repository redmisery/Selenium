import inspect
from pathlib import Path

from ruamel.yaml import YAML
from selenium.webdriver.common.by import By

from common import LogUtils, Config


class Element:
    __method_set = {'css', 'xpath'}
    __method_map = {
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH
    }

    def __init__(self, method: str, path: str):
        if method in self.__method_set:
            self.method = self.__method_map.get(method)
            self.path = path
        else:
            error_log = f'{method} not support! '
            LogUtils().error(error_log)
            raise Exception(error_log)


class Page:
    """
    加载yaml文件中的元素信息，并返回所有元素对象。
    element的元素文件名必须和operation的操作文件名一致，且位于elements目录下。
    加载元素后的结构示例：
        {模块：{元素：元素对象}}
    """
    def __init__(self, yaml_name: str = None):
        self.page = None
        # yaml文件路径
        yaml_dir = Config().project_path / 'page_object' / 'elements'
        # 获取调用该类的文件名
        caller_file = inspect.stack()[1].filename
        # 元素文件名
        yaml_name = yaml_name or Path(caller_file).stem + '.yaml'
        yaml_path = yaml_dir / yaml_name
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml = YAML()
                self.data = dict(yaml.load(f))
                if not self.data:
                    error_log = f"元素文件为空: {yaml_path}"
                    LogUtils().error(error_log)
                    raise Exception(error_log)
        except FileNotFoundError as e:
            error_log = f"元素文件未找到: {yaml_path}! {e}"
            LogUtils().error(error_log)
            raise FileNotFoundError(error_log)
        except Exception as e:
            error_log = f"加载元素时发生错误: {str(e)}"
            LogUtils().error(error_log)
            raise Exception(error_log)

    def load(self):
        # 默认不要第一层的模块名，只保留元素
        yaml_data = self.data.values()
        # 使用递归函数根据yaml结构创建page对象
        def create_page(data, parent):
            for key, value in data:
                if isinstance(value, dict) and ('method' or 'path') in value:
                    # 创建元素
                    element = Element(value['method'], value['path'])
                    setattr(parent, key, element)
                else:
                    # 创建模块
                    module = type(key, (object,), {})()
                    create_page(value, module)
                    setattr(parent, key, module)
            return parent
        self.page = create_page(yaml_data, type('Page', (object,), {})())
        return self.page

    def __getattr__(self, item):
        # 增加链式访问
        try:
            current = self.page
            parts = item.split('.')
            for part in parts:
                current = getattr(current, part)
                if current is None:
                    raise AttributeError
            return current
        except AttributeError:
            error_log = f"元素不存在: {item}"
            LogUtils().error(error_log)
            raise AttributeError(error_log)