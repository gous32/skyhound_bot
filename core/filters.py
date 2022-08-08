# -*- coding: utf-8 -*-

import telebot
from telebot import types
import random

'''
    Пример фильтра:
        filters.AnyOf(
            filters.ContentType("image", "gif"),
            filters.AllOf(
                filters.StartsWith("понтелеймон,"),
                filters.ContainsAny("кофе", "чаю")
            ),
            filters.Command("settings", "configure")
        )


    (На примере ContainsAny([a, b, c])
        Функция фильтра (ContainsAny) должна принимать параметры фильтра ([a, b, c]) и возвращать функцию,
        которая должна принимать сообщение и параметры, и возвращать True (OK) или False (зафильтровано)

    Посмотрите один любой фильтр, там всё просто
'''

def Always():
    return lambda *args, **kwargs: True


def AnyOf(filters):
    def do(message, args):
        for f in filters:
            if f(message, args):
                return True
        return False

    return do


def AllOf(filters):
    def do(message, args):
        for f in filters:
            if not f(message, args):
                return False
        return True

    return do


def Not(filter):
    def do(message, args):
        return not filter(message, args)

    return do


def ContentType(types):
    if type(types) != list:
        types = [types]
    def do(message, args):
        return message.content_type in types

    return do


def ContainsAny(items):
    if type(items) != list:
        items = [items]
    ci_items = [str(i).lower() for i in items]
    def do(message, args):
        if not message.text:
            return False
        text = message.text.lower()
        for item in ci_items:
            if item in text:
                return True
        return False

    return do


def ContainsAll(items):
    if type(items) != list:
        items = [items]
    ci_items = [str(i).lower() for i in items]
    def do(message, args):
        if not message.text:
            return False
        text = message.text.lower()
        for item in ci_items:
            if not item in text:
                return False
        return True

    return do


def StartsWith(items):
    if type(items) != list:
        items = [items]
    ci_items = [str(i).lower() for i in items]
    def do(message, args):
        if not message.text:
            return False
        text = message.text.lower()
        for item in ci_items:
            if text.startswith(item):
                return True
        return False

    return do


def Command(items):
    if type(items) != list:
        items = [items]
    items = ['/' + i for i in items]
    return StartsWith(['/' + i for i in items])


def Random(p):
    def do(message, args):
        return random.random() < p

    return do

