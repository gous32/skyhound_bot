import json
from os import listdir
from os.path import isfile, join
import sys


def ReadFile(path):
    if not isfile(path):
        return ""
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data


def WriteFile(path, data):
    f = open(path, 'w')
    data = f.write(data)
    f.close()
    return data


def GetOrCreate(obj, key, placeholder):
    if key not in obj:
        obj[key] = placeholder
    return obj[key]


class StateHolder(object):
    def __init__(self, path):
        self.Path = path
        self.Data = ""
        self.State = {}
        self.Load()


    def Load(self):
        if not self.Path:
            return

        self.Data = ReadFile(self.Path)
        if len(self.Data) == 0:
            self.Data = "{}"
        self.State = json.loads(self.Data)
        GetOrCreate(self.State, "chats", {})
        GetOrCreate(self.State, "chat_only", {})
        GetOrCreate(self.State, "triggers", {})
        GetOrCreate(self.State, "admins", {})
        GetOrCreate(self.State, "chat_admins", {})


    def Save(self):
        if not self.Path:
            return

        data = json.dumps(self.State)
        if data == self.Data:
            return

        self.Data = data
        WriteFile(self.Path, data)


    def Get(self, chat, trigger):
        chatState = GetOrCreate(self.State["chats"], str(chat), {})
        return GetOrCreate(chatState, str(trigger), {})


    def GetTrigger(self, trigger):
        return GetOrCreate(self.State["triggers"], str(trigger), {})


    def GetChat(self, chat):
        return GetOrCreate(self.State["chat_only"], str(chat), {})


    def AddAdmin(self, id, name):
        self.State["admins"][name] = id

    def GetAdmins(self):
        return self.State["admins"]

    def AddChatAdmin(self, chat, id, name):
        self.GetChatAdmins(chat)[name] = id

    def GetChatAdmins(self, chat):
        return GetOrCreate(self.State["chat_admins"], str(chat), {})

    def IsSuperAdmin(self, message):
        return message.from_user.id in self.GetAdmins().values()

    def IsChatBotAdmin(self, message):
        return message.from_user.id in self.GetChatAdmins(message.chat.id).values()

    def IsChatAdmin(self, message, bot):
        try:
            admins = bot.get_chat_administrators(message.chat.id)
            return message.from_user.id in [a.user.id for a in admins]
        except Exception:
            return False

    def IsAdmin(self, message, bot):
        return self.IsSuperAdmin(message) or self.IsChatBotAdmin(message) or self.IsChatAdmin(message, bot)


    def GetProba(self, chat, name, trigger):
        proba = self.GetChat(chat).get("probas", {}).get(name, None)
        if proba is None:
            return trigger.GetProba()
        return proba

    def SetProba(self, chat, name, proba):
        probas = GetOrCreate(self.GetChat(chat), "probas", {})
        probas[name] = proba




GlobalState = None

def GetGlobalState():
    global GlobalState
    return GlobalState

def SetGlobalState(state):
    global GlobalState
    GlobalState = state

def IsAdminMessage(message):
    id = message.from_user.id
    chatId = message.chat.id
    return id in GlobalState.GetAdmins().values() or id in GlobalState.GetChatAdmins(chatId).values()
