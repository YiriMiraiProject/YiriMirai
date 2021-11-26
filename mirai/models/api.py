# -*- coding: utf-8 -*-
"""
此模块提供 API 调用与返回数据解析相关。
"""
import logging
from typing import Any, Generic, List, Optional, Type, TypeVar, Union, cast

from pydantic import ValidationError

from mirai.api_provider import ApiProvider, Method
from mirai.exceptions import ApiParametersError
from mirai.models.base import (
    MiraiBaseModel, MiraiIndexedMetaclass, MiraiIndexedModel
)

logger = logging.getLogger(__name__)


class ApiResponse(MiraiBaseModel):
    """响应对象。"""
    code: int
    """状态码。"""
    msg: str
    """消息。"""
    data: Optional[Any] = None
    """返回数据。"""
    @classmethod
    def parse_obj(cls, obj: dict) -> 'ApiResponse':
        """将字典解析为对应的响应对象，对于无 code 和 msg 的响应，自动处理为 data 部分。

        Args:
            obj: 一个字典，包含了响应对象的属性。
        """
        if 'code' in obj and 'msg' in obj:
            return super().parse_obj(obj)
        return super().parse_obj({'code': 0, 'msg': '', 'data': obj})

    def __getattr__(self, item):
        return getattr(self.data, item)

    def __iter__(self):
        return iter(self.data or [])

    def __getitem__(self, item):
        return self.data and self.data[item]


class ApiMetaclass(MiraiIndexedMetaclass):
    """API 模型的元类。"""
    __apimodel__ = None

    class ApiInfo():
        """API 的信息。"""
        name = ""
        alias = ""
        parameter_names: List[str] = []

    Info: Type[ApiInfo]

    def __new__(cls, name, bases, attrs, **kwargs):
        new_cls: ApiMetaclass = cast(
            ApiMetaclass,
            super().__new__(cls, name, bases, attrs, **kwargs)
        )

        if name == 'ApiModel':
            cls.__apimodel__ = new_cls
            new_cls.__indexes__ = {}
            return new_cls

        if not cls.__apimodel__:  # ApiBaseModel 构造时，ApiModel 还未构造
            return new_cls

        for base in bases:
            if issubclass(base, cls.__apimodel__):
                info = new_cls.Info
                if hasattr(info, 'name') and info.name:
                    base.__indexes__[info.name] = new_cls
                if hasattr(info, 'alias') and info.alias:
                    base.__indexes__[info.alias] = new_cls

                # 获取 API 参数名
                if hasattr(new_cls, '__fields__'):
                    info.parameter_names = list(new_cls.__fields__)
                else:
                    info.parameter_names = []
                break

        return new_cls

    def get_subtype(cls, name: str) -> 'ApiMetaclass':
        try:
            return cast(ApiMetaclass, super().get_subtype(name))
        except ValueError as e:
            raise ValueError(f'`{name}` 不是可用的 API！') from e


class ApiBaseModel(MiraiIndexedModel, metaclass=ApiMetaclass):
    """API 模型基类。

    直接继承此类，不会被 ApiMetaclass 索引，也不会引起 metaclass 冲突。
    用于实现 API 类型之间的方法复用。
    """


TModel = TypeVar('TModel', bound=MiraiBaseModel)


