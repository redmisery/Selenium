import logging
import os
from pathlib import Path
from typing import List

from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.driver_finder import DriverFinder
from selenium.webdriver.common.options import ArgOptions, BaseOptions
from selenium.webdriver.common.selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)


class MySeleniumManager(SeleniumManager):
    def binary_paths(self, args: List) -> dict:
        args = [str(self._get_binary())] + args

        if logger.getEffectiveLevel() == logging.DEBUG:
            args.append("--debug")
        args.append("--language-binding")
        args.append("python")
        args.append("--output")
        args.append("json")

        env_vars = {
            "SE_BROWSER": "--browser",  # chrome, firefox, edge, iexplorer, safari
            "SE_DRIVER": "--driver",  # chromedriver, geckodriver, msedgedriver, IEDriverServer, or safaridriver
            "SE_BROWSER_VERSION": "--browser-version",  # 105, 106, etc
            "SE_DRIVER_VERSION": "--driver-version",  # e.g., 106.0.5249.61, 0.31.0, etc.
            "SE_BROWSER_PATH": "--browser-path",  # absolute path
            "SE_DRIVER_MIRROR_URL": "--driver-mirror-url",  # Mirror URL for driver repositories
            "SE_BROWSER_DOWNLOAD_URL": "--browser-download-url",  # URL to download the browser
            "SE_BROWSER_MIRROR_URL": "--browser-mirror-url",  # Mirror URL for browser repositories
            "SE_OUTPUT": "--output",
            # output type: LOGGER (using INFO, WARN, etc.), JSON (custom JSON notation), SHELL (Unix-like), or MIXED (INFO, WARN, DEBUG, etc. to stderr and minimal JSON to stdout). Default: LOGGER
            "SE_OS": "--os",  # os name: windows, linux, or mac
            "SE_ARCH": "--arch",  # architecture: x64, x86, arm, etc.
            "SE_PROXY": "--proxy",  # proxy server address
            "SE_TIMEOUT": "--timeout",  # timeout for network requests (in seconds). Default: 300
            "SE_OFFLINE": "--offline",  # whether to use the offline mode. Default: false
            "SE_FORCE_BROWSER_DOWNLOAD": "--force-browser-download",
            # whether to force the browser to download even if it is already downloaded. Default: false
            "SE_AVOID_BROWSER_DOWNLOAD": "--avoid-browser-download",  # whether to avoid downloading the browser if it is not found in the cache. Default: false
            "SE_DEBUG": "--debug",  # whether to enable debug mode. Default: true
            "SE_TRACE": "--trace",  # whether to enable trace mode. Default: false
            "SE_CACHE_PATH": "--cache-path",  # path to the cache directory. Default: ~/.cache/selenium
            "SE_TTL": "--ttl",  # time-to-live for the cache (in seconds). Default: 3600
            "SE_LANGUAGE_BINDING": "--language-binding",  # language binding: python, java, etc.
            "SE_AVOID_STATS": "--avoid-stats"  # Avoid sends usage statistics to plausible.io. Default: false
        }

        for env_var, cli_arg in env_vars.items():
            env_value = os.getenv(env_var)
            if env_value and cli_arg not in args:
                args.append(cli_arg)
                if cli_arg not in ["--offline", "--force-browser-download", "--avoid-browser-download", "--debug", "--trace", "--avoid-stats"]:
                    args.append(env_value)
        return self._run(args)


class MyDriverFinder(DriverFinder):
    def __init__(self, service: Service, options: BaseOptions) -> None:
        super().__init__(service, options)

    def _binary_paths(self) -> dict:
        if self._paths["driver_path"]:
            return self._paths

        browser = self._options.capabilities["browserName"]
        try:
            path = self._service.path
            if path:
                logger.debug(
                    "Skipping Selenium Manager; path to %s driver specified in Service class: %s", browser, path
                )
                if not Path(path).is_file():
                    raise ValueError(f"The path is not a valid file: {path}")
                self._paths["driver_path"] = path
            else:
                output = MySeleniumManager().binary_paths(self._to_args())
                if Path(output["driver_path"]).is_file():
                    self._paths["driver_path"] = output["driver_path"]
                else:
                    raise ValueError(f'The driver path is not a valid file: {output["driver_path"]}')
                if Path(output["browser_path"]).is_file():
                    self._paths["browser_path"] = output["browser_path"]
                else:
                    raise ValueError(f'The browser path is not a valid file: {output["browser_path"]}')
        except Exception as err:
            msg = f"Unable to obtain driver for {browser}"
            raise NoSuchDriverException(msg) from err
        return self._paths


class MyChromiumDriver(ChromiumDriver):
    """Controls the WebDriver instance of ChromiumDriver and allows you to
    drive the browser."""

    def __init__(
            self,
            browser_name: str = None,
            vendor_prefix: str = None,
            options: ArgOptions = ArgOptions(),
            service: Service = None,
            keep_alive: bool = True,
    ) -> None:
        """Creates a new WebDriver instance of the ChromiumDriver. Starts the
        service and then creates new WebDriver instance of ChromiumDriver.

        :Args:
         - browser_name - Browser name used when matching capabilities.
         - vendor_prefix - Company prefix to apply to vendor-specific WebDriver extension commands.
         - options - this takes an instance of ChromiumOptions
         - service - Service object for handling the browser driver if you need to pass extra details
         - keep_alive - Whether to configure ChromiumRemoteConnection to use HTTP keep-alive.
        """
        self.service = service

        finder = MyDriverFinder(self.service, options)
        if finder.get_browser_path():
            options.binary_location = finder.get_browser_path()
            options.browser_version = None

        self.service.path = self.service.env_path() or finder.get_driver_path()
        self.service.start()

        executor = ChromiumRemoteConnection(
            remote_server_addr=self.service.service_url,
            browser_name=browser_name,
            vendor_prefix=vendor_prefix,
            keep_alive=keep_alive,
            ignore_proxy=options._ignore_local_proxy,
        )

        try:
            # 调用父类的父类
            super(ChromiumDriver, self).__init__(command_executor=executor, options=options)
        except Exception:
            self.quit()
            raise

        self._is_remote = False


class WebDriver(MyChromiumDriver):
    """重写WebDrive类，使其使用chrome浏览器"""

    def __init__(
            self,
            options: Options = None,
            service: Service = None,
            keep_alive: bool = True,
    ) -> None:
        """Creates a new instance of the chrome driver. Starts the service and
        then creates new instance of chrome driver.

        :Args:
         - options - this takes an instance of ChromeOptions
         - service - Service object for handling the browser driver if you need to pass extra details
         - keep_alive - Whether to configure ChromeRemoteConnection to use HTTP keep-alive.
        """
        service = service if service else Service()
        options = options if options else Options()

        super().__init__(
            browser_name=DesiredCapabilities.CHROME["browserName"],
            vendor_prefix="goog",
            options=options,
            service=service,
            keep_alive=keep_alive,
        )
