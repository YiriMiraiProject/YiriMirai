# -*- coding: utf-8 -*-
"""
此模块提供 model 层封装。

model 层架构在 bus 和 adapters 之上，将 mirai-api-http 传回的原始数据解析为 Python 对象，
并支持用 Python 对象作为参数调用 API。

model 层使用 pydantic 进行数据解析。
"""
from YiriMirai.models.bus import ModelEventBus
from YiriMirai.models.entities import (
    Entity, Friend, Group, GroupMember, Permission, Sender
)
from YiriMirai.models.events import (
    BotEvent, BotGroupPermissionChangeEvent, BotInvitedJoinGroupRequestEvent,
    BotJoinGroupEvent, BotLeaveEventActive, BotLeaveEventKick, BotMuteEvent,
    BotOfflineEventActive, BotOfflineEventDropped, BotOfflineEventForce,
    BotOnlineEvent, BotReloginEvent, BotUnmuteEvent, CommandEvent,
    CommandExecutedEvent, Event, FriendEvent, FriendInputStatusChangedEvent,
    FriendMessage, FriendNickChangedEvent, FriendRecallEvent,
    GroupAllowAnonymousChatEvent, GroupAllowConfessTalkEvent,
    GroupAllowMemberInviteEvent, GroupEntranceAnnouncementChangeEvent,
    GroupEvent, GroupMember, GroupMessage, GroupMuteAllEvent,
    GroupNameChangeEvent, GroupRecallEvent, MemberCardChangeEvent,
    MemberHonorChangeEvent, MemberJoinEvent, MemberJoinRequestEvent,
    MemberLeaveEventKick, MemberLeaveEventQuit, MemberMuteEvent,
    MemberPermissionChangeEvent, MemberSpecialTitleChangeEvent,
    MemberUnmuteEvent, MessageEvent, NewFriendRequestEvent, OtherClientMessage,
    RequestEvent, StrangerMessage, TempMessage
)
from YiriMirai.models.message import (
    App, At, AtAll, Dice, Face, File, FlashImage, Forward, ForwardMessageNode,
    Image, Json, MessageChain, MessageComponent, MusicShare, Plain, Poke,
    Quote, Source, Unknown, Voice, Xml, deserialize, serialize
)

__all__ = [
    'Entity',
    'Friend',
    'Group',
    'GroupMember',
    'Permission',
    'Sender',
    'BotEvent',
    'BotGroupPermissionChangeEvent',
    'BotInvitedJoinGroupRequestEvent',
    'BotJoinGroupEvent',
    'BotLeaveEventActive',
    'BotLeaveEventKick',
    'BotMuteEvent',
    'BotOfflineEventActive',
    'BotOfflineEventDropped',
    'BotOfflineEventForce',
    'BotOnlineEvent',
    'BotReloginEvent',
    'BotUnmuteEvent',
    'CommandEvent',
    'CommandExecutedEvent',
    'Event',
    'FriendEvent',
    'FriendInputStatusChangedEvent',
    'FriendMessage',
    'FriendNickChangedEvent',
    'FriendRecallEvent',
    'GroupAllowAnonymousChatEvent',
    'GroupAllowConfessTalkEvent',
    'GroupAllowMemberInviteEvent',
    'GroupEntranceAnnouncementChangeEvent',
    'GroupEvent',
    'GroupMessage',
    'GroupMuteAllEvent',
    'GroupNameChangeEvent',
    'GroupRecallEvent',
    'MemberCardChangeEvent',
    'MemberHonorChangeEvent',
    'MemberJoinEvent',
    'MemberJoinRequestEvent',
    'MemberLeaveEventKick',
    'MemberLeaveEventQuit',
    'MemberMuteEvent',
    'MemberPermissionChangeEvent',
    'MemberSpecialTitleChangeEvent',
    'MemberUnmuteEvent',
    'MessageEvent',
    'NewFriendRequestEvent',
    'OtherClientMessage',
    'RequestEvent',
    'StrangerMessage',
    'TempMessage',
    'App',
    'At',
    'AtAll',
    'Dice',
    'Face',
    'File',
    'FlashImage',
    'Forward',
    'ForwardMessageNode',
    'Image',
    'Json',
    'MessageChain',
    'MessageComponent',
    'MusicShare',
    'Plain',
    'Poke',
    'Quote',
    'Source',
    'Unknown',
    'Voice',
    'Xml',
    'serialize',
    'deserialize',
    'ModelEventBus',
]
