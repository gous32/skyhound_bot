# -*- coding: utf-8 -*-

import telebot
from telebot import types
import logging
import traceback
import random
import time




class TriggerWrapper(object):
    def __init__(self, trigger, name, config, state):
        self.Trigger = trigger
        self.Name = name
        self.Config = config
        self.State = state



class Skyhound(object):
    def __init__(self, bot, config, state, logger, silent_time):
        self.Bot = bot
        self.Config = config
        self.State = state
        self.Logger = logger
        self.Triggers = []
        self.LastFailures = {}
        self.SilenceTill = time.time() + silent_time

    def Register(self, triggerCls, name, *args, **kwargs):
        config = self.Config.get(name, {})
        state = self.State.GetTrigger(name)
        magic = {
            "config": config,
            "state": state,
            "name": name,
            "bot": self.Bot,
            "defaultProba": kwargs.get("proba", 1000)
        }

        if "proba" in kwargs:
            del kwargs["proba"]

        trigger = triggerCls(magic, *args, **kwargs)
        self.Triggers.append(
            TriggerWrapper(trigger, name, config, state)
        )


    def Process(self, message):
        if time.time() < self.SilenceTill:
            return
        self.Logger.debug("Got message %s", str(message))

        chat = message.chat.id
        ts = self.State.GetChat(chat).get("ignore_till", 0)
        if time.time() < ts:
            return

        for wrapper in self.Triggers:
            try:
                trigger = wrapper.Trigger
                proba = self.State.GetProba(message.chat.id, trigger.Name, trigger)
                rnd = 1000 * random.random()
                if rnd > proba:
                    continue

                chat_state = self.State.Get(chat, trigger.Name)
                if not trigger.Filter(message, chat_state):
                    continue

                self.Logger.warning("Processing message %s from %s and chat %s to trigger %s",
                    message.message_id,
                    message.from_user.username,
                    message.chat.id,
                    trigger.Name
                )
                if trigger.DoProcess(message, chat_state):
                    self.Logger.warning("Message %s: processing done, stopping", message.message_id)
                    break
                self.Logger.warning("Message %s: processing done, continuing", message.message_id)

            except Exception as e:
                self.Logger.error(traceback.format_exc())
                self.Logger.error(message)

                dobavka = "\n\nПроизошла ошибка, позовите, пожалйста, @gous32."
                errors = [
                    "Моя душа полна исключений\n\n",
                    "Ой! Ничего не произошло! Или всё-таки произошло?",
                    "А можно писать код без багов?",
                ]

                now = time.time()
                self.LastFailures[message.chat.id] = self.LastFailures.get(message.chat.id, 0)
                if self.LastFailures[message.chat.id] + 3600 < now:
                    self.LastFailures[message.chat.id] = now
                    self.Bot.send_message(message.chat.id, random.choice(errors) + dobavka)

        self.State.Save()
