import inspect
import os
from pathlib import Path

from ruamel.yaml import YAML, CommentedMap
from selenium.webdriver.common.by import By

from common import LogUtils


class Element:
    """
    元素对象，包含元素定位方式和定位路径。
    """
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
            LogUtils().errors(error_log)
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
        yaml_dir = Path(os.getenv('HOME')) / 'page_object' / 'elements'
        # 获取调用该类的文件名
        caller_file = inspect.stack()[1].filename
        # 元素文件名
        yaml_name = yaml_name or Path(caller_file).stem + '.yaml'
        yaml_path = yaml_dir / yaml_name
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml = YAML()
                self.data: CommentedMap = yaml.load(f)
                if not self.data:
                    error_log = f"元素文件为空: {yaml_path}"
                    LogUtils().errors(error_log)
                    raise Exception(error_log)
        except FileNotFoundError as e:
            error_log = f"元素文件未找到: {yaml_path}! {e}"
            LogUtils().errors(error_log)
            raise FileNotFoundError(error_log)
        except Exception as e:
            error_log = f"加载元素时发生错误: {str(e)}"
            LogUtils().errors(error_log)
            raise Exception(error_log)


    def load(self):
        """
        加载yaml文件中的元素信息，并返回所有元素对象。
        """
        # 默认不要第一层的模块名，只保留元素，不能直接使用data.values()，否则返回一个CommentedMapView视图对象
        yaml_data: CommentedMap = iter(self.data.values()).__next__()

        # 阶段1：创建所有对象
        def create_page_stage1(data, parent, parent_path="") -> object:
            for key, value in data.items():
                current_path = f"{parent_path}.{key}" if parent_path else key
                if isinstance(value, dict):
                    # 修复逻辑：判断当前层级是否直接定义 method 和 path
                    is_element = 'method' in value.keys() and 'path' in value.keys()

                    if is_element:
                        # 创建元素对象
                        try:
                            element = Element(value['method'], value['path'])
                            setattr(parent, key, element)
                        except KeyError as e:
                            error_log = f"元素配置错误: {key} {value} {e}"
                            LogUtils().errors(error_log)
                            raise KeyError(error_log)
                        # 递归处理子元素（支持元素嵌套子元素）
                        create_page_stage1(value, element, current_path)
                    else:
                        # 创建模块对象
                        module = type(key, (object,), {})()
                        setattr(parent, key, module)
                        create_page_stage1(value, module, current_path)
            return parent

        # 执行加载
        try:
            self.page = create_page_stage1(yaml_data, type('Page', (object,), {})())
            return self.page
        except Exception as e:
            LogUtils().errors(f"加载页面对象失败: {str(e)}")
            raise

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
            LogUtils().errors(error_log)
            raise AttributeError(error_log)
