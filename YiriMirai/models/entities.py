import abc
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Entity(BaseModel):
    '''实体，表示一个用户或群。'''
    def __repr__(self):
        return f'<{self.__class__.__name__} {str(self)}>'

    @abc.abstractmethod
    def get_avatar_url(self) -> str:
        pass


class Friend(Entity):
    '''好友。'''
    id: int
    nickname: Optional[str]
    remark: Optional[str]

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class Permission(Enum):
    '''群成员身份权限。'''
    Member = "MEMBER"
    Administrator = "ADMINISTRATOR"
    Owner = "OWNER"


class Group(Entity):
    '''群。'''
    id: int
    name: str
    permission: Permission

    def get_avatar_url(self) -> str:
        return f'https://p.qlogo.cn/gh/{self.id}/{self.id}/'


class GroupMember(Entity):
    '''群成员。'''
    id: int
    memberName: str
    permission: Permission
    group: Group

    def __repr__(self):
        return f"<GroupMember id={self.id} group={self.group} permission={self.permission} group={self.group.id}>"

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


class GroupMemberEx(GroupMember):
    '''群成员（包含更多信息）。'''
    specialTitle: str = ''
    joinTimestamp: datetime = 0
    lastSpeakTimestamp: datetime = 0
    muteTimeRemaining: int = 0


class Sender(Entity):
    '''来自其他客户端的用户。'''
    id: int
    platform: str

    def get_avatar_url(self) -> str:
        return f'http://q4.qlogo.cn/g?b=qq&nk={self.id}&s=140'


# class MemberChangeableSetting(BaseModel):
#     name: str
#     announcement: str

#     def modify(self, **kwargs):
#         for i in ("name", "kwargs"):
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         return self

# class GroupSetting(BaseModel):
#     name: str
#     announcement: str
#     confessTalk: bool
#     allowMemberInvite: bool
#     autoApprove: bool
#     anonymousChat: bool

#     def modify(self, **kwargs):
#         for i in ("name", "announcement", "confessTalk", "allowMemberInvite",
#                   "autoApprove", "anonymousChat"):
#             if i in kwargs:
#                 setattr(self, i, kwargs[i])
#         return self

__all__ = [
    'Entity',
    'Friend',
    'Group',
    'GroupMember',
    'GroupMemberEx',
    'Permission',
    'Sender',
]
