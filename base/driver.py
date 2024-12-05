import traceback

from selenium.webdriver import Chrome
from base.session import SessionManager
from common import LogUtils


class Driver:
    """
    驱动类
    description: 由于Selenium的驱动启动过程比较耗时，因此这里使用单例模式，避免每次都要启动驱动,
                 同时Selenium升级到4.26.1后，会自动获取最新驱动，无需手动更新，在此不使用本地chrome_driver_update包
                 首次启动时间较长，请耐心等待。
    """
    __instance = None
    __inited = False

    def __new__(cls):
        """
        单例模式
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__inited:
            self.__inited = True
            driver_path = None
            try:
                self.driver = Chrome()
                driver_path = self.driver.service.path
                # 驱动启动起始位置
                self.driver.set_window_position(-8, 0, windowHandle='current')
                # 驱动启动起始大小
                self.driver.set_window_size(1920, 1080, windowHandle='current')
                # 实例化session管理器
                self.sessionManger = SessionManager(self.driver)
                debug_log = f'驱动路径：{driver_path}！  Driver first created!'
                LogUtils().debug(debug_log)
            except RuntimeError as e:
                error_log = f'驱动{driver_path}启动失败！{e} {traceback.format_exc()}'
                LogUtils().error(error_log)
                raise RuntimeError(error_log)


    # 关闭driver
    @staticmethod
    def close_driver(self):
        try:
            self.driver.quit()
            debug_log = 'Driver closed'
            LogUtils().debug(debug_log)
            self.__instance = None  # 重置驱动实例
            self.__inited = False  # 重置初始化状态
            self.sessionManger = None  # 重置session管理实例
        except Exception as e:
            error_log = f'Driver close failed!{e} {traceback.format_exc()}'
            LogUtils().error(error_log)
            raise Exception(error_log)