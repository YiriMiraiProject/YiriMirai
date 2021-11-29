# -*- coding: utf-8 -*-
"""
此模块提供异常相关。
"""
import re
import traceback

from pydantic import ValidationError


class NetworkError(RuntimeError):
    """网络连接出错。"""


API_ERROR_FMT = {
    0: '正常。',
    1: 'Verify Key 错误。',
    2: '指定的 Bot 不存在。',
    3: 'Session 失效或不存在。',
    4: 'Session 未认证或未激活。',
    5: '发送消息目标不存在，或指定对象不存在。',
    6: '指定文件不存在。',
    10: 'Bot 无对应操作的权限。',
    20: 'Bot 被禁言。',
    30: '消息过长。',
    400: '参数错误。',
    500: 'mirai 内部错误。',
}


class ApiError(RuntimeError):
    """调用 API 出错。"""
    def __init__(self, response: dict):
        """
        Args:
            response(`dict`): mirai-api-http 的 API 返回结果。
        """
        code = response['code']
        self.code = code
        self.args = (
            code, f'[ERROR {code}]' + API_ERROR_FMT.get(code, ''),
            response.get('msg', '')
        )


class StopPropagation(Exception):
    """终止事件处理器执行，并停止事件向上传播。"""


class StopExecution(Exception):
    """终止事件处理器执行，但不阻止事件向上传播。"""


class SkipExecution(Exception):
    """跳过同优先度的事件处理器，进入下一优先度。"""


class ApiParametersError(TypeError):
    """API 参数错误。"""
    def __init__(self, err: ValidationError):
        """
        Args:
            err(`str`): pydantic 的解析错误。
        """
        self._err = err
        try:
            errors = [f'在调用 `{err.model.Info.alias}` 时出错。']
            for error in self._err.errors():
                parameter_name = error['loc'][0]
                parameter_name = re.sub(
                    r'[A-Z]', lambda m: '_' + m.group(0).lower(),
                    parameter_name
                )
                message = error['msg']
                errors.append(f'参数 `{parameter_name}` 类型错误，原因：{message}')
            self.args = tuple(errors)
        except TypeError:
            self.args = (err.json(), )


def print_exception(e: Exception):
    """打印异常信息。"""
    traceback.print_exception(type(e), e, e.__traceback__)


__all__ = [
    'NetworkError', 'ApiError', 'StopPropagation', 'StopExecution',
    'SkipExecution', 'print_exception'
]