class ApiModel(ApiBaseModel):
    """API 模型。"""
    class Info(ApiMetaclass.ApiInfo):
        """API 的信息。"""
        name = ""
        alias = ""
        parameter_names: List[str] = []

    Response = ApiResponse

    def __init__(self, *args, **kwargs):
        # 解析参数列表，将位置参数转化为具名参数
        parameter_names = self.Info.parameter_names
        if len(args) > len(parameter_names):
            raise TypeError(
                f'`{self.Info.alias}` 需要{len(parameter_names)}个参数，' +
                '但传入了{len(args)}个。'
            )
        for name, value in zip(parameter_names, args):
            if name in kwargs:
                raise TypeError(
                    f'在 `{self.Info.alias}` 中，具名参数 `{name}` 与位置参数重复。'
                )
            kwargs[name] = value

        super().__init__(**kwargs)

    async def _call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
    ):
        return await api_provider.call_api(
            api=self.Info.name,
            method=method,
            **self.dict(by_alias=True, exclude_none=True)
        )

    async def call(
        self,
        api_provider: ApiProvider,
        method: Method = Method.GET,
        response_type: Optional[Type[ApiResponse]] = None,
    ):
        """调用 API。"""
        logger.debug(f'调用 API：{repr(self)}')
        raw_response = await self._call(api_provider, method)

        # 如果 API 无法调用，raw_response 为空
        if not raw_response:
            return None
        # 解析 API 返回数据
        response_type = response_type or self.Response
        return response_type.parse_obj(raw_response).data

    class Proxy(Generic[TModel]):
        """API 代理类。由 API 构造，提供对适配器的访问。

        Proxy: 提供更加简便的调用 API 的写法。`Proxy` 对象一般由 `Mirai.__getattr__` 获得，
        这个方法依托于 `MiraiIndexedModel` 的子类获取机制，支持按照命名规范转写的 API，
        所有的 API 全部使用小写字母及下划线命名。

        对于 GET 方法的 API，可以使用 `get` 方法：
        ```py
        profile = await bot.friend_profile.get(12345678)
        ```

        或者直接调用：
        ```py
        profile = await bot.friend_profile(12345678)
        ```

        对于 POST 方法的 API，推荐直接调用：
        ```
        await bot.send_friend_message(12345678, [Plain('Hello World!')])
        ```

        `set` 方法也可用，但由于语义不准确，不推荐使用。

        对于 RESTful 的 API，首先应直接调用，传入基本参数，然后使用 `get` 或 `set`：
        ```py
        config = await bot.group_config(12345678).get()
        await bot.group_config(12345678).set(config.modify(announcement='测试'))
        ```

        `ApiProxy` 同时提供位置参数支持。比如上面的例子中，没有使用具名参数，而是使用位置参数，
        这可以让 API 调用更简洁。参数的顺序可参照 mirai-api-http
        的[文档](https://project-mirai.github.io/mirai-api-http/api/API.html)。
        除去`sessionKey`由适配器自动指定外，其余参数可按顺序传入。具名参数仍然可用，适当地使用具名参数可增强代码的可读性。
        """
        def __init__(
            self, api_provider: ApiProvider, api_type: Type['ApiModel']
        ):
            self.api_provider = api_provider
            self.api_type = api_type

        async def _call_api(
            self,
            method: Method = Method.GET,
            response_type: Optional[Type[ApiResponse]] = None,
            args: Union[list, tuple, None] = None,
            kwargs: Optional[dict] = None
        ):
            """调用 API。

            将结果解析为 Model。
            """
            args = args or []
            kwargs = kwargs or {}
            try:
                api = self.api_type(*args, **kwargs)
                return await api.call(self.api_provider, method, response_type)
            except ValidationError as e:
                raise ApiParametersError(e) from None

        async def get(self, *args, **kwargs) -> Optional[TModel]:
            """获取。对于 GET 方法的 API，调用此方法。"""
            return await self._call_api(
                method=Method.GET, args=args, kwargs=kwargs
            )

        async def set(self, *args, **kwargs) -> Optional[TModel]:
            """设置。对于 POST 方法的 API，可调用此方法。"""
            return await self._call_api(
                method=Method.POST, args=args, kwargs=kwargs
            )

        async def __call__(self, *args, **kwargs):
            return await self.get(*args, **kwargs)


class ApiGet(ApiModel):
    class Proxy(ApiModel.Proxy[TModel]):
        async def set(self, *args, **kwargs):
            """GET 方法的 API 不具有 `set`。

            调用此方法会报错 `TypeError`。
            """
            raise TypeError(f'`{self.api_type.Info.alias}` 不支持 `set` 方法。')

        async def __call__(self, *args, **kwargs) -> Optional[TModel]:
            return await self.get(*args, **kwargs)


class ApiPost(ApiModel):
    class Proxy(ApiModel.Proxy[TModel]):
        """POST 方法的 API 代理对象。"""
        async def get(self, *args, **kwargs):
            """POST 方法的 API 不具有 `get`。

            调用此方法会报错 `TypeError`。
            """
            raise TypeError(f'`{self.api_type.Info.alias}` 不支持 `get` 方法。')

        async def __call__(self, *args, **kwargs) -> Optional[TModel]:
            return await self.set(*args, **kwargs)


TModel_ = TypeVar('TModel_', bound=MiraiBaseModel)


class ApiRest(ApiModel):
    class Info(ApiModel.Info):
        """API 的信息。"""
        name = ""
        alias = ""
        method = Method.GET

    PostResponse = ApiResponse

    class Proxy(ApiModel.Proxy[TModel]):
        """RESTful 的 API 代理对象。

        直接调用时，传入 GET 和 POST 的公共参数，返回一个 `ApiRest.Proxy.Partial` 对象，
        由此对象提供实际调用支持。
        """
        def __call__(self, *args, **kwargs) -> 'ApiRest.Proxy.Partial':
            return ApiRest.Proxy.Partial(
                self.api_provider, cast(Type['ApiRest'], self.api_type), args,
                kwargs
            )

        class Partial(ApiModel.Proxy[TModel_]):
            """RESTful 的 API 代理对象（已传入公共参数）。"""
            api_type: Type['ApiRest']

            def __init__(
                self, api_provider: ApiProvider, api_type: Type['ApiRest'],
                partial_args: Union[list, tuple], partial_kwargs: dict
            ):
                super().__init__(api_provider=api_provider, api_type=api_type)
                self.partial_args = partial_args
                self.partial_kwargs = partial_kwargs

            async def get(self, *args, **kwargs) -> Optional[TModel_]:
                """获取。"""
                return await self._call_api(
                    method=Method.RESTGET,
                    args=[*self.partial_args, *args],
                    kwargs={
                        **self.partial_kwargs,
                        **kwargs
                    }
                )

            async def set(self, *args, **kwargs) -> Optional[TModel_]:
                """设置。"""
                return await self._call_api(
                    method=Method.RESTPOST,
                    response_type=self.api_type.PostResponse,
                    args=[*self.partial_args, *args],
                    kwargs={
                        **self.partial_kwargs,
                        **kwargs
                    }
                )


__all__ = [
    'ApiBaseModel',
    'ApiGet',
    'ApiMetaclass',
    'ApiModel',
    'ApiPost',
    'ApiProvider',
    'ApiRest',
    'ApiResponse',
]

from mirai.models.api_impl import *
