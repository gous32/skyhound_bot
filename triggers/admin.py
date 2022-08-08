# -*- coding: utf-8 -*-

from core.trigger import MultiTrigger
from core.state import GetGlobalState
import core.filters as flt
import util
import random
import time



helpText = '''
Я – Добби, и со мной можно делать всякое. Иногда просто так.

Вы можете задать мне некоторые вопросы в свободной форме. Например:
    * Кто хороший мальчик?
    * Кто сладкая булочка?
    * Поговорить про альпак

Есть более формализованные команды, тоже в свободной форме:
    * Добби, новости – пришлёт вам самую важную новость.
    * Добби, пой – заставит меня спеть

Если в сообщении написано "Добби, игнорируй", я его проигнорирую.

Есть команды для админов:
    * Добби, заткнись – затыкает меня на час
    * Добби, песни на X – регулирует мою болтливость от 0 до 1000
    * Добби, это твой повелитетель/твоя повелительница – назначает админа бота в местном чате
    * судо лист, /sudolist – показывает список триггеров
    * судо проба %trigger% %proba% – задаёт вероятность срабатывания триггера в чате от 0 до 100

Есть три разных вида админов:
    * Глобальный админ, который сказал Добби волшебную фразу
    * Адмиин чата в терминах телеграма
    * Повелитель Добби в этом чате. Назначается предыдущими двумя, работает в рамках одного чата

С предложениями и критикой пишите gous32@
'''


class GlobalAdminTrigger(MultiTrigger):
    def __init__(self, magic, app):
        super().__init__(magic)

        self.App = app

        self.AddScenario(flt.StartsWith(["/describe"]), self.Describe)
        self.AddScenario(flt.ContainsAll(["Добби", "игнорируй"]), self.IgnoreMessage)
        self.AddScenario(flt.StartsWith(["Добби, заткнись", "/shut_up"]), self.ShutUp)

        self.AddScenario(flt.StartsWith(["судо лист", "sudo list", "/sudolist"]), self.SudoList)
        self.AddScenario(flt.StartsWith(["судо проба", "sudo proba"]), self.SudoProba)

        self.AddScenario(flt.ContainsAny("Добби, послушай меня сюда"), self.ProcessSuperAdmin)
        self.AddScenario(
            flt.ContainsAny([
                "Добби, это твой повелитель",
                "Добби, это твоя повелительница"
            ]),
            self.AddChatAdmin
        )

    def CheckAdmin(self, message):
        if GetGlobalState().IsAdmin(message, self.Bot):
            return True

        self.Bot.send_message(message.chat.id, "403. Недостаточно прав.")


    def CheckAdminOrSuperAdmin(self, message):
        if GetGlobalState().IsSuperAdmin(message) or GetGlobalState().IsChatAdmin(message, self.Bot):
            return True

        self.Bot.send_message(message.chat.id, "403. Недостаточно прав.")


    def Describe(self, message, chat_state):
        self.Bot.send_message(message.chat.id, helpText)


    def IgnoreMessage(self, message, chat_state):
        print("Ignoring message", message.chat.id)
        pass


    def ShutUp(self, message, chat_state):
        if not self.CheckAdmin(message):
            return

        ts = int(time.time()) + 3600
        GetGlobalState().GetChat(message.chat.id)["ignore_till"] = ts
        print("Ignoring chat", message.chat.id)
        self.Bot.send_message(message.chat.id, "Умолкаю")


    def ProcessSuperAdmin(self, message, chat_state):
        state = GetGlobalState()
        name = message.from_user.username
        id = message.from_user.id

        if id in state.GetAdmins().values():
            self.Bot.send_message(message.chat.id, "Вы уже мой хозяин, господин!")
            return

        for n, i in state.GetAdmins():
            self.Bot.send_message(i, n + "! У меня появился новый хозяин: " + name)

        state.AddAdmin(id, name)
        self.Bot.send_message(message.chat.id, "Да, мой хозяин!")


    def AddChatAdmin(self, message, chat_state):
        if not self.CheckAdminOrSuperAdmin(message):
            return

        state = GetGlobalState()
        fromId = message.from_user.id

        if not message.reply_to_message:
            self.Bot.send_message(message.chat.id, "Нулл поинтер эксепшн, так сказать")
            return

        name = message.reply_to_message.from_user.username
        id = message.reply_to_message.from_user.id

        if id in state.GetChatAdmins(message.chat.id).values():
            self.Bot.send_message(message.chat.id, "Он(а) уже владеет моим сердцем, хозяин!")
            return

        state.AddChatAdmin(message.chat.id, id, name)
        self.Bot.send_message(message.chat.id, "Буду слушаться, хозяин!")


    def SudoList(self, message, chat_state):
        if not self.CheckAdmin(message):
            return

        result = "Список триггеров и вероятность срабатывания:\n"
        triggerTexts = []

        GetGlobalState().IsChatAdmin(message, self.Bot)

        for wrapper in self.App.Triggers:
            proba = GetGlobalState().GetProba(message.chat.id, wrapper.Name, wrapper.Trigger)
            triggerTexts.append("    * " + wrapper.Name + ": " + str(proba))

        result = result + '\n'.join(triggerTexts) + '\n\nЧтобы изменить вероятность, напишите:\n   sudo proba %trigger% %proba%'
        self.Bot.send_message(message.chat.id, result)


    def SudoProba(self, message, chat_state):
        if not self.CheckAdmin(message):
            return

        try:
            items = message.text.split(" ")
            name = items[-2]
            proba = int(items[-1])
            if name in ["admins", "stats"]:
                self.Bot.send_message(message.chat.id, "Вероятность этого триггера менять нельзя")
                return
            GetGlobalState().SetProba(message.chat.id, name, proba)
            self.Bot.send_message(message.chat.id, "Установил вероятность " + str(proba) + " из 1000 для триггера " + name)
        except Exception as e:
            self.Bot.send_message(message.chat.id, "Что-то пошло не так")
            print(e)
