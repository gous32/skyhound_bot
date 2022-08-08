from core.trigger import BaseTrigger
import core.filters as flt
import util
import random


dictionary = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'jo',
    'ж': 'j',
    'з': 'z',
    'и': 'i',
    'й': 'j',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'h',
    'ц': 'c',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '_',
    'ы': 'i',
    'ь': '_',
    'э': 'e',
    'ю': 'jy',
    'я': 'ja',
}

def transform(line):
    if not line:
        return ''
    result = ''
    for c in line:
        result = result + dictionary.get(c.lower(), c)
    return result


class StatsTrigger(BaseTrigger):
    def __init__(self, magic):
        super().__init__(magic)
        self.State["users"] = self.State.get("users", {})
        self.State["chats"] = self.State.get("chats", {})


    def Process(self, message, chat_state):
        self.State["users"][message.from_user.username] = {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'id': message.from_user.id,
            'transformed_first_name': transform(message.from_user.first_name),
            'transformed_last_name': transform(message.from_user.last_name),
        }

        self.State["chats"][str(message.chat.id)] = {
            'username': message.chat.username,
            'first_name': message.chat.first_name,
            'last_name': message.chat.last_name,
            'id': message.chat.id,
            'title': message.chat.title,
            'transformed_title': transform(message.chat.title),
            'transformed_first_name': transform(message.chat.first_name),
            'transformed_last_name': transform(message.chat.last_name),
        }

        return False


