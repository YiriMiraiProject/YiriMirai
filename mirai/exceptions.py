# -*- coding: utf-8 -*-
"""
此模块提供异常相关。
"""
import traceback


class NetworkError(RuntimeError):
    """网络连接出错。
    """
    pass


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
}


class ApiError(RuntimeError):
    """调用 API 出错。

    `code: int` mirai-api-http 的 API 状态码。
    """
    def __init__(self, code: int):
        self.code = code
        self.args = (code, f'[ERROR {code}]' + API_ERROR_FMT[code])


class LoginError(ApiError):
    """登陆出错。
    """
    pass


def print_exception(e: Exception):
    """打印异常信息。
    """
    traceback.print_exception(type(e), e, e.__traceback__)


__all__ = ['NetworkError', 'ApiError', 'LoginError', 'print_exception']
