import logging
import shutil
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ruamel.yaml import YAML

class LogConfig:
    """
    通过config/log_config.yaml文件获取日志配置
    """
    yaml = YAML()
    current_dir = Path(__file__).resolve()
    project_path = current_dir.parents[1]
    log_config_path = project_path / "config/config.yaml"

    @staticmethod
    def get_log_config(key=None):
        with open(LogConfig.log_config_path, "r") as f:
            data = LogConfig.yaml.load(f)
            if key and data:
                log_config = data["log"][key]
            else:
                log_config = data["log"]
            return log_config


class LogUtils(Logger):
    """
    日志工具类:
    继承Logger类，重写error、info、debug方法，使用反射设置日志级别
    """
    file_handlers = {}
    current_level = LogConfig.get_log_config('log_level')
    log_format = LogConfig.get_log_config('log_format')
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    shutil.rmtree(LogConfig.project_path / LogConfig.get_log_config("log_path"),ignore_errors=True)
    def __init__(self):
        super().__init__(LogUtils.current_level)
        # 创建一个日志对象
        self.__logger = super()
        # 设置日志级别
        self.__logger.setLevel(LogUtils.current_level.upper())

    # 创建日志句柄
    @staticmethod
    def create_file_handler(level):
        log_dirname = LogConfig.project_path / LogConfig.get_log_config("log_path")
        log_base_name = f"{LogConfig.get_log_config('log_base_name')}_{level}.log"
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

    # 重写error
    def error(self, msg, *args, **kwargs):
        self.__logger.addHandler(self.create_file_handler('error'))
        if self.isEnabledFor(LogUtils.ERROR):
            self._log(LogUtils.ERROR, msg, args, **kwargs)

    # 重写info
    def info(self, msg, *args, **kwargs):
        self.__logger.addHandler(self.create_file_handler('info'))
        if self.isEnabledFor(LogUtils.INFO):
            self._log(LogUtils.INFO, msg, args, **kwargs)

    # 重写debug
    def debug(self, msg, *args, **kwargs):
        self.__logger.addHandler(self.create_file_handler('debug'))
        if self.isEnabledFor(LogUtils.DEBUG):
            self._log(LogUtils.DEBUG, msg, args, **kwargs)
