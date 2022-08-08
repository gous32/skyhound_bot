# -*- coding: utf-8 -*-

from core.trigger import MultiTrigger
from core.state import IsAdminMessage
import core.filters as flt
import util
import random
import json



class BardTrigger(MultiTrigger):
    def __init__(self, magic, path, pic403):
        super().__init__(magic)

        self.Texts = json.loads(util.ReadFileSafe(path, "[]"))
        self.Pic403 = pic403

        self.AddScenario(flt.ContainsAll(["Добби", "песни", "на"]), self.SetProba)
        self.AddScenario(flt.ContainsAll(["Добби", "пой"]), self.ForceScream)
        self.AddScenario(flt.Always(), self.Scream)

    def SetProba(self, message, chat_state):
        if not IsAdminMessage(message):
            if not self.Pic403:
                return
            photo = open(self.Pic403, 'rb')
            self.Bot.send_photo(message.chat.id, photo, caption="У тебя здесь нет власти!", parse_mode='html')
            photo.close()
            return

        value = int(message.text.split(' ')[-1])
        chat_state["proba"] = value
        self.Bot.send_message(message.chat.id, "Поставил песни и пляски на " + str(value))


    def Scream(self, message, chat_state):
        if 1000 * random.random() > chat_state.get("proba", 10):
            return False

        return self.ForceScream(message, chat_state)

    def ForceScream(self, message, chat_state):
        if len(self.Texts) == 0:
            return False

        items = random.choice(self.Texts)

        if type(items) == str:
            items = [items]

        for item in items:
            item = str(item)
            if not item.strip():
                continue
            self.Bot.send_message(message.chat.id, item)

