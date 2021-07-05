import React from "react";

const data = [
  {
    name: "Event",
    children: [
      {
        name: "BotEvent",
        children: [
          { name: "BotOfflineEventActive" },
          { name: "BotOfflineEventDropped" },
          { name: "BotOfflineEventForce" },
          { name: "BotOnlineEvent" },
          { name: "BotReloginEvent" },
        ],
      },
      {
        name: "CommandEvent",
        children: [{ name: "CommandExecutedEvent" }],
      },
      {
        name: "FriendEvent",
        children: [
          { name: "FriendInputStatusChangedEvent" },
          { name: "FriendNickChangedEvent" },
        ],
      },
      { name: "FriendRecallEvent" },
      {
        name: "GroupEvent",
        children: [
          { name: "BotGroupPermissionChangeEvent" },
          { name: "BotJoinGroupEvent" },
          { name: "BotLeaveEventActive" },
          { name: "BotLeaveEventKick" },
          { name: "BotMuteEvent" },
          { name: "BotUnmuteEvent" },
          { name: "GroupAllowAnonymousChatEvent" },
          { name: "GroupAllowConfessTalkEvent" },
          { name: "GroupAllowMemberInviteEvent" },
          { name: "GroupEntranceAnnouncementChangeEvent" },
          { name: "GroupMuteAllEvent" },
          { name: "GroupNameChangeEvent" },
          { name: "GroupRecallEvent" },
          { name: "MemberCardChangeEvent" },
          { name: "MemberHonorChangeEvent" },
          { name: "MemberJoinEvent" },
          { name: "MemberLeaveEventKick" },
          { name: "MemberLeaveEventQuit" },
          { name: "MemberMuteEvent" },
          { name: "MemberPermissionChangeEvent" },
          { name: "MemberSpecialTitleChangeEvent" },
          { name: "MemberUnmuteEvent" },
        ],
      },
      {
        name: "MessageEvent",
        children: [
          { name: "FriendMessage" },
          { name: "GroupMessage" },
          { name: "OtherClientMessage" },
          { name: "StrangerMessage" },
          { name: "TempMessage" },
        ],
      },
      {
        name: "RequestEvent",
        children: [
          { name: "BotInvitedJoinGroupRequestEvent" },
          { name: "MemberJoinRequestEvent" },
          { name: "NewFriendRequestEvent" },
        ],
      },
    ],
  },
];

export default data;
