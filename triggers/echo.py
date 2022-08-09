from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class EchoTrigger(FilteredTrigger):
    def __init__(self, magic, captions, filters):
        super().__init__(magic, filters)
        if type(captions) != list:
            captions = [captions]
        self.Captions = captions

    def Process(self, message, chat_state):
        self.Bot.send_message(message.chat.id, random.choice(self.Captions))

