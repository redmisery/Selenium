import json
import traceback
import allure

from common.log import LogUtils


class AllureLog:
    @staticmethod
    def allure_log(req_data, res):
        """
        日志步骤描述
        日志包含：title、decription、level、url、method、params、response、status_code、request_data

        :param req_data: 请求数据
        :param res: 返回结果
        :return:
        """
        try:
            # 标题
            title = req_data['kwargs']['title']
            # 描述
            decription = req_data['kwargs']['description']
            # 优先级
            level = getattr(allure.severity_level, req_data['level'])
            # 请求地址
            url = res.url
            # 请求方法
            method = req_data['kwargs']['request']['method']
            # 请求参数
            params = None
            body = None
            if 'params' in req_data['kwargs']['request'].keys():
                params = req_data['kwargs']['request']['params']
            if 'body' in req_data['kwargs']['request'].keys():
                body = req_data['kwargs']['request']['body']
            data = {"params": params, "body": body}
            data = json.dumps(data, ensure_ascii=False, indent=4)
            # 响应数据
            try:
                res_content = res.json()
            except Exception:
                res_content = res.text
            if res.status_code == 302:
                res_content = "重定向网址：" + res.headers['Location']
            response_data = json.dumps(res_content, ensure_ascii=False, indent=4)
            # 响应状态码
            response_status_code = str(res.status_code)
            # 请求完整参数
            request_data = json.dumps(req_data, ensure_ascii=False, indent=4)

            # --------------------allure报告-------------------------
            allure.dynamic.title(title)
            allure.dynamic.description(decription)
            allure.dynamic.severity(level)
            allure.attach(body=url, name="请求地址", attachment_type=allure.attachment_type.TEXT)
            allure.attach(body=method, name="请求方法", attachment_type=allure.attachment_type.TEXT)
            allure.attach(body=data, name="请求数据", attachment_type=allure.attachment_type.TEXT)
            allure.attach(body=response_data, name="响应数据", attachment_type=allure.attachment_type.TEXT)
            allure.attach(body=response_status_code, name="响应状态码", attachment_type=allure.attachment_type.TEXT)
            allure.attach(body=request_data, name="请求完整参数", attachment_type=allure.attachment_type.TEXT)

            # -------------------日志报告------------------
            LogUtils().info("请求接口:" + url)
            LogUtils().info("请求数据：\n" + data)
            LogUtils().info("响应状态码:" + response_status_code)
            LogUtils().info("响应结果：\n" + response_data)
        except KeyError:
            LogUtils().error("allure log日志打印异常：%s" % traceback)
