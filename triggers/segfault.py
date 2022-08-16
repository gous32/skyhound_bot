from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class SegfaultTrigger(FilteredTrigger):
    def __init__(self, magic, filters):
        super().__init__(magic, filters)

    def Process(self, message, chat_state):
        self.Bot.send_message(message.chat.id, "Сейчас я упаду")
        raise Exception("Manual exception")

