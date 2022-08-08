# -*- coding: utf-8 -*-

import telebot
from telebot import types


'''
    ПРО ТРИГГЕРЫ

    Триггер - это какой-то обработчик сообщений из чата или диалога.

    У бота может быть много триггеров. И много экземпляров одного класса триггера

    Триггеры подключаются в main.py. Порядок подключения важен: при обработке сообщения
    триггер может сказать, что обработка сообщения закончена, и в нижестоящие триггеры
    сообщение не придёт. Для этого нужно из метода Process...() вернуть True.

    У триггера есть два стейта: стейт триггера и стейт чата
        * Стейт триггера - это какой-то json, доступный с момента создания триггера
        * Стейт чата - это какой-то другой json, который приходит в метод Process...().
            Для каждой пары {триггер, чат} используется свой стейт, то есть нельзя прочитать
            стейт чужого триггера или чужого чата.
    Оба стейта автоматически сохраняются после каждого сообщения

    Вызов триггера состоит из двух стадий (конкретные имена методов зависят от базового класса):
        * Filter - понимаем, нужно ли вообще этому триггеру обрабатывать это сообщение
        * Process... - собственно обработка сообщения. Вызывается, если фильтр был успешен
            Если Process... возвращает True, то нижележащие триггеры не активируются

    В триггере всегда доступны такаие поля:
        self.Config - json-конфиг триггера (config["triggers"][name], где config - конфиг приложения)
        self.State - стейт триггера. Не перезаписывайте его! Менять можно.
        self.Name - имя триггера
        self.Bot - ссылка на бота (для отправки сообщений и т.п.)
            * self.Bot.send_message(message.chat.id, "text") - отправит сообщение в чат

    В методы приходят аргументы chat_state и message:
        * chat_state - это стейт чата (см. выше)
        * message - это объект сообщения. Подробности: https://pypi.org/project/pyTelegramBotAPI/ и https://core.telegram.org/bots/api#message
            * message.text - текст сообщения
            * message.chat.id - id чата, из которого отправлено сообщение
            * message.from_user

    Базовые типы триггеров:
        * BaseTrigger - совсем базовый, можно переопределять всё
        * FilteredTrigger - один набор фильтров, одно действие в ответ на фильтр
        * MultiTrigger - можно задать несколько пар {фильтр - действие}
'''


'''
    Базовый класс триггера

    Принимает все сообщения подряд, ничего не делает. Важные методы:
        Filter(message, chat_state) - фильтрует сообщения.
            По дефолту ничего не фильтруется
        Process(message, chat_state) - обрабатывает сообщения.
            По дефолту ничего не делает и передаёт сообщение нижележащим триггерам
'''
class BaseTrigger(object):
    def __init__(self, magic):
        self.Config = magic["config"]
        self.State = magic["state"]
        self.Name = magic["name"]
        self.Bot = magic["bot"]
        self.DefaultProba = magic["defaultProba"]


    def Filter(self, message, chat_state):
        return True

    def Process(self, message, chat_state):
        return False

    # специальный метод, чтобы базовые классы его переопределяли
    def DoProcess(self, message, chat_state):
        return self.Process(message, chat_state)

    def GetProba(self):
        return self.DefaultProba


'''
    Триггер с произвольным фильтром

    Если сообщение попадает под фильтр, вызывается метод Process, и на этом обработка завершается,
    то есть в следующие триггеры сообщение не попадёт
        Исключение - если Process явно вернёт False

    Фильтр задаётся через модуль filters, см. пример ниже и комментарий в модуле.
    Фильтр можно задать в конструкторе или через метод SetFilter

    Удобные фильтры (больше есть в filters.py):
        * AnyOf([a, b, c]) - ИЛИ. Принимает в себя любое количество других фильтров.
            ОК, если оно проходит хотя бы через один из них
        * AllOf([a, b, c]) - И. Принимает в себя любое количество других фильтров.
            ОК, если оно проходит все фильтры
        * ContentType([a, b, c]) - ОК, если сообщение одного из этих типов. Некоторые допустимые типы:
            "text", "photo", "sticker"
        * ContainsAny(["a", "b", "c"]) - ОК, если в тексте есть хотя бы одна из подстрок
        * StartsWith(["a", "b", "c"]) - ОК, если текст начинается с одной из этих строк
        * Command(["a", "b"]) - ОК, если сообщение - это одна из команд /a или /b
        * Random(p) - OK с вероятностью p. 0 <= p <= 1

    Пример фильтра:
        filters.AnyOf(
            filters.ContentType("image", "gif"),
            filters.AllOf(
                filters.StartsWith("понтелеймон,"),
                filters.ContainsAny("кофе", "чаю")
            ),
            filters.Command("settings", "configure")
        )
'''
class FilteredTrigger(BaseTrigger):
    def __init__(self, magic, filter=lambda x, y: True):
        super().__init__(magic)
        self.FilterSet = filter

    def SetFilter(self, filter):
        self.FilterSet = filter

    def Filter(self, message, chat_state):
        return self.FilterSet(message, args={
            "chat_state": chat_state
        })

    def DoProcess(self, message, chat_state):
        result = self.Process(message, chat_state)
        if result is False:
            return False
        return True



'''
    Триггер, в котором можно задать разные обработчики на разные фильтры сообщений.
    Фильтры перебираются в порядке добавления. Если фильтр сработал, а обработчик не вернул явно False, перебор останавливается.
    Добавить фильтр можно так: self.AddScenario(filter, lambda). В качестве лямбды лучше всего использовать свой метод.

    Пример:
        class SomeTrigger(MultiTrigger):
            def __init__(self, magic):
                super().__init__(magic)
                self.AddScenario(flt.ContainsAny("привет"), self.SayHello)

            def SayHello(self, message, chat_state):
                self.Bot.send_message(message.chat.id, "И тебе привет")

'''
class MultiTrigger(BaseTrigger):
    def __init__(self, magic):
        super().__init__(magic)
        self.FilterSet = []

    def AddScenario(self, filter, scenario):
        self.FilterSet.append([filter, scenario])

    def Process(self, message, chat_state):
        for filter, scenario in self.FilterSet:
            ok = filter(message, args={
                "chat_state": chat_state
            })
            if ok:
                result = scenario(message, chat_state)
                if result is False:
                    continue
                return True
        return False
