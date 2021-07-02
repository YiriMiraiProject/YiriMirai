# -*- coding: utf-8 -*-
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from YiriMirai.adapters.base import Api, Method
from YiriMirai.models.base import MiraiBaseModel
from YiriMirai.models.entities import Friend, Group, GroupMember, GroupConfig, MemberInfo
from YiriMirai.models.events import MessageEvent
from YiriMirai.models.message import Image, Voice
from YiriMirai.utils import async_


class Response(MiraiBaseModel):
    '''响应对象。'''
    code: int
    msg: str


class About(Response):
    '''插件信息。'''
    data: dict


class MessageFromId(Response):
    data: MessageEvent


class FriendList(Response):
    '''好友列表。'''
    data: List[Friend]

    def __iter__(self):
        yield from self.data


class GroupList(Response):
    '''群组列表。'''
    data: List[Group]

    def __iter__(self):
        yield from self.data


class MemberList(Response):
    '''群成员列表。'''
    data: List[GroupMember]

    def __iter__(self):
        yield from self.data


class Sex(str, Enum):
    Unknown = 'UNKNOWN'
    Male = 'MALE'
    Female = 'FEMALE'


class Profile(MiraiBaseModel):
    '''好友资料。'''
    nickname: str
    email: str
    age: int
    level: int
    sign: str
    sex: Sex


class MessageResponse(Response):
    '''发送消息响应。'''
    message_id: int = Field(..., alias='messageId')


class File(MiraiBaseModel):
    '''文件对象。'''
    name: str
    id: str
    path: str
    parent: Optional['File'] = None
    contact: Union[Group, Friend]
    is_file: bool = Field(..., alias='isFile')
    is_directory: bool = Field(..., alias='isDirectory')


class FileList(Response):
    '''文件列表。'''
    data: List[File]

    def __iter__(self):
        yield from self.data


class FileInfo(Response):
    '''文件信息。'''
    data: File


class FileMkdir(Response):
    '''创建文件夹响应。'''
    data: File


AVAIABLE_API = {
    "about": ("about", Method.GET, [], About),
    "message_from_id": ("messageFromId", Method.GET, [], MessageFromId),
    "friend_list": ("friendList", Method.GET, [], FriendList),
    "group_list": ("groupList", Method.GET, [], GroupList),
    "member_list": ("memberList", Method.GET, ['target'], MemberList),
    "bot_profile": ("botProfile", Method.GET, [], Profile),
    "friend_profile": ("friendProfile", Method.GET, ['target'], Profile),
    "member_profile":
        ("memberProfile", Method.GET, ['target', 'memberId'], Profile),
    "send_friend_message":
        (
            "sendFriendMessage", Method.POST, ['target',
                                               'messageChain'], MessageResponse
        ),
    "send_group_message":
        (
            "sendGroupMessage", Method.POST, ['target',
                                              'messageChain'], MessageResponse
        ),
    "send_temp_message":
        (
            "sendTempMessage", Method.POST, ['qq', 'group',
                                             'messageChain'], MessageResponse
        ),
    "send_nudge":
        ("sendNudge", Method.POST, ['target', 'subject', 'kind'], Response),
    "recall": ("recall", Method.POST, ['target'], Response),
    "file_list":
        ("file/list", Method.GET, ['id', 'target', 'group', 'qq'], FileList),
    "file_info":
        ("file/info", Method.GET, ['id', 'target', 'group', 'qq'], FileInfo),
    "file_mkdir":
        (
            "file/mkdir", Method.POST,
            ['id', 'target', 'group', 'qq', 'dictionaryName'], FileMkdir
        ),
    "file_delete":
        (
            "file/delete", Method.POST, ['id', 'target', 'group',
                                         'qq'], Response
        ),
    "file_move":
        (
            "file/move", Method.POST,
            ['id', 'target', 'group', 'qq', 'moveTo'], Response
        ),
    "file_rename":
        (
            "file/rename", Method.POST,
            ['id', 'target', 'group', 'qq', 'renameTo'], Response
        ),
    "upload_image": ("uploadImage", Method.GET, [], Image),
    "upload_voice": ("uploadVoice", Method.GET, [], Voice),
    "delete_friend": ("deleteFriend", Method.POST, ['target'], Response),
    "mute": ("mute", Method.POST, ['target', 'memderId', 'time'], Response),
    "unmute": ("unmute", Method.POST, ['target', 'memderId'], Response),
    "kick": ("kick", Method.POST, ['target', 'memderId', 'msg'], Response),
    "quit": ("quit", Method.POST, ['target'], Response),
    "mute_all": ("muteAll", Method.POST, ['target'], Response),
    "unmute_all": ("unmuteAll", Method.POST, ['target'], Response),
    "set_essence": ("setEssence", Method.POST, ['target'], Response),
    "group_config":
        ("groupConfig", Method.REST, ['target', 'config'], GroupConfig),
    "member_info":
        (
            "memberInfo", Method.REST, ['target', 'memberId',
                                        'info'], MemberInfo
        ),
    "resp_new_friend_request_event":
        (
            "resp/newFriendRequestEvent", Method.POST,
            ['eventId', 'fromId', 'groupId', 'operate',
             'message'], MiraiBaseModel
        ),
    "resp_member_join_request_event":
        (
            "resp/memberJoinRequestEvent", Method.POST,
            ['eventId', 'fromId', 'groupId', 'operate',
             'message'], MiraiBaseModel
        ),
    "resp_bot_invited_join_group_request_event":
        (
            "resp/botInvitedJoinGroupRequestEvent", Method.POST,
            ['eventId', 'fromId', 'groupId', 'operate',
             'message'], MiraiBaseModel
        ),
    "cmd_execute": ("cmd/execute", Method.POST, ['command'], Response),
    "cmd_register":
        (
            "cmd/register", Method.POST,
            ['name', 'alias', 'usage', 'description'], Response
        )
}

