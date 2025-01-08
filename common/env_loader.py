from pathlib import Path

from dotenv import dotenv_values

from common import LogUtils

"""
由pytest-dotenv自动执行加载，无需显式加载环境变量
"""


class Env:
    # 必要环境变量
    __env_data = {
        'HOME': Path(__file__).resolve().parents[1],
        'CONFIG_PATH': r'${HOME}\config\config.ini'
    }

    @property
    def env_path(self) -> Path:
        return self.__env_data['HOME'] / 'env' / '.env'

    # 写入.env文件
    def write_env(self, **kwargs) -> None:
        """
        写入.env文件，且保留注释
        :param kwargs: 环境变量
        """
        try:
            if kwargs:
                env_data = [line for line in self.env_path.read_text(encoding='utf-8').split('\n') if line.strip()]
                for i, line in enumerate(env_data):
                    if not line.startswith('#'):
                        key, value = line.split('=')
                        if key in kwargs and value != kwargs[key]:
                            env_data[i] = f'{key}={kwargs[key]}'
                self.env_path.write_text('\n'.join(env_data), encoding='utf-8')
                debug_info = f'写入环境变量成功! {kwargs}'
                LogUtils().debug(debug_info)
        except Exception as e:
            error_log = f'写入环境变量失败! {e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)

    # 校验环境并加载
    def check_env(self) -> None:
        """
        校验是否存在required_env_vars环境变量是否存在，不存在则抛出异常
        校验env配置里面是否存在必要变量，且内容一致，否则创建或修改
        """
        try:
            required_env_vars = ['PUBLIC_DATA_PATH', 'CONFIG_PATH']
            env_path = self.env_path
            env_data = dotenv_values(dotenv_path=env_path)
            missing_env_vars = [var for var in required_env_vars if var not in env_data]
            if missing_env_vars:
                error_log = f'缺少必要环境变量{missing_env_vars}，立刻停止执行测试！'
                LogUtils().errors(error_log)
                raise Exception(error_log)
            # 检测必要环境变量，若不存在则添加，若存在但不一致则修改
            for k, v in self.__env_data.items():
                if k not in env_data or env_data[k] != v:
                    self.write_env(**{k: v})
            debug_info = f'检查环境变量完成!'
            LogUtils().debug(debug_info)
        except Exception as e:
            error_log = f'检查环境变量失败! {e}'
            LogUtils().errors(error_log)
            raise Exception(error_log)
