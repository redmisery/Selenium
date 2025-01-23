import configparser
import os
from pathlib import Path
from typing import Type


class Config:
    @staticmethod
    def dependency_config():
        """
        获取依赖配置，配置文件dependency.yaml
        """
        from ruamel.yaml import YAML
        yaml = YAML()
        dependency_path = Path(os.getenv("DEPENDENCY_PATH"))
        if dependency_path.exists():
            try:
                with dependency_path.open("r") as f:
                    return yaml.load(f)
            except Exception as e:
                raise f'读取依赖配置失败，原因：{e}'
        else:
            raise FileNotFoundError(f'依赖配置文件路径不存在，请检查DEPENDENCY_PATH:{dependency_path}是否配置正确')

    @staticmethod
    def getini(section, key, key_type: Type = str):
        """
        获取配置,配置文件config.ini
        """
        config_path = Path(os.getenv("CONFIG_PATH"))
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            # 根据type获取对应值
            try:
                if key_type == str:
                    return config.get(section, key)
                elif key_type == int:
                    return config.getint(section, key)
                elif key_type == float:
                    return config.getfloat(section, key)
                elif key_type == bool:
                    return config.getboolean(section, key)
                else:
                    raise TypeError(f'不支持的类型{key_type}')
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                raise f'读取配置失败，原因：{e}'
        else:
            raise FileNotFoundError(f'配置文件路径不存在，请检查CONFIG_PATH:{config_path}是否配置正确')