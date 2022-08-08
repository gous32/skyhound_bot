from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class NewsTrigger(FilteredTrigger):
    def __init__(self, magic, filters):
        super().__init__(magic, filters)

    def Process(self, message, chat_state):
        try:
            self.Bot.forward_message(chat_id=message.chat.id, from_chat_id=-1001563800800, message_id=int(random.random() * 250 + 250))
        except Exception as e:
            self.Bot.send_message(message.chat.id, "Извините, новостей пока нет")
            print(e)

