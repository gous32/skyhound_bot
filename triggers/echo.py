from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class EchoTrigger(FilteredTrigger):
    def __init__(self, magic, caption, filters):
        super().__init__(magic, filters)
        self.Caption = caption

    def Process(self, message, chat_state):
        self.Bot.send_message(message.chat.id, self.Caption)

