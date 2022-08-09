# -*- coding: utf-8 -*-

import argparse

import telebot
from telebot import types
import json
import logging
import random

from util import GetToken, ReadFileSafe
from core.state import StateHolder, SetGlobalState
from core.wrapper import Skyhound
from core.timer import SetTimer, GetTimer, Timer
import core.filters as flt

from triggers.photo_sender import PhotoSenderTrigger
from triggers.logger import LoggerTrigger
from triggers.admin import GlobalAdminTrigger
from triggers.echo import EchoTrigger
from triggers.bard import BardTrigger
from triggers.roboselfie import RoboSelfieTrigger
from triggers.stats import StatsTrigger
from triggers.news import NewsTrigger
from triggers.zaryadka import ZaryadkaTrigger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="./config", help="Config file path")
    parser.add_argument("-s", "--state", type=str, default="./state.json", help="State file path")

    parser.add_argument("--token", type=str, help="Telegram token")
    parser.add_argument("--token-path", type=str, help="Telegram token file path")
    parser.add_argument("--token-env", type=str, help="Telegram token environment variable")

    parser.add_argument('-v', "--verbose", action='store_true', help="Verbose")
    parser.add_argument("--super-verbose", action='store_true', help="Super verbose")

    _args, _ = parser.parse_known_args()
    return _args


SkyhoundInstance = None


def CreateTriggers(args):
    # Логгer
    # SkyhoundInstance.Register(LoggerTrigger, "logger", lambda *args, **kwargs: True, verbose=args.super_verbose)

    # Админка
    SkyhoundInstance.Register(GlobalAdminTrigger, "admins", SkyhoundInstance)

    # Статы
    SkyhoundInstance.Register(StatsTrigger, "stats")

    # Берт
    SkyhoundInstance.Register(
        PhotoSenderTrigger,
        "bert",
        '/etc/skytg/bert',
        flt.AllOf([
            flt.ContainsAny("хорош"),
            flt.ContainsAny("мальч"),
        ]),
        captions='Вот хороший мальчик!'
    )

    # Берт просит кушать
    SkyhoundInstance.Register(
        PhotoSenderTrigger,
        "bert_eda",
        '/etc/skytg/eda',
        flt.ContainsAny(["завтрак+", "обед+", "ужин+", "кушат"]),
        captions=[
            'А вы не поделитесь?',
            'А у вас осталось?',
            'А какая из этих порций мне?',
            'Эх, давно я не кушал(',
            'А вы меня сегодня ещё не кормили!',
            'Кто сказал "кушать?"',
            'Если долго смотреть на еду, еда начнёт попадать в тебя',
        ],
        proba=200
    )

    # Булка
    SkyhoundInstance.Register(PhotoSenderTrigger, "bulka", '/etc/skytg/bulka',
        flt.AnyOf([
            flt.ContainsAll(["сладк", 'булк']),
            flt.ContainsAll(["сладк", "булочк"]),
            flt.ContainsAny(["молыш", "млемик"]),
        ]),
        captions=[
            'Вот сладкая булочка!',
            'А кто тут такая кошка-картошка?',
            'Просто для иллюстрации',
            'Плюшка московская, 1 шт.',
            'Молыш',
        ]
    )

    # Альпака
    SkyhoundInstance.Register(PhotoSenderTrigger, "alpaca", '/etc/skytg/alpaca', flt.ContainsAny(['альпак']))

    # Робоселфи
    SkyhoundInstance.Register(RoboSelfieTrigger, "roboselfie", '/etc/skytg/robotselfie', flt.ContainsAny(['селфитайм']), captions="Роботный селфитайм!")

    # Новости
    SkyhoundInstance.Register(NewsTrigger, "news", flt.AnyOf([
        flt.ContainsAll(['добби', 'новост']),
        flt.AllOf([
            flt.ContainsAny(['новост']),
            flt.Random(0.1)
        ])
    ]))

    # # Зарядка+
    # SkyhoundInstance.Register(
    #     EchoTrigger,
    #     "zaryadka",
    #     [
    #         'А мог(ла) бы вместо этого вкусно покушать или сладко поспать!',
    #         'Так держать!',
    #     ],
    #     flt.AllOf([
    #         flt.ContainsAny(['зарядка+'])
    #     ]),
    #     proba=100
    # )
    # Зарядка+
    SkyhoundInstance.Register(
        ZaryadkaTrigger,
        "zaryadka"
    )

    # Вопрос+
    SkyhoundInstance.Register(
        EchoTrigger,
        "the_question",
        ['Ты!', 'Я!'],
        flt.ContainsAll(['кто', "пидор"])
    )

    # Бард
    SkyhoundInstance.Register(BardTrigger, "bard", '/etc/skytg/bard.json', '/etc/skytg/no_power.jpg')



def main():
    global SkyhoundInstance

    args = parse_args()
    logger = logging.getLogger('skyhound')
    if not args.verbose:
        logger.setLevel(logging.ERROR)

    if args.super_verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Info log enabled")
    logger.debug("Debug log enabled")
    logger.warning("Warning log enabled")
    logger.warning("Error log enabled")

    SetTimer(Timer())
    GetTimer().Start()

    bot=telebot.TeleBot(GetToken(args))

    # bot.send_message(id, "msg")
    # bot.send_message(-1001653127007, "Я не понимаю человеческую речь, но мне нравится твой голос. И карты красивые")

    config = json.loads(ReadFileSafe(args.config, "{}"))
    state = StateHolder(args.state)
    SetGlobalState(state)

    SkyhoundInstance = Skyhound(bot, config, state, logger)
    CreateTriggers(args)

    @bot.message_handler(content_types=['photo', 'text'])
    def process_message(message):
        SkyhoundInstance.Process(message)

    bot.polling(none_stop=True)

    GetTimer().Stop()




if __name__ == "__main__":
    main()





