from core.trigger import MultiTrigger
from core.state import GetGlobalState
import core.filters as flt
import util
import random
import time


class ZaryadkaTrigger(MultiTrigger):
    def __init__(self, magic):
        super().__init__(magic)
        self.AddScenario(flt.ContainsAny(["зарядка+"]), self.OnZaryadka)
        self.AddScenario(flt.ContainsAny(["фишбургер+"]), self.OnFishburger)
        self.AddScenario(flt.ContainsAny(["кофе+"]), self.OnCoffee)

        self.State["zaryad"] = self.State.get("zaryad", {})
        self.State["fish"] = self.State.get("fish", {})
        self.State["coffee"] = self.State.get("coffee", {})


    def OnZaryadka(self, message, chat_state):
        self.SayAboutIt(message, self.State['zaryad'], "Это ваша первая зарядка", "С вашей последней зарядки")

    def OnFishburger(self, message, chat_state):
        self.SayAboutIt(message, self.State['fish'], "Это ваш первый фишбургер", "С вашего последнего фишбургера")

    def OnCoffee(self, message, chat_state):
        if message.chat.id != -1001653127007:
            return False
        self.SayAboutIt(message, self.State['coffee'], "Слышь ты, это твой первый кофе", "Слышь ты, с последней чашки кофе")

    def SayAboutIt(self, message, state, itIsFirst, fromYourLast):
        id = str(message.from_user.id)
        ts = state.get(id, None)
        now = time.time()
        state[id] = now

        if ts is None:
            self.Bot.send_message(message.chat.id, itIsFirst + " на моей памяти. Молодец!")
            return

        delta = int(now - ts)
        secs = int(delta % 60)
        mins = int((delta / 60) % 60)
        hours = int((delta / 3600) % 24)
        hours = int((delta / 3600) % 24)
        days = int((delta / 86400) % 365)
        years = int(delta / 86400 / 365)
        passed = ', '.join([
            str(years) + " лет",
            str(days) + " дней",
            str(hours) + " часов",
            str(mins) + " минут и " +  str(secs) + " секунд"
        ])

        self.Bot.send_message(
            message.chat.id,
            fromYourLast + " прошло " + passed + "."
        )

