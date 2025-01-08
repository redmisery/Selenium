import configparser
import logging
import shutil
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LogConfig:
    """
    通过config/log_config.ini文件获取日志配置
    """
    current_dir = Path(__file__).resolve()
    home = current_dir.parents[1]
    log_config_path = home / "config" / "log.ini"

    @staticmethod
    def get_config(key=None):
        """
        获取日志配置
        :param key: 日志配置项
        :return: 日志配置值
        """
        config = configparser.ConfigParser(interpolation=None)
        config.read(LogConfig.log_config_path)
        if key:
            return config.get('log', key)
        else:
            return config['log']


class LogUtils(Logger):
    """
    日志工具类:
    继承Logger类，重写error、info、debug方法，使用反射设置日志级别
    """
    # 用于存储不同日志级别的日志处理器
    file_handlers = {}
    current_level = LogConfig.get_config('log_level')
    log_format = LogConfig.get_config('log_format')
    # 日志级别字典集合
    log_levels = {'CRITICAL': 50, 'FATAL': 50, 'ERROR': 40, 'WARNING': 30, 'WARN': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0}
    # 清空日志目录
    shutil.rmtree(LogConfig.home / LogConfig.get_config("log_path"), ignore_errors=True)

    def __init__(self):
        super().__init__(LogUtils.current_level)
        # 创建一个日志对象
        self.__logger = super()
        # 设置日志级别
        self.__logger.setLevel(LogUtils.current_level.upper())

    # 创建日志句柄
    @staticmethod
    def create_file_handler(level):
        log_dirname = LogConfig.home / LogConfig.get_config("log_path")
        log_base_name = f"{LogConfig.get_config('log_base_name')}_{level}.log"
        log_file_name = log_dirname / log_base_name
        log_dirname.mkdir(parents=True, exist_ok=True)
        # 创建文件日志的控制器
        if level not in LogUtils.file_handlers.keys():
            file_handler = RotatingFileHandler(filename=log_file_name, encoding='utf-8', delay=True, maxBytes=1 * 1024 * 1024, backupCount=10)
            # 使用反射设定日志级别
            file_handler.setLevel(getattr(logging, level.upper()))
            # 设置日志格式
            file_handler.setFormatter(logging.Formatter(LogUtils.log_format))
            # 将控制器加入日志对象
            LogUtils.file_handlers[level] = file_handler
        return LogUtils.file_handlers[level]

    def errors(self, msg, *args, **kwargs):
        """
        同时写入error和debug日志
        """
        self.__logger.addHandler(self.create_file_handler('debug'))
        self.__logger.addHandler(self.create_file_handler('error'))
        self._log(LogUtils.log_levels['ERROR'], msg, args, **kwargs)

    def infos(self, msg, *args, **kwargs):
        """
        同时写入info和debug日志
        """
        self.__logger.addHandler(self.create_file_handler('debug'))
        self.__logger.addHandler(self.create_file_handler('info'))
        self._log(LogUtils.log_levels['INFO'], msg, args, **kwargs)

    def logs(self, msg, *args, **kwargs):
        """
        同时写入所有日志
        """
        self.__logger.addHandler(self.create_file_handler('debug'))
        self.__logger.addHandler(self.create_file_handler('info'))
        self.__logger.addHandler(self.create_file_handler('error'))
        self._log(LogUtils.log_levels['INFO'], msg, args, **kwargs)

    # 重写debug
    def debug(self, msg, *args, **kwargs):
        """
        写入debug日志
        """
        self.__logger.addHandler(self.create_file_handler('debug'))
        self._log(LogUtils.log_levels['DEBUG'], msg, args, **kwargs)

    # 重写info
    def info(self, msg, *args, **kwargs):
        """
        写入info日志
        """
        self.__logger.addHandler(self.create_file_handler('info'))
        self._log(LogUtils.log_levels['INFO'], msg, args, **kwargs)

    # 重写error
    def error(self, msg, *args, **kwargs):
        """
        写入error日志
        """
        self.__logger.addHandler(self.create_file_handler('error'))
        self._log(LogUtils.log_levels['ERROR'], msg, args, **kwargs)

