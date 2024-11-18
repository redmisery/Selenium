import traceback
import zipfile
from pathlib import Path
from typing import Optional

import requests
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.download_manager import DownloadManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.os_manager import OperationSystemManager, ChromeType
from webdriver_manager.drivers.chrome import ChromeDriver

from common import LogUtils

"""
Author: 韩琰
Date: 2024年11月18日
Version: 1.0
Description: Chrome驱动自动更新，4.26.1后，会自动获取最新驱动，无需手动更新，在此本功能废弃
"""

class ChromeDriverUpdate(ChromeDriverManager):
    """
    自定义驱动自动更新版本
    :param update_path:绝对下载路径
    :param driver_version:驱动版本
    :param name:驱动名称
    :param chrome_type:浏览器类型
    :param url:驱动下载地址
    :param latest_release_url:驱动最新版本地址
    :param download_manager:下载管理器
    :param cache_manager:缓存管理器
    :param os_system_manager:操作系统管理器
    """

    def __init__(
            self,
            update_path: str = None,
            driver_version: Optional[str] = None,
            name: str = "chromedriver",
            chrome_type: str = ChromeType.GOOGLE,
            url: str = "https://registry.npmmirror.com/-/binary/chrome-for-testing/",
            # latest_release_url已废弃
            latest_release_url: str = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
            download_manager: Optional[DownloadManager] = None,
            cache_manager: Optional[DriverCacheManager] = None,
            os_system_manager: Optional[OperationSystemManager] = None,
    ):
        super().__init__(
            download_manager=download_manager,
            cache_manager=cache_manager,
            os_system_manager=os_system_manager
        )

        self.driver = ChromeDriver(
            name=name,
            driver_version=driver_version,
            chrome_type=chrome_type,
            url=url,
            latest_release_url=latest_release_url,
            http_client=self.http_client,
            os_system_manager=os_system_manager
        )
        self.url = url
        self.update_dir = update_path
        self.update_version = None
        self.dirver_version = None
        self.driver_path = None

    def __get_download_dir(self) -> Path:
        """
        获取默认下载保存路径
        :return: 路径
        """
        if self.update_dir is None:
            user_home = Path.home()
            driver_home = user_home / '.wdm/drivers/chromedriver' / self.get_os_type()
            driver_home.mkdir(parents=True, exist_ok=True)
            return driver_home
        else:
            self.update_dir = Path(self.update_dir).resolve()
            Path(self.update_dir).mkdir(parents=True, exist_ok=True)
            return self.update_dir

    def __get_current_version(self) -> str:
        """
        获取当前Chrome浏览器版本
        :return: str:版本号
        """
        # 需要使用cmd命令，该函数花费时间较长，尽量少调用
        try:
            if self.dirver_version is None:
                browser_type = self.driver.get_browser_type()
                dirver_version = OperationSystemManager().get_browser_version_from_os(browser_type)
                self.dirver_version = dirver_version
            return self.dirver_version
        except Exception as e:
            error_log = f'未获取到浏览器版本！{e} {traceback.format_exc()}'
            LogUtils().error(error_log)
            raise error_log

    @staticmethod
    def __compare_version(version1: str, version2: str) -> bool:
        """
        比较版本号大小
        :param version1:
        :param version2:
        :return:
        """
        version1 = version1.replace('.', '')
        version2 = version2.replace('.', '')
        max_length = max(len(version1), len(version2))
        version1_num = int(version1 + '0' * (max_length - len(version1)))
        version2_num = int(version2 + '0' * (max_length - len(version2)))
        return version1_num >= version2_num

    def __needUpdate(self) -> bool:
        """
        判断是否需要更新,比对当前浏览器版本和驱动器版本，若驱动器最新版本>=当前浏览器版本，则不需要更新
        :return:
        """
        is_need = True
        browser_version = self.__get_current_version()
        # 若update_path指定了路径，则使用指定路径，否则使用默认路径
        self.update_dir = self.__get_download_dir()
        driver_dir = self.update_dir
        # 如果dirver_path目录存在且目录不为空
        if driver_dir.exists() and len(list(driver_dir.iterdir())) > 0:
            files = [file for file in driver_dir.iterdir() if file.is_dir()]
            # 若版本文件夹为空，则直接返回True
            if len(files) != 0:
                files.sort(key=lambda file: file.stat().st_mtime, reverse=True)
                latest_driver_version = str(files[0].name)
                # 若latest_driver_version>=browser_version，则不需要更新
                if self.__compare_version(latest_driver_version, browser_version):
                    # 检测是否存在chromedirver.exe
                    file_path = driver_dir / latest_driver_version / 'chromedriver.exe'
                    self.driver_path = file_path
                    if file_path.exists():
                        is_need = False
                        debug_log = f'当前版本：{browser_version},不需要更新'
                        LogUtils().debug(debug_log)
                    else:
                        debug_log = f'当前版本：{browser_version},不需要更新，但是chromedriver.exe不存在,路径：{file_path}'
                        LogUtils().debug(debug_log)
                else:
                    debug_log = f'当前版本：{browser_version},需要更新'
                    LogUtils().debug(debug_log)
        return is_need

    def __get_file_url(self) -> str:
        """
        获取ChromeDriver下载地址
        :return: url
        """
        response = requests.get(self.url)
        response_code = response.status_code
        response_content = response.json()
        browser_version = self.__get_current_version()
        version_url = None
        if response_code == 200 and response_content and type(response_content) == list:
            current_version = browser_version.replace('.', '')
            for item in response_content:
                if self.__compare_version(item['name'][0:-1], current_version):
                    self.update_version = item['name'][0:-1]
                    version_url = item['url']
                    break
            if version_url is None:
                # 遍历所有版本后，仍然没有合适的版本
                error_log = f'当前版本：{browser_version},没有找到合适的版本，请手动下载!'
                LogUtils().error(error_log)
                raise Exception(error_log)
        else:
            # 请求失败
            error_log = f'请求失败，请求地址：{self.url}'
            LogUtils().error(error_log)
            raise Exception(error_log)

        os_type = self.get_os_type()
        response = requests.get(version_url)
        response_code = response.status_code
        response_content = response.json()
        file_url = None

        if response_code == 200 and response_content and type(response_content) == list:
            for item in response_content:
                if item['name'][0:-1] == os_type:
                    file_url = item['url']
                    break
            if file_url is None:
                # 遍历所有系统后，仍然没有合适的版本
                error_log = f'当前版本：{browser_version}没有找到合适{os_type}的版本，请手动下载!'
                LogUtils().error(error_log)
                raise Exception(error_log)
            else:
                return file_url
        else:
            error_log = f'请求失败，请求地址：{version_url}'
            LogUtils().error(error_log)
            raise Exception(error_log)

    def __download(self, file_url, path) -> str:
        download_url = None
        response = requests.get(file_url)
        response_code = response.status_code
        response_content = response.json()
        if response_code == 200 and response_content and type(response_content) == list:
            for item in response_content:
                if 'chromedriver' in item['name']:
                    download_url = item['url']
                    break
            if download_url is None:
                # 遍历所有系统后，仍然没有合适的版本
                error_log = f'当前url：{file_url}没有找到chromedriver，请手动下载!'
                LogUtils().error(error_log)
                raise Exception(error_log)
        else:
            error_log = f'请求失败，请求地址：{file_url}'
            LogUtils().error(error_log)
            raise Exception(error_log)

        response = requests.get(download_url)
        file_path = Path(path) / self.update_version / f'chromedriver-{self.get_os_type()}.zip'
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if response.status_code == 200:
            try:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                    # 下载完后开始解压
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # 验证是否损坏
                    zip_file.testzip()
                    zip_dist_file = f'chromedriver-{self.get_os_type()}/chromedriver.exe'
                    zip_file.extract(zip_dist_file, file_path.parent)
                driver_path = file_path.parent / zip_dist_file
                dist_path = file_path.parent / 'chromedriver.exe'
                driver_path.replace(dist_path)
                driver_path.parent.rmdir()
                driver_path = dist_path
                # 解压完后删除源文件
                file_path.unlink()
                debug_log = f'{file_url}驱动下载成功，下载地址：{driver_path}'
                LogUtils().debug(debug_log)
                return driver_path
            except Exception as e:
                Path(file_path).unlink(missing_ok=True)
                error_log = f'{file_url}请求成功，下载失败，下载地址:{file_path} ,失败详情：{e} {traceback.format_exc()}'
                LogUtils().error(error_log)
                raise e
        else:
            Path(file_path).rmdir()
            error_log = f'{file_url}请求失败，响应代码：{response.status_code}'
            LogUtils().error(error_log)
            raise error_log

    def install(self) -> str:
        """
        更新ChromeDriver版本，若当前版本>=浏览器版本，则返回驱动路径，否则更新驱动再返回更新后的驱动路径
        :return: driver_path
        """
        if self.__needUpdate():
            url = self.__get_file_url()
            download_path = self.__get_download_dir()
            driver_path = self.__download(url, download_path)
            return driver_path
        else:
            return self.driver_path
