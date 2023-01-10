import time

from work.npc.ai.chatbot.rules.Reactivation import Reactivation
from work.npc.ai.chatbot.rules.Rule import Rule


class PeriodicReactivation(Reactivation):
    def __init__(self, period: float, until: float, start: float = 0.0, lastTry: float = 0.0):
        self.period = period
        self.until = until
        self.start = start
        self.lastTry = lastTry

    def tryActivate(self, rule: Rule):
        now = time.time()
        if now > self.until:
            return

        if self.lastTry // self.period < now // self.period:
            rule.deactivated = False

        self.lastTry = now
