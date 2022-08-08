from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class LoggerTrigger(FilteredTrigger):
    def __init__(self, magic, filters, verbose=False):
        super().__init__(magic, filters)
        self.Verbose = verbose

    def Process(self, message, chat_state):
        if self.Verbose:
            print(message)
        else:
            print("Got message: ",
                message.message_id,
                message.from_user.username,
                message.chat.id,
                self.Name
            )

