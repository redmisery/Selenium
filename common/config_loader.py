import configparser
import os


class Config:
    @staticmethod
    def log_config(key):
        """
        获取日志配置,加入${}扩展替换为环境变量值
        :param key: 配置项
        :return: 配置值
        """
        output = None
        config_path = os.getenv("CONFIG_PATH")
        if config_path:
            config = configparser.ConfigParser()
            config.read(config_path)
            if key and config.has_option("log", key):
                config["log"][key] = os.path.expandvars(config["log"][key])
                output = config["log"][key]
        return output