from core.trigger import FilteredTrigger
import core.filters as flt
import util
import random


class PhotoSenderTrigger(FilteredTrigger):
    def __init__(self, magic, path, filters, captions=""):
        super().__init__(magic, filters)
        self.Path = path
        if type(captions) != list:
            captions = [captions]
        self.Captions = captions

    def Process(self, message, chat_state):
        files = util.FindAllFiles(self.Path)
        file = random.choice(files)
        photo = open(file, 'rb')
        caption = random.choice(self.Captions)
        self.Bot.send_photo(message.chat.id, photo, caption=str(caption), parse_mode='html')
        photo.close()

