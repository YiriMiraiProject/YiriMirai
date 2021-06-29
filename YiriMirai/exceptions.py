
class ApiError(Exception):
    '''
    调用 API 出错。

    `code: int` mirai-api-http 的 API 状态码
    '''
    def __init__(self, code: int):
        self.code = code

class LoginError(ApiError):
    pass
