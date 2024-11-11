from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML()


class Config:
    """
    路径、项目管理工具类
    """

    @property
    def project_path(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def config_path(self) -> Path:
        return self.project_path / 'config' / 'config.yaml'

    @property
    def data_path(self) -> Path:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            data_path = self.project_path / config['data']['data_path']
            return data_path

    @property
    def public_data_path(self) -> Path:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            public_data_path = self.project_path / config['data']['public_data_path']
            return public_data_path