AVAIABLE_API_ALIAS = {value[0]: key for key, value in AVAIABLE_API.items()}


def encode_model(model):
    '''将含有`BaseModel`的对象编码为`dict`。'''
    if isinstance(model, BaseModel):
        return model.dict()
    elif isinstance(model, list):
        return [encode_model(node) for node in model]
    else:
        return model


class ApiProxy(object):
    '''api代理类。由 api 访问 adapter。'''
    def __init__(self, command: str, api_provider: Api):
        '''api代理类。由 api 访问 adapter。
        此构造函数不应被使用，改为`ApiProxy.analyze`以获取正确的子类。

        `command: str` Api 名称。
        `api_provider: Api` 提供实际访问的接口。
        '''
        self.command = command
        self.host, _, self.parameter_names, self.model = AVAIABLE_API[command]
        self.api_provider = api_provider

    async def _call_api(self, model: MiraiBaseModel = None, **kwargs):
        '''调用 api。
        将结果解析为 Model。
        '''
        raw_response = await async_(
            self.api_provider.call_api(api=self.host, **kwargs)
        )
        model = model or self.model
        return model.parse_obj(raw_response)

    async def get(self, *args, **kwargs) -> MiraiBaseModel:
        kwargs = self.parameters_to_dict(*args, **kwargs)
        return await self._call_api(method=Method.GET, **kwargs)

    async def set(self, *args, **kwargs) -> MiraiBaseModel:
        kwargs = self.parameters_to_dict(*args, **kwargs)
        return await self._call_api(method=Method.POST, **kwargs)

    async def __call__(self, *args, **kwargs) -> MiraiBaseModel:
        return await self.get(*args, **kwargs)

    def parameters_to_dict(self, *args, **kwargs) -> dict:
        '''将参数列表解析为字典。'''
        if len(args) > len(self.parameter_names):
            raise TypeError(
                f'`{self.command}`需要{len(self.parameter_names)}个参数，但传入了{len(args)}个。'
            )
        for name, value in zip(self.parameter_names, args):
            if kwargs.get(name):
                raise TypeError(f'在`{self.command}`中，具名参数`{name}`与位置参数重复。')
            else:
                kwargs[name] = value

        return {name: encode_model(value) for name, value in kwargs.items()}

    @staticmethod
    def analyze(api: str, api_provider: Api) -> 'ApiProxy':
        '''分析 api，返回对应的代理对象。'''
        api = AVAIABLE_API_ALIAS.get(api) or api
        try:
            method = AVAIABLE_API[api][1]
            return PROXIES[method](api, api_provider)
        except KeyError as e:
            raise ValueError(f'`{api}`不是可用的 api。') from e


class ApiProxyGet(ApiProxy):
    async def set(self, *args, **kwargs):
        raise TypeError(f'`{self.command}`不支持`set`方法。')


class ApiProxyPost(ApiProxy):
    async def get(self, *args, **kwargs):
        raise TypeError(f'`{self.command}`不支持`get`方法。')

    async def __call__(self, *args, **kwargs):
        return await self.set(*args, **kwargs)


class ApiProxyRestPartial(ApiProxy):
    def __init__(
        self, command: str, api_provider: Api, partial_args: list,
        partial_kwargs: dict
    ):
        super().__init__(command=command, api_provider=api_provider)
        self.partial_args = partial_args
        self.partial_kwargs = partial_kwargs

    async def get(self, *args, **kwargs) -> MiraiBaseModel:
        return await super().get(
            *self.partial_args, *args, **self.partial_kwargs, **kwargs
        )

    async def set(self, *args, **kwargs) -> MiraiBaseModel:
        kwargs = self.parameters_to_dict(
            *self.partial_args, *args, **self.partial_kwargs, **kwargs
        )
        return await self._call_api(
            method=Method.POST, model=Response, **kwargs
        )


class ApiProxyRest(ApiProxy):
    def __call__(self, *args, **kwargs) -> ApiProxyRestPartial:
        return ApiProxyRestPartial(
            self.command, self.api_provider, args, kwargs
        )


PROXIES = {
    'GET': ApiProxyGet,
    'POST': ApiProxyPost,
    'REST': ApiProxyRest,
}
