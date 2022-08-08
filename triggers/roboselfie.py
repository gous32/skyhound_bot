from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random
from core.timer import GetTimer
import time


class RoboSelfieTrigger(FilteredTrigger):
    def __init__(self, magic, path, filters, captions="", delta=128):
        super().__init__(magic, filters)
        self.Path = path
        if type(captions) != list:
            captions = [captions]
        self.Captions = captions
        self.Delta = delta

    def Process(self, message, chat_state):
        ts = chat_state.get("ts", 0)
        now = int(time.time())
        if now < ts + 3600 * 12:
            return False
        chat_state["ts"] = now

        files = util.FindAllFiles(self.Path)
        file = random.choice(files)
        photo = open(file, 'rb')
        caption = random.choice(self.Captions)
        bot = self.Bot

        def doSend():
            bot.send_photo(message.chat.id, photo, caption=str(caption), parse_mode='html')
            photo.close()

        GetTimer().AddTaskDelta(self.Delta, doSend)

