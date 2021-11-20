# -*- coding: utf-8 -*-
"""
此模块提供实体和配置项模型。
"""
import abc
from datetime import datetime
from enum import Enum, Flag
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal

from mirai.models.base import MiraiBaseModel


class Entity(MiraiBaseModel):
    """实体，表示一个用户或群。"""
    id: int
    """QQ 号或群号。"""
    @abc.abstractmethod
    def get_avatar_url(self) -> str:
        """头像图片链接。"""

    @abc.abstractmethod
    def get_name(self) -> str:
        """名称。"""


class Friend(Entity):
    """好友。"""
    id: int
    """QQ 号。"""
    nickname: Optional[str]
    """昵称。"""
    remark: Optional[str]
    """备注。"""
    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'

    def get_name(self) -> str:
        return self.nickname or self.remark or ''


class Permission(str, Enum):
    """群成员身份权限。"""
    Member = "MEMBER"
    """成员。"""
    Administrator = "ADMINISTRATOR"
    """管理员。"""
    Owner = "OWNER"
    """群主。"""
    def __repr__(self) -> str:
        return repr(self.value)


class Group(Entity):
    """群。"""
    id: int
    """群号。"""
    name: str
    """群名称。"""
    permission: Permission
    """Bot 在群中的权限。"""
    def get_avatar_url(self) -> str:
        return f'https://p.qlogo.cn/gh/{self.id}/{self.id}/'

    def get_name(self) -> str:
        return self.name


class GroupMember(Entity):
    """群成员。"""
    id: int
    """QQ 号。"""
    member_name: str
    """群成员名称。"""
    permission: Permission
    """Bot 在群中的权限。"""
    group: Group
    """群。"""
    special_title: str = ''
    """群头衔。"""
    join_timestamp: datetime = datetime.utcfromtimestamp(0)
    """加入群的时间。"""
    last_speak_timestamp: datetime = datetime.utcfromtimestamp(0)
    """最后一次发言的时间。"""
    mute_time_remaining: int = 0
    """禁言剩余时间。"""
    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'

    def get_name(self) -> str:
        return self.member_name


class Client(Entity):
    """来自其他客户端的用户。"""
    id: int
    """识别 id。"""
    platform: str
    """来源平台。"""
    def get_avatar_url(self) -> str:
        raise NotImplementedError

    def get_name(self) -> str:
        return self.platform


class Subject(MiraiBaseModel):
    """另一种实体类型表示。"""
    id: int
    """QQ 号或群号。"""
    kind: Literal['Friend', 'Group', 'Stranger']
    """类型。"""


class Sex(str, Enum):
    """性别。"""
    Unknown = 'UNKNOWN'
    Male = 'MALE'
    Female = 'FEMALE'

    def __repr__(self) -> str:
        return repr(self.value)


class Profile(MiraiBaseModel):
    """用户资料。"""
    nickname: str
    """昵称。"""
    email: str
    """邮箱地址。"""
    age: int
    """年龄。"""
    level: int
    """QQ 等级。"""
    sign: str
    """个性签名。"""
    sex: Sex
    """性别。"""


class DownloadInfo(MiraiBaseModel):
    """文件的下载信息。"""
    sha1: str
    """文件的 SHA1。"""
    md5: str
    """文件的 MD5。"""
    url: str
    """文件的下载地址。"""
    downloadTimes: Optional[int]
    """文件被下载过的次数。"""
    uploaderId: Optional[int]
    """上传者的 QQ 号。"""
    uploadTime: Optional[datetime]
    """上传时间。"""
    lastModifyTime: Optional[datetime]
    """最后修改时间。"""


class FileProperties(MiraiBaseModel):
    """文件对象。"""
    name: str
    """文件名。"""
    id: Optional[str]
    """文件 ID。"""
    path: str
    """所在目录路径。"""
    parent: Optional['FileProperties'] = None
    """父文件对象，递归类型。None 为存在根目录。"""
    contact: Union[Group, Friend]
    """群信息或好友信息。"""
    is_file: bool
    """是否是文件。"""
    is_directory: bool
    """是否是文件夹。"""
    size: Optional[int] = None
    """文件大小。"""
    download_info: Optional[DownloadInfo] = None
    """文件的下载信息。"""


FileProperties.update_forward_refs()
class RespOperate(Flag):
    """事件响应操作。

    使用例：

    `RespOperate.ALLOW` 允许请求

    `RespOperate.DECLINE & RespOpearte.BAN` 拒绝并拉黑
    """
    ALLOW = 1
    """允许请求。"""
    DECLINE = 2
    """拒绝请求。"""
    IGNORE = 3
    """忽略请求。"""
    BAN = 4
    """拉黑。与前三个选项组合。"""

class Config(MiraiBaseModel):
    """配置项类型。"""
    def modify(self, **kwargs) -> 'Config':
        """修改部分设置。"""
        for k, v in kwargs.items():
            if k in self.__fields__:
                setattr(self, k, v)
            else:
                raise ValueError(f'未知配置项: {k}')
        return self


class GroupConfigModel(Config):
    """群配置。"""
    name: str
    """群名称。"""
    confess_talk: bool
    """是否允许坦白说。"""
    allow_member_invite: bool
    """是否允许成员邀请好友入群。"""
    auto_approve: bool
    """是否开启自动审批入群。"""
    anonymous_chat: bool
    """是否开启匿名聊天。"""
    announcement: str = ''
    """群公告。"""


class MemberInfoModel(Config, GroupMember):
    """群成员信息。"""


__all__ = [
    'Entity',
    'Friend',
    'Group',
    'GroupMember',
    'Permission',
    'Sender',
    'Subject',
    'Config',
    'GroupConfigModel',
    'MemberInfoModel',
]
